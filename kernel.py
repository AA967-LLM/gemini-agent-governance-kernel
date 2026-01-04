import argparse
import sys
from governance.council import Council

def main():
    parser = argparse.ArgumentParser(description="Gemini Agent Governance Kernel")
    parser.add_argument("--code", required=True, help="Code to review")
    parser.add_argument("--context", default="Kernel Verification", help="Context of the review")
    
    args = parser.parse_args()
    
    council = Council()
    print("--- DELIBERATION IN PROGRESS ---")
    results = council.deliberate(args.code, args.context)
    
    for agent, feedback in results.items():
        print(f"\n[{agent.upper()} FEEDBACK]")
        print("-" * 20)
        print(feedback)
        print("-" * 20)

if __name__ == "__main__":
    main()

