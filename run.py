import argparse
import asyncio
import threading
import sys
from kernel.advisory_kernel import AdvisoryKernel, GeminiCouncil
from core.registry import AgentRegistry
from agents.critic import CriticAgent
from agents.specialist import SpecialistAgent
from dashboard.app import CouncilDashboard

def run_dashboard():
    """Runs the TUI Dashboard in a blocking call."""
    app = CouncilDashboard()
    app.run()

async def main():
    parser = argparse.ArgumentParser(description="Gemini v6.0 Governance Kernel Launcher")
    parser.add_argument("--code", help="Code to review and execute")
    parser.add_argument("--context", default="General Task", help="Context for the task")
    parser.add_argument("--visualize", action="store_true", help="Launch the TUI Dashboard (opens in this window)")
    parser.add_argument("--enforce", action="store_true", help="Enable enforcing mode (block on FAIL)")
    
    args = parser.parse_args()

    # 1. Setup Registry and Agents
    registry = AgentRegistry()
    registry.register("critic", lambda cfg: CriticAgent())
    registry.register("specialist", lambda cfg: SpecialistAgent())
    
    # 2. Setup Council
    # For Phase 4a, we pass some dummy config to initialize weights
    council_config = [
        {"name": "critic", "weight": 0.5, "veto_power": False},
        {"name": "specialist", "weight": 1.0, "veto_power": True}
    ]
    council = GeminiCouncil(registry=registry, config=council_config)
    
    # Manually add agents for this session
    council.agents = [CriticAgent(), SpecialistAgent()]

    # 3. Setup Kernel
    kernel = AdvisoryKernel(council=council, enforcing=args.enforce)

    # 4. Handle Visualization
    if args.visualize:
        print("Launching Dashboard... (Press Ctrl+C to exit dashboard and return to CLI)")
        # Note: Textual takes over the terminal. 
        # In a real integrated flow, we might run deliberation in a background task
        # and let the dashboard show the progress.
        
        dashboard = CouncilDashboard()
        
        # We start the deliberation in a background task that starts AFTER the dashboard mounts
        async def background_deliberation():
            await asyncio.sleep(2) # Wait for UI to settle
            if args.code:
                await kernel.execute_task(args.code, {"context": args.context})
        
        # Run both
        async with asyncio.TaskGroup() as tg:
            tg.create_task(dashboard.run_async())
            tg.create_task(background_deliberation())
    else:
        # Standard CLI Flow
        if args.code:
            print(f"--- DELIBERATING: {args.context} ---")
            result = await kernel.execute_task(args.code, {"context": args.context})
            print(f"\nFINAL VERDICT: {result['governance_verdict']}")
            print(f"OUTCOME: {result['outcome']}")
        else:
            parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
