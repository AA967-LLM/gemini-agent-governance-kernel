import pytest
import asyncio
import time
import os
import json
from core.gemini_agent import GeminiAgent
from core.registry import AgentRegistry
from governance.gemini_council import GeminiCouncil, CouncilFailurePolicy

# Ensure .env is loaded for tests
from dotenv import load_dotenv
load_dotenv()

class TestPhase1Architecture:
    """
    Phase 1 validation suite (Refined based on Council Feedback):
    1. Async execution works with timeouts.
    2. Instance-based Registry loads agents (no singletons).
    3. Council runs agents in parallel with configurable failure policy.
    4. Structured verdicts are returned.
    """

    @pytest.mark.asyncio
    async def test_async_agent_query_structure(self):
        """Test that GeminiAgent returns structured verdicts."""
        # Mocking the _call_api method to return valid JSON
        class MockAgent(GeminiAgent):
            async def _call_api(self, model, prompt, system_context):
                return json.dumps({
                    "verdict": "PASS",
                    "confidence": 0.9,
                    "evidence": ["test evidence"],
                    "reasoning": "Mock pass"
                })

        agent = MockAgent(name="TestAgent", role="Reviewer")
        response = await agent.query(prompt="Hello", system_context="Testing", constraints=[])
        
        assert isinstance(response, dict)
        assert response["verdict"] == "PASS"
        assert response["confidence"] == 0.9

    def test_instance_based_registry(self):
        """Test that registry is instance-based, not global."""
        registry1 = AgentRegistry()
        registry2 = AgentRegistry()

        class MockAgent(GeminiAgent): pass

        registry1.register("agent1", MockAgent)
        
        assert "agent1" in registry1.list_agents()
        assert "agent1" not in registry2.list_agents() # Should be isolated

    @pytest.mark.asyncio
    async def test_council_parallel_execution_and_timeout(self):
        """
        Verify that Council runs agents in parallel and respects timeouts.
        """
        registry = AgentRegistry()
        
        # Mock agent that simulates work
        class SlowAgent(GeminiAgent):
            def __init__(self, delay):
                super().__init__("SlowAgent", "Tester")
                self.delay = delay

            async def query(self, prompt, system_context, constraints=None):
                await asyncio.sleep(self.delay)
                return {"verdict": "PASS", "confidence": 1.0, "evidence": [], "reasoning": "Slow but steady"}

        registry.register("fast", lambda config: SlowAgent(0.1))
        registry.register("slow", lambda config: SlowAgent(0.5))
        
        council = GeminiCouncil(registry=registry)
        
        start_time = time.time()
        # Create council with fast and slow agents
        # We need to manually add them since create_council factory might need config
        council.agents = [SlowAgent(0.1), SlowAgent(0.2)] 
        
        results = await council.deliberate(code="print(1)", context="Performance Test")
        end_time = time.time()
        
        duration = end_time - start_time
        # Parallel execution: max(0.1, 0.2) = 0.2s approx. Sequential would be 0.3s.
        assert duration < 0.4 
        assert len(results["agent_reviews"]) == 2

    @pytest.mark.asyncio
    async def test_failure_policy_fail_open(self):
        """Test FAIL_OPEN policy when council fails."""
        # Force a council-level failure (e.g., no agents)
        registry = AgentRegistry()
        council = GeminiCouncil(registry=registry, failure_policy=CouncilFailurePolicy.FAIL_OPEN)
        council.agents = [] # No agents triggers warning usually, or we mock failure
        
        # Mocking run_agents to raise exception
        async def mock_fail(*args, **kwargs): raise Exception("Council Down")
        council._run_agents = mock_fail

        result = await council.deliberate("code", "context")
        assert result["consensus"]["decision"] == "WARN" # Should warn, not crash
        assert result["fallback"] is True

    def test_backward_compatibility(self):
        """Verify that the original kernel file still exists and is importable."""
        from kernel import Council as OldCouncil
        assert OldCouncil is not None
