from typing import Dict, Any, Optional
from kernel import GeminiKernel # Assuming v5.2 kernel exists
from governance.gemini_council import GeminiCouncil

class GovernanceError(Exception):
    """Raised when Council blocks execution (Enforcing Mode)."""
    pass

class AdvisoryKernel(GeminiKernel):
    """
    Adapter Pattern: Bridges v5.2 Kernel with v6.0 Council.
    Consults Council before execution.
    """
    def __init__(self, council: GeminiCouncil, enforcing: bool = False):
        super().__init__() # Initialize v5.2 kernel
        self.council = council
        self.enforcing = enforcing

    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Overridden execution method.
        1. Consult Council.
        2. Block if FAIL (Enforcing) or Log (Advisory).
        3. Execute via Parent Kernel.
        4. Record Outcome.
        """
        context_str = str(context) if context else "No context provided"
        
        # 1. Deliberate
        verdict = await self.council.deliberate(task, context_str)
        consensus = verdict.get("consensus", {})
        decision = consensus.get("decision", "FAIL")
        
        # 2. Enforce Governance
        if decision == "FAIL":
            reason = consensus.get("reason", "Unknown")
            msg = f"Council Blocked Execution: {reason}"
            
            if self.enforcing:
                await self.council.record_outcome(verdict, "BLOCKED", {"reason": reason})
                raise GovernanceError(msg)
            else:
                print(f"[GOVERNANCE ADVISORY] {msg} - Proceeding (Advisory Mode)")
        
        # 3. Execute (Simulation for Phase 3)
        # In real life: result = await super().execute_task(task, context)
        # For testing learning, we'll simulate a success or failure
        
        outcome = "SUCCESS"
        details = {}
        
        if "fail" in task.lower():
            outcome = "FAILURE"
            details = {"error": "Simulated failure", "failed_line": task}
        
        # 4. Record Outcome for Learning
        await self.council.record_outcome(verdict, outcome, details)
        
        return {
            "status": "executed",
            "outcome": outcome,
            "task": task,
            "governance_verdict": decision
        }
