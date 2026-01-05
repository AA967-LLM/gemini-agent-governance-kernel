import pytest
import asyncio
from unittest.mock import MagicMock, patch
from governance.gemini_council import GeminiCouncil, CouncilFailurePolicy
from governance.adaptive_router import AdaptiveRouter
from core.token_manager import TokenManager
from core.verdicts import VerdictType

@pytest.mark.asyncio
async def test_adaptive_routing_trivial():
    """Test that trivial tasks route to Flash."""
    tm = MagicMock(spec=TokenManager)
    # Mock async method properly
    future = asyncio.Future()
    future.set_result((True, "OK", 0.0, "gemini-1.5-flash"))
    tm.can_make_request.return_value = future
    
    router = AdaptiveRouter(tm)
    route = await router.route_task("Fix typo", complexity=1)
    
    assert route.model == "gemini-3-flash"
    assert route.primary_provider == "google"

@pytest.mark.asyncio
async def test_adaptive_routing_complex():
    """Test that complex tasks route to Pro."""
    tm = MagicMock(spec=TokenManager)
    router = AdaptiveRouter(tm)
    route = await router.route_task("Architect system", complexity=5)
    
    assert route.model == "gemini-3-pro"
    assert route.primary_provider == "google"

@pytest.mark.asyncio
async def test_council_hierarchy_veto():
    """Test that Validator (Groq) can veto Lead (Gemini)."""
    council = GeminiCouncil(config=[
        {"name": "LeadArchitect", "weight": 3.0, "veto_power": False},
        {"name": "AdversarialValidator", "weight": 1.0, "veto_power": True}
    ])
    
    # Mock agents returning conflicting results
    with patch.object(council, '_run_agents') as mock_run:
        mock_run.return_value = {
            "LeadArchitect_0": {"verdict": VerdictType.PASS, "confidence": 0.9},
            "AdversarialValidator_1": {"verdict": VerdictType.FAIL, "confidence": 1.0}
        }
        
        # We mock route_task to avoid router logic in this specific test
        council.router.route_task = MagicMock()
        route_future = asyncio.Future()
        route_future.set_result(MagicMock(model="gemini-1.5-pro", primary_provider="google"))
        council.router.route_task.return_value = route_future
        
        result = await council.deliberate("code", "context")
        assert result["consensus"]["decision"] == "FAIL"
        assert "Blocked by Veto" in result["consensus"]["reason"]

    @pytest.mark.asyncio
    async def test_mediator_deadlock_trigger():
        """Test that Mediator is triggered on deadlock."""
        config = [
            {"name": "LeadArchitect", "weight": 3.0, "veto_power": False},
            {"name": "AdversarialValidator", "weight": 1.0, "veto_power": True}
        ]
        council = GeminiCouncil(config=config)
    
        # Mock deadlock scenario (0.5 score)    with patch.object(council, '_run_agents') as mock_run:
        mock_run.return_value = {
            "LeadArchitect_0": {"verdict": VerdictType.PASS, "confidence": 0.5},
            "AdversarialValidator_1": {"verdict": VerdictType.WARN, "confidence": 0.5}
        }
        
        # Mock Mediator
        council.mediator.attempt_resolution = MagicMock()
        future = asyncio.Future()
        future.set_result({
            "action": "APPLY_RESOLUTION",
            "resolution": {"verdict": "COMPROMISE", "rewritten_instructions": "Fix it."}
        })
        council.mediator.attempt_resolution.return_value = future
        
        council.router.route_task = MagicMock()
        route_future = asyncio.Future()
        route_future.set_result(MagicMock(model="gemini-1.5-pro", primary_provider="google"))
        council.router.route_task.return_value = route_future
        
        result = await council.deliberate("code", "context")
        
        # Check if mediator was called
        council.mediator.attempt_resolution.assert_called_once()
        assert "MEDIATED" in result["consensus"]["reason"]
