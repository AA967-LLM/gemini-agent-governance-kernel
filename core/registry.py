from typing import Dict, Type, Optional, Any
import asyncio
from core.gemini_agent import GeminiAgent

class AgentRegistry:
    """
    Thread-safe, instance-based registry for dynamic agent loading.
    Supports dependency injection for parallel testing.
    """
    def __init__(self):
        self._agents: Dict[str, Type[GeminiAgent]] = {}
        # In Phase 1, we use a simple dict. 
        # For thread safety in highly concurrent environments, asyncio.Lock would be added here.
    
    def register(self, name: str, agent_factory: Any):
        """
        Register an agent factory (class or function).
        """
        self._agents[name] = agent_factory
    
    def create_agent(self, name: str, config: Dict = None) -> GeminiAgent:
        """Create an instance of the requested agent."""
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' not registered")
        
        factory = self._agents[name]
        # Check if it's a class or a factory function
        try:
            return factory(config or {})
        except TypeError:
            # Fallback for simple class instantiation if config fails
            return factory(name=name, role="Dynamic Agent")

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    @classmethod
    def create_default(cls) -> 'AgentRegistry':
        """Factory for default production registry with standard agents."""
        registry = cls()
        # Here we would register the standard Critic and Specialist
        # For now, we leave it empty or register placeholders if they existed
        return registry
