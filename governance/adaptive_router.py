from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from core.token_manager import TokenManager

@dataclass
class RoutingDecision:
    primary_provider: str
    model: str
    reason: str
    max_tokens: int

class AdaptiveRouter:
    """
    Routes tasks based on complexity.
    Optimized for Gemini Pro/Flash (v3/v2.5) and Groq 70B tiers.
    Strict Rule: Never use 8B models.
    """
    
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    async def route_task(self, task_description: str, complexity: int) -> RoutingDecision:
        """
        Selects the best provider/model.
        """
        # Trivial Tasks (Complexity 1-2) -> Gemini Flash (v3 preferred)
        if complexity <= 2:
            return RoutingDecision(
                primary_provider="google",
                model="gemini-3-flash", # Elite Fallback
                reason="Trivial Task - Using Gemini 3 Flash for elite speed/intelligence.",
                max_tokens=2000
            )
            
        # Standard Validation (Complexity 3-4) -> Groq (70B+ Tier)
        if complexity <= 4:
            allowed, reason, _, model = await self.token_manager.can_make_request("groq", complexity=complexity)
            if allowed:
                return RoutingDecision(
                    primary_provider="groq",
                    model=model, # Managed by GroqModelManager (Llama 70B / Mixtral)
                    reason="Standard Validation - Using Groq 70B Tier.",
                    max_tokens=4000
                )
            else:
                # Fallback to Gemini 2.5/3 Flash if Groq is limited
                return RoutingDecision(
                    primary_provider="google",
                    model="gemini-2.5-flash",
                    reason=f"Groq Limited ({reason}) - Fallback to Gemini 2.5 Flash.",
                    max_tokens=4000
                )

        # Complex Architecture (Complexity 5) -> Gemini 3 Pro
        return RoutingDecision(
            primary_provider="google",
            model="gemini-3-pro",
            reason="Complex Task - Using Gemini 3 Pro for maximum reasoning depth.",
            max_tokens=8192
        )
