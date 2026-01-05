import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from core.memory_store import MemoryStore
from core.constraints import Constraint, ConstraintTier, ConstraintScope

class FeedbackLoop:
    """
    The Institutional Reflexion Loop.
    Learns from execution outcomes to refine future governance.
    """
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    async def record_outcome(self, verdict: Dict, outcome: str, details: Dict):
        """
        Processes the result of an execution.
        verdict: The original council deliberation result.
        outcome: 'SUCCESS', 'FAILURE', or 'INCIDENT'.
        details: Metadata about the failure (error logs, etc).
        """
        consensus = verdict.get("consensus", {})
        decision = consensus.get("decision")
        
        # 1. Record the incident/outcome
        incident_record = {
            "verdict_id": verdict.get("session_id", str(uuid.uuid4())),
            "decision": decision,
            "outcome": outcome,
            "details": details
        }
        self.memory_store.record_incident(incident_record)

        # 2. Logic: False Negative (Council approved bad code)
        if decision == "PASS" and outcome in ["FAILURE", "INCIDENT"]:
            await self._learn_from_failure(verdict, details)
        
        # 3. Logic: True Positive (Council blocked code that would have failed)
        # Note: Hard to verify if blocked code *would* have failed, 
        # but we can reinforce 'FAIL' verdicts that are later validated.

    async def _learn_from_failure(self, verdict: Dict, details: Dict):
        """
        Extracts a pattern from the failure and proposes a new constraint.
        """
        # In Phase 3, we create an 'EXPERIMENTAL' constraint based on the failure.
        # Ideally, we would use an LLM to extract the specific pattern.
        # For now, we stub with a generic constraint based on the error.
        
        error_msg = details.get("error", "Unknown runtime error")
        context = details.get("context", "general")
        
        # Create a new experimental constraint
        new_id = f"C-{str(uuid.uuid4())[:8]}"
        description = f"Auto-learned: Prevent failure related to '{error_msg[:50]}'"
        
        # Pattern extraction is a stub: we'd ideally extract code patterns
        pattern = details.get("failed_line", "Unknown") 
        
        new_constraint = Constraint(
            id=new_id,
            description=description,
            pattern=pattern,
            tier=ConstraintTier.EXPERIMENTAL,
            source="reflexion_loop",
            scope=ConstraintScope(domain="security" if "security" in error_msg.lower() else "general"),
            metadata={"original_error": error_msg}
        )
        
        self.memory_store.add_constraint(new_constraint)
        print(f"[REFLEXION] New experimental constraint added: {new_id}")
