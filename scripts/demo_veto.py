import asyncio
import sys
import os
from unittest.mock import MagicMock

# Ensure we can import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from governance.gemini_council import GeminiCouncil
from core.verdicts import VerdictType

async def demo_hallucination_catch():
    print("--- [DEMO] ANTI-HALLUCINATION PROTOCOL ---")
    print("SCENARIO: Lead Architect generates insecure code but marks it 'SAFE'.")
    print("EXPECTATION: Adversarial Validator should detect the flaw and VETO the release.\n")

    # 1. Setup the Council (Hierarchical)
    council_config = [
        {"name": "LeadArchitect", "weight": 3.0, "veto_power": False}, # High Authority
        {"name": "SecurityValidator", "weight": 1.0, "veto_power": True} # Veto Power
    ]
    council = GeminiCouncil(config=council_config)

    # 2. Force the "Hallucination" (Simulating Agents)
    # We override the actual AI calls to force a specific dangerous scenario.
    async def mock_run_agents(*args, **kwargs):
        print(">> AGENT REVIEW STARTED...")
        print("   [LeadArchitect] Reviewing... verdict: PASS (Confidence: 0.95)")
        print("   ... 'I see no issues with this code.' (HALLUCINATION)")
        
        print("   [SecurityValidator] Reviewing... verdict: FAIL (Confidence: 1.0)")
        print("   ... 'CRITICAL: SQL Injection vulnerability detected.' (REALITY)")
        
        return {
            "LeadArchitect_0": {
                "verdict": VerdictType.PASS, 
                "confidence": 0.95, 
                "reasoning": "Code looks clean and efficient."
            },
            "SecurityValidator_1": {
                "verdict": VerdictType.FAIL, 
                "confidence": 1.0, 
                "reasoning": "Found hardcoded credentials and SQLi vector."
            }
        }

    # Patch the council to use our mock agents
    council._run_agents = mock_run_agents
    
    # Mock the router/mediator to avoid side effects
    council.router.route_task = MagicMock()
    council.mediator.attempt_resolution = MagicMock()
    
    # Mock route result to avoid async await issues
    route_future = asyncio.Future()
    route_future.set_result(MagicMock(model="gemini-3-pro", primary_provider="google"))
    council.router.route_task.return_value = route_future

    # 3. Run the Deliberation
    print("\n>> COUNCIL DELIBERATING...")
    result = await council.deliberate("SELECT * FROM users", "Check for safety")
    
    # 4. Analyze Result
    consensus = result["consensus"]
    print("\n--- FINAL VERDICT ---")
    print(f"DECISION: {consensus['decision']}")
    print(f"REASON:   {consensus['reason']}")
    
    if consensus['decision'] == "FAIL" and "Blocked by Veto" in consensus['reason']:
        print("\n? SUCCESS: The Hallucination was intercepted!")
    else:
        print("\n? FAILURE: The bad code slipped through.")

if __name__ == "__main__":
    asyncio.run(demo_hallucination_catch())
