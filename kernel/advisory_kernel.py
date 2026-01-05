from typing import Dict, Any, Optional
from governance.gemini_council import GeminiCouncil
from core.linter import CodeLinter
import os

class GovernanceError(Exception):
    """Raised when Council blocks execution (Enforcing Mode)."""
    pass

class AdvisoryKernel:
    """
    The Core Execution Kernel (v6.0).
    Orchestrates the lifecycle: Deliberate -> Decide -> Execute -> Learn.
    """
    def __init__(self, council: GeminiCouncil, enforcing: bool = False):
        self.council = council
        self.enforcing = enforcing
        self.linter = CodeLinter()

    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execution Pipeline:
        1. Consult Council (Deliberation).
        2. Block if FAIL (Enforcing) or Log (Advisory).
        3. Execute Task (Simulated).
        4. Verify (Linting).
        5. Record Outcome (Learning).
        """
        context_str = str(context) if context else "No context provided"

        # 1. Deliberate (Phase 4b: Routing handled inside Council)
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

        # 3. Execute (Simulated for v6.0 Kernel)
        outcome = "SUCCESS"
        details = {}

        if "fail" in task.lower() or "error" in task.lower():
            outcome = "FAILURE"
            details = {"error": "Simulated failure based on task keywords", "failed_line": task}

        # 4. Verify (The Linter Protocol)
        # Scan workspace for syntax errors to ensure no "Indentation Errors" were left behind.
        # In a real run, this would check specific files modified.
        # Here we do a quick spot check if the task implies python modification.
        if "python" in task.lower() or ".py" in task.lower():
            lint_passed, lint_error = self._lint_workspace()
            if not lint_passed:
                outcome = "FAILURE"
                details["error"] = f"Linter Failed: {lint_error}"
                print(f"[LINTER] âš ï¸  Syntax Error Detected: {lint_error}")

        # 5. Record Outcome for Learning
        await self.council.record_outcome(verdict, outcome, details)

        return {
            "status": "executed",
            "outcome": outcome,
            "task": task,
            "governance_verdict": decision,
            "route": verdict.get("route")
        }

    def _lint_workspace(self) -> tuple[bool, Optional[str]]:
        """Scans python files in current directory for syntax errors."""
        # Check specific critical directories
        for root, _, files in os.walk("."):
            if "venv" in root or "__pycache__" in root: continue
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    valid, err = self.linter.check_file(path)
                    if not valid:
                        return False, f"{file}: {err}"
        return True, None