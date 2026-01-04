import time
import json
from datetime import datetime
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
from core.groq_model_manager import GroqModelManager

@dataclass
class ProviderLimits:
    rpm_limit: int = 30
    tpm_limit: int = 600000 
    daily_budget: float = 5.0 
    
class TokenManager:
    """
    Manages Rate Limits (Groq) and Budget (Gemini Pro + Flash).
    Integrated with GroqModelManager for rotation.
    """
    
    def __init__(self, config_path: str = ".gemini/token_config.json"):
        self.config_path = Path(config_path)
        self.limits = ProviderLimits()
        self.groq_manager = GroqModelManager()
        
        # Runtime State
        self.gemini_spend_today = 0.0
        self.last_reset_date = datetime.now().date()
        self._load_state()

    def _load_state(self):
        """Loads persistent state (budget) from disk."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.gemini_spend_today = data.get("gemini_spend", 0.0)
                    saved_date = data.get("date")
                    if saved_date != str(datetime.now().date()):
                        self.gemini_spend_today = 0.0
            except Exception as e:
                print(f"[TokenManager] Error loading config: {e}")

    def _save_state(self):
        """Saves daily spend."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump({
                    "gemini_spend": self.gemini_spend_today,
                    "date": str(datetime.now().date())
                }, f)
        except Exception as e:
            print(f"[TokenManager] Error saving config: {e}")

    async def can_make_request(self, provider: str, estimated_tokens: int = 1000, complexity: int = 1, task_type: str = "general") -> Tuple[bool, str, float, Optional[str]]:
        """
        Extended check supporting Model selection.
        Returns: (Allowed, Reason, WaitTime, ModelName)
        """
        if provider.lower() == "groq":
            # Groq Manager selects model
            model = self.groq_manager.get_model_for_task(complexity, task_type)
            if not model:
                return False, "No suitable Groq model (Use Flash)", 0.0, None
                
            allowed, reason, wait = self.groq_manager.can_make_request(model.name, estimated_tokens)
            return allowed, reason, wait, model.name
            
        elif provider.lower() == "google":
            # Check Budget
            cost = estimated_tokens * 0.000005 # Pro estimate
            # Flash is cheaper ($0.0000005), logic could be refined if model known
            
            if self.gemini_spend_today + cost > self.limits.daily_budget:
                return False, "Budget Exceeded", 0.0, None
                
            return True, "OK", 0.0, "gemini-1.5-pro" # Default, Router overrides for Flash
            
        return False, "Unknown Provider", 0.0, None

    def record_usage(self, provider: str, tokens: int, model: str = None, status_code: int = 200):
        """Records usage."""
        if provider.lower() == "groq":
            if model:
                self.groq_manager.record_request(model, tokens, status_code)
            
        elif provider.lower() == "google":
            # Rough cost: Pro vs Flash
            rate = 0.0000005 if "flash" in (model or "").lower() else 0.000005
            cost = tokens * rate
            self.gemini_spend_today += cost
            self._save_state()

    def get_status(self) -> Dict:
        """Returns stats."""
        return {
            "groq": {
                "current_model": self.groq_manager.get_current_model().name,
                "status": "ACTIVE"
            },
            "gemini": {
                "spend": round(self.gemini_spend_today, 4),
                "budget": self.limits.daily_budget,
                "status": "HEALTHY" if self.gemini_spend_today < (self.limits.daily_budget * 0.8) else "WARN"
            }
        }