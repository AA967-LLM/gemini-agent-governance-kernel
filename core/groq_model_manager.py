import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GroqModel:
    name: str
    rate_limit_rpm: int = 30
    rate_limit_tpm: int = 40000
    requests_this_minute: int = 0
    tokens_this_minute: int = 0
    last_request_time: Optional[datetime] = None
    tier: str = "workhorse" # flagship, workhorse, utility

class GroqModelManager:
    """
    Manages Groq models with rotation and rate limiting.
    EXCLUDES llama3-8b per user preference (Gemini Flash is preferred fallback).
    """

    def __init__(self, models: List[GroqModel] = None):
        # Default chain of models (High Quality Only)
        self.models = models or [
            GroqModel("llama-3.3-70b-versatile", 30, 40000, tier="flagship"),
            GroqModel("mixtral-8x7b-32768", 30, 40000, tier="workhorse"),
            GroqModel("llama3-70b-8192", 30, 40000, tier="workhorse"),
        ]

        # Current active model index
        self.current_model_index = 0
        
        # Background task to reset rate limits
        self._start_reset_task()

    def _start_reset_task(self):
        """Start background task to reset rate limits every minute"""
        async def reset_loop():
            while True:
                await asyncio.sleep(60)
                self._reset_minute_counts()

        # Start in background (simplified for CLI context)
        # In a full app this would be a proper async task
        pass 

    def _reset_minute_counts(self):
        """Reset minute counts for all models"""
        for model in self.models:
            model.requests_this_minute = 0
            model.tokens_this_minute = 0

    def get_current_model(self) -> GroqModel:
        return self.models[self.current_model_index]

    def rotate_model(self):
        """Rotate to the next model in the chain"""
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        print(f"[GroqModelManager] Rotated to model: {self.get_current_model().name}")

    def can_make_request(self, model_name: str, estimated_tokens: int) -> Tuple[bool, str, float]:
        """Check if we can make a request to the specified model"""
        model = next((m for m in self.models if m.name == model_name), None)
        if not model:
            return False, f"Model {model_name} not found", 0.0

        # Simple check (In real imp, check timestamps)
        if model.requests_this_minute >= model.rate_limit_rpm:
             return False, f"Rate limit exceeded for {model_name}", 60.0
             
        return True, "OK", 0.0

    def record_request(self, model_name: str, tokens_used: int, status_code: int):
        """Record a request to a model"""
        model = next((m for m in self.models if m.name == model_name), None)
        if not model:
            return

        model.requests_this_minute += 1
        model.tokens_this_minute += tokens_used
        model.last_request_time = datetime.now()

        # If we got a 429, rotate immediately
        if status_code == 429:
            self.rotate_model()

    def get_model_for_task(self, complexity: int, task_type: str = "general") -> Optional[GroqModel]:
        """
        Selects the best Groq model. 
        Returns None if task is trivial and should use Gemini Flash instead.
        """
        # Trivial tasks -> Gemini Flash (handled by Router, so we return None or lowest Groq)
        # Here we just return the current active model for standard validation
        
        # Security critical -> Enforce 70B
        if task_type == "security" and complexity >= 4:
             for model in self.models:
                 if "70b" in model.name:
                     return model
                     
        return self.get_current_model()
