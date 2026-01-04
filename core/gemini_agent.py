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
                # Attempt recovery (Half-Open)
                return False
            return True
        return False

class GeminiAgent:
    """
    Async-first agent with semantic circuit breakers, resilient chain, and structured output.
    """
    def __init__(self, name: str, role: str, model_chain: List[str] = None):
        self.name = name
        self.role = role
        self.model_chain = model_chain or [
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.circuit_breakers = {model: CircuitBreaker() for model in self.model_chain}
        
        # Timeout Configuration
        self.timeouts = {
            "connection": 10,
            "read": 30,
            "total": 45
        }

    async def query(self, prompt: str, system_context: Optional[str] = None, constraints: List[Any] = None) -> Dict[str, Any]:
        """
        Queries the agent and returns a structured verdict (PASS/WARN/FAIL).
        Iterates through the resilient model chain.
        """
        full_system_role = f"You are {self.name}. {self.role}\n"
        full_system_role += "IMPORTANT: You must respond in valid JSON format with the following structure:\n"
        full_system_role += '{"verdict": "PASS"|"WARN"|"FAIL", "confidence": 0.0-1.0, "evidence": ["citation1", "citation2"], "reasoning": "..."}'

        # Inject Institutional Memory
        if constraints:
            full_system_role += "\n\n### INSTITUTIONAL MEMORY (LEARNED CONSTRAINTS)\n"
            full_system_role += "The following constraints have been learned from past incidents. Violating these is a hard FAIL:\n"
            for c in constraints:
                full_system_role += f"- [{c.tier.upper()}] {c.description} (Pattern: {c.pattern})\n"

        if system_context:
            full_system_role += f"\nContext: {system_context}"

        errors = []

        for model in self.model_chain:
            cb = self.circuit_breakers.get(model)
            if cb and cb.is_open():
                continue

            try:
                raw_response = await self._call_api(model, full_system_role, prompt)
                
                # Semantic Validation (Tier 1: Structure)
                parsed_response = self._validate_structure(raw_response)
                
                if parsed_response:
                    if cb: cb.record_success()
                    return parsed_response
                else:
                    if cb: cb.record_failure() # Semantic failure
                    errors.append(f"{model}: Invalid JSON structure")

            except Exception as e:
                if cb: cb.record_failure() # Network/API failure
                errors.append(f"{model}: {str(e)}")

        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "evidence": [f"All models failed. Errors: {'; '.join(errors)}"]
        }

    async def _call_api(self, model: str, system_role: str, user_prompt: str) -> str:
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY not found")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"} # Enforce JSON mode if supported
        }

        timeout = aiohttp.ClientTimeout(
            total=self.timeouts["total"],
            connect=self.timeouts["connection"],
            sock_read=self.timeouts["read"]
        )

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    resp_json = await response.json()
                    return resp_json['choices'][0]['message']['content']
                elif response.status == 429:
                    raise Exception(f"Rate limit exceeded: {response.status}")
                else:
                    raise Exception(f"API Error: {response.status} - {await response.text()}")

    def _validate_structure(self, raw_response: str) -> Optional[Dict]:
        """Validates that response is JSON and has required fields."""
        try:
            data = json.loads(raw_response)
            required_keys = ["verdict", "confidence", "evidence"]
            if all(key in data for key in required_keys):
                return data
            return None
        except json.JSONDecodeError:
            return None
