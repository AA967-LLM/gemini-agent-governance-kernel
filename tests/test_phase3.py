import pytest
import asyncio
import os
import json
import shutil
from pathlib import Path
from core.gemini_agent import GeminiAgent
from core.registry import AgentRegistry
from governance.gemini_council import GeminiCouncil, CouncilFailurePolicy
from core.memory_store import MemoryStore
from core.constraints import ConstraintTier

# Setup a clean test memory directory
TEST_MEMORY_DIR = ".gemini/test_memory"

@pytest.fixture(autouse=True)
def setup_test_memory():
    if os.path.exists(TEST_MEMORY_DIR):
        shutil.rmtree(TEST_MEMORY_DIR)
    os.makedirs(TEST_MEMORY_DIR)
    yield
    # Cleanup after tests
    # shutil.rmtree(TEST_MEMORY_DIR)

class TestPhase3Learning:
    """
    Phase 3 validation suite:
    1. Council records outcomes.
    2. False Negatives (PASS -> FAILURE) trigger learning.
    3. Learned constraints are injected into future deliberation prompts.
    """

    @pytest.mark.asyncio
    async def test_institutional_learning_loop(self):
        """Verify the full loop: Deliberate -> Fail -> Learn -> Re-deliberate."""
        
        # 1. Initialize Council with Test Memory
        memory = MemoryStore(storage_dir=TEST_MEMORY_DIR)
        registry = AgentRegistry()
        
        # Mock agent that passes everything initially
        class PassiveAgent(GeminiAgent):
            def __init__(self, name, role):
                super().__init__(name, role)
                self.received_constraints = []

            async def query(self, prompt, system_context=None, constraints=None):
                self.received_constraints = constraints or []
                return {
                    "verdict": "PASS",
                    "confidence": 0.9,
                    "reasoning": "Standard pass",
                    "evidence": []
                }

        registry.register("passive", lambda cfg: PassiveAgent("Passive", "Tester"))
        council = GeminiCouncil(registry=registry, memory_store=memory)
        agent = PassiveAgent("Passive", "Tester")
        council.agents = [agent]

        # 2. First Deliberation (Should have no constraints)
        code = "eval(user_input)"
        verdict = await council.deliberate(code, "Testing learning")
        assert verdict["consensus"]["decision"] == "PASS"
        assert len(agent.received_constraints) == 0

        # 3. Record a FAILURE (False Negative)
        await council.record_outcome(
            verdict, 
            "FAILURE", 
            {"error": "Security Breach: eval used", "failed_line": code}
        )

        # 4. Verify Constraint was Created
        active_constraints = memory.get_active_constraints(language="python")
        assert len(active_constraints) == 1
        assert active_constraints[0].tier == ConstraintTier.EXPERIMENTAL
        assert "eval" in active_constraints[0].description

        # 5. Second Deliberation (Should now have constraints injected)
        verdict2 = await council.deliberate(code, "Re-testing after learning")
        
        # Check if the agent received the learned constraint
        assert len(agent.received_constraints) == 1
        assert agent.received_constraints[0].id == active_constraints[0].id

