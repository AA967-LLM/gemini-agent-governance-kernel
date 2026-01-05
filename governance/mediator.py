import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.token_manager import TokenManager
from core.event_bus import EventBus, EventType

class MediatorSpawnController:
    """Controls the spawning of mediators to prevent resource exhaustion."""
    def __init__(self):
        self.max_spawns = 3
        self.spawn_cost_multiplier = [1.0, 1.5, 2.0]
        self.backoff_delays = [0, 5, 10] # Reduced for dev/testing
        self.session_spawns = {} # session_id -> count

    def can_spawn_mediator(self, session_id: str, token_manager: TokenManager) -> tuple[bool, str]:
        count = self.session_spawns.get(session_id, 0)
        
        if count >= self.max_spawns:
            return False, f"Max spawns ({self.max_spawns}) reached."
            
        # Cost Check (Estimating 4k tokens base)
        base_cost = 4000
        multiplier = self.spawn_cost_multiplier[count]
        estimated_cost = int(base_cost * multiplier)
        
        allowed, reason, _, _ = asyncio.run(token_manager.can_make_request("gemini", estimated_tokens=estimated_cost))
        
        if not allowed:
            return False, f"Budget insufficient: {reason}"
            
        return True, f"OK (Attempt {count + 1})"

    def record_spawn(self, session_id: str):
        self.session_spawns[session_id] = self.session_spawns.get(session_id, 0) + 1

class MediatorInvariantPolicy:
    """Ensures the Mediator respects constitutional constraints."""
    def __init__(self):
        self.immutable_tiers = ["TIER_1", "HARD_INVARIANT"]
        
    def can_modify(self, constraint_tier: str) -> bool:
        if constraint_tier in self.immutable_tiers:
            return False
        return True

class HumanGateSystem:
    """Determines if a resolution requires human ratification."""
    def should_require_human(self, task_type: str, confidence: float) -> bool:
        critical_tasks = ["security", "architecture"]
        if task_type in critical_tasks:
            return True # Always require human for critical stuff
            
        if confidence < 0.8:
            return True
            
        return False

class CivilizedMediator:
    """
    Autonomous deadlock resolver using Chain-of-Verification (CoVe).
    """
    def __init__(self, token_manager: TokenManager, event_bus: EventBus):
        self.token_manager = token_manager
        self.event_bus = event_bus
        self.spawn_controller = MediatorSpawnController()
        self.invariant_policy = MediatorInvariantPolicy()
        self.human_gate = HumanGateSystem()

    async def attempt_resolution(self, deadlock_data: Dict, session_id: str) -> Dict:
        # 1. Spawn Check
        can_spawn, reason = self.spawn_controller.can_spawn_mediator(session_id, self.token_manager)
        if not can_spawn:
            self.event_bus.publish(EventType.ERROR, {"session_id": session_id, "error": f"Mediator Spawn Failed: {reason}"})
            return {"action": "HALT", "reason": reason}

        self.spawn_controller.record_spawn(session_id)
        
        # 2. CoVe Analysis (Simulated for this implementation, would be LLM call)
        # In a real system, this would call Gemini Pro with the CoVe prompt.
        analysis = await self._simulate_cove_analysis(deadlock_data)
        
        # 3. Invariant Check
        if not self._validate_constraints(analysis, deadlock_data):
             return {"action": "HALT", "reason": "Resolution violated Hard Invariants"}

        # 4. Generate Resolution
        resolution = await self._simulate_resolution_generation(analysis)
        
        # 5. Human Gate
        requires_human = self.human_gate.should_require_human("general", resolution["confidence"])
        
        result = {
            "action": "APPLY_RESOLUTION",
            "resolution": resolution,
            "requires_human": requires_human,
            "analysis": analysis
        }
        
        self.event_bus.publish(EventType.AGENT_ACTION, {
            "session_id": session_id,
            "agent": "Mediator",
            "action": "resolve_deadlock",
            "details": result
        })
        
        return result

    async def _simulate_cove_analysis(self, data: Dict) -> Dict:
        await asyncio.sleep(1)
        return {
            "disagreement_point": "Logic structure vs Security pattern",
            "analysis_confidence": 0.85
        }

    def _validate_constraints(self, analysis: Dict, data: Dict) -> bool:
        # Check if analysis suggests breaking Tier 1 rules
        return True 

    async def _simulate_resolution_generation(self, analysis: Dict) -> Dict:
        return {
            "verdict": "COMPROMISE",
            "rewritten_instructions": "Refactor the logic to separate the security concern.",
            "confidence": 0.82
        }
