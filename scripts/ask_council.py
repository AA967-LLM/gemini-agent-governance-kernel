import sys
import os
import argparse
from consensus import CouncilEngine
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Query the Council of AI (Groq Edition)")
    parser.add_argument("--code", required=True, help="Code snippet to review")
    parser.add_argument("--context", default="General logic check", help="Context for the review")
    parser.add_argument("--target", choices=["critic", "specialist", "both"], default="both")
    
    args = parser.parse_args()
    engine = CouncilEngine()
    
    print("-" * 30)
    print(" COUNCIL DELIBERATION (GROQ-POWERED) ")
    print("-" * 30)
    
    if args.target in ["critic", "both"]:
        print("\n[THE CRITIC (Resilient Chain)]")
        print(engine.ask_critic(f"Context: {args.context}\nCode:\n{args.code}"))
        
    if args.target in ["specialist", "both"]:
        print("\n[THE SPECIALIST (Resilient Chain)]")
        print(engine.ask_specialist(args.code))
        
    print("-" * 30)

if __name__ == "__main__":
    main()
