import os
import json
import asyncio
import time
import aiohttp
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class FailureType(Enum):
    NETWORK = "network"
    SEMANTIC = "semantic"
    RATE_LIMIT = "rate_limit"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

    def record_success(self):
        self.failures = 0

    def is_open(self) -> bool:
        if self.failures >= self.failure_threshold:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                return False # Recovery attempt
            return True
        return False

class GeminiAgent:
    """
    Async-first agent supporting Multi-Provider (Groq + Google Gemini).
    """
    def __init__(self, name: str, role: str, model_chain: List[str] = None):
        self.name = name
        self.role = role
        self.model_chain = model_chain or [
            "gemini-1.5-pro", # Primary
            "llama-3.3-70b-versatile", # Backup
            "gemini-1.5-flash" # Fallback
        ]
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GOOGLE_API_KEY") # Check env var name
        
        self.circuit_breakers = {model: CircuitBreaker() for model in self.model_chain}
        self.timeouts = {"total": 60}

    async def query(self, prompt: str, system_context: Optional[str] = None, constraints: List[Any] = None) -> Dict[str, Any]:
        """
        Queries the agent using the appropriate provider for the current model in the chain.
        """
        full_system_role = f"You are {self.name}. {self.role}\n"
        full_system_role += 'IMPORTANT: Respond in valid JSON: {"verdict": "PASS"|"WARN"|"FAIL", "confidence": 0.0-1.0, "evidence": [], "reasoning": "..."}'

        if constraints:
            full_system_role += "\n\n### CONSTRAINTS\n" + "\n".join([f"- {c.description}" for c in constraints])

        if system_context:
            full_system_role += f"\nContext: {system_context}"

        errors = []

        # NOTE: The "Model Chain" here is the *Agent's* internal resilience.
        # The *Council* might have already routed specific instructions (via context).
        # We check the context for [SYSTEM: Use Model X] overrides from the Router.
        active_chain = self.model_chain
        if system_context and "[SYSTEM: Use Model" in system_context:
            # Extract routed model if present (Simple parsing)
            import re
            match = re.search(r"Use Model ([\w\.-]+)", system_context)
            if match:
                active_chain = [match.group(1)] # Force routed model

        for model in active_chain:
            cb = self.circuit_breakers.get(model, CircuitBreaker())
            if cb.is_open(): continue

            try:
                if "gemini" in model.lower():
                    raw_response = await self._call_gemini(model, full_system_role, prompt)
                else:
                    raw_response = await self._call_groq(model, full_system_role, prompt)
                
                parsed = self._validate_structure(raw_response)
                if parsed:
                    cb.record_success()
                    return parsed
                else:
                    cb.record_failure()
                    errors.append(f"{model}: Invalid JSON")

            except Exception as e:
                cb.record_failure()
                errors.append(f"{model}: {str(e)}")

        return {"verdict": "ERROR", "confidence": 0.0, "reasoning": f"All providers failed: {errors}"}

    async def _call_groq(self, model: str, system_role: str, user_prompt: str) -> str:
        if not self.groq_key: raise ValueError("GROQ_API_KEY missing")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.groq_key}"}
        data = {
            "model": model,
            "messages": [{"role": "system", "content": system_role}, {"role": "user", "content": user_prompt}],
            "response_format": {"type": "json_object"}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status != 200: raise Exception(f"Groq {resp.status}: {await resp.text()}")
                return (await resp.json())['choices'][0]['message']['content']

    async def _call_gemini(self, model: str, system_role: str, user_prompt: str) -> str:
        if not self.gemini_key: raise ValueError("GOOGLE_API_KEY missing")
        # Google AI Studio REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
        
        # Gemini doesn't support 'system' role in the same way for all models, 
        # but 1.5 Pro/Flash supports 'system_instruction'.
        data = {
            "system_instruction": {"parts": {"text": system_role}},
            "contents": {"parts": {"text": user_prompt}},
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                if resp.status != 200: raise Exception(f"Gemini {resp.status}: {await resp.text()}")
                result = await resp.json()
                try:
                    return result['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    raise Exception(f"Gemini Malformed Response: {result}")

    def _validate_structure(self, raw: str) -> Optional[Dict]:
        try:
            return json.loads(raw)
        except:
            return None