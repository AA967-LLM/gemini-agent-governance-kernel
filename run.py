import argparse
import asyncio
import sys
from kernel.advisory_kernel import AdvisoryKernel
from governance.gemini_council import GeminiCouncil
from core.registry import AgentRegistry
from core.gemini_agent import GeminiAgent
from dashboard.app import CouncilDashboard

async def main():
    parser = argparse.ArgumentParser(description="Gemini v6.0 Civilization Kernel")
    parser.add_argument("--code", help="Code or Task to execute")
    parser.add_argument("--context", default="General Task", help="Context for the task")
    parser.add_argument("--visualize", action="store_true", help="Launch the Flight Recorder Dashboard")
    parser.add_argument("--enforce", action="store_true", help="Enable enforcing mode (block on FAIL)")

    args = parser.parse_args()

    # 1. Setup Registry
    registry = AgentRegistry()
    registry.register("LeadArchitect", lambda cfg: GeminiAgent("LeadArchitect", "Lead Architect. I prioritize structure, efficiency, and correctness."))
    registry.register("AdversarialValidator", lambda cfg: GeminiAgent("AdversarialValidator", "Security Auditor. I find flaws, bugs, and security risks."))

    # 2. Setup Council (Hierarchical)
    council_config = [
        {"name": "LeadArchitect", "weight": 3.0, "veto_power": False},
        {"name": "AdversarialValidator", "weight": 1.0, "veto_power": True}
    ]
    council = GeminiCouncil(registry=registry, config=council_config)

    # 3. Setup Kernel
    kernel = AdvisoryKernel(council=council, enforcing=args.enforce)

    # 4. Execution Mode
    if args.visualize:
        print("Launching Flight Recorder... (Ctrl+C to exit)")
        dashboard = CouncilDashboard()
        
        async def background_task():
            await asyncio.sleep(2) 
            if args.code:
                await kernel.execute_task(args.code, {"context": args.context})
        
        async with asyncio.TaskGroup() as tg:
            tg.create_task(dashboard.run_async())
            tg.create_task(background_task())
            
    elif args.code:
        print(f"--- CIVILIZATION KERNEL: EXECUTING TASK ---")
        try:
            result = await kernel.execute_task(args.code, {"context": args.context})
            print(f"\n[VERDICT]: {result['governance_verdict']}")
            
            if result.get('route'):
                route = result['route']
                print(f"[ROUTING]: {route.model} via {route.primary_provider}")
                
            print(f"[OUTCOME]: {result['outcome']}")
        except Exception as e:
            print(f"\n[ERROR]: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass