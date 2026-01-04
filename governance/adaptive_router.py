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
    Routes tasks based on complexity and user preference.
    Preference: Quality over lowest-possible cost (Flash > Llama 8B).
    """
    
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    async def route_task(self, task_description: str, complexity: int) -> RoutingDecision:
        """
        Selects the best provider/model.
        """
        # Trivial Tasks -> Gemini Flash (Fast, Cheap, Smarter than 8B)
        if complexity <= 2:
            return RoutingDecision(
                primary_provider="google",
                model="gemini-1.5-flash",
                reason="Trivial Task - Using Flash for speed/cost.",
                max_tokens=2000
            )
            
        # Standard Validation -> Groq (Free Tier)
        # We prefer Llama 70B or Mixtral here.
        if complexity <= 4:
            # Check if Groq is available
            allowed, reason, _, model = await self.token_manager.can_make_request("groq", complexity=complexity)
            if allowed:
                return RoutingDecision(
                    primary_provider="groq",
                    model=model, # Managed by GroqModelManager (70B/Mixtral)
                    reason="Standard Validation - Using Groq Free Tier.",
                    max_tokens=4000
                )
            else:
                # Fallback to Flash if Groq is dead
                return RoutingDecision(
                    primary_provider="google",
                    model="gemini-1.5-flash",
                    reason=f"Groq Limited ({reason}) - Fallback to Flash.",
                    max_tokens=4000
                )

        # Complex Architecture -> Gemini Pro (The Big Gun)
        return RoutingDecision(
            primary_provider="google",
            model="gemini-1.5-pro",
            reason="Complex Task - Using Gemini Pro for maximum reasoning.",
            max_tokens=8192
        )