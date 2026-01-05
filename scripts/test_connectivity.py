import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)

async def test_connectivity():
    print("--- 1. Querying Available Models ---")
    try:
        # List all models
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        print(f"Found {len(models)} models supporting content generation:")
        found_v3 = False
        found_v2_5 = False
        
        for m in models:
            print(f" - {m.name}")
            if "gemini-3" in m.name: found_v3 = True
            if "gemini-2.5" in m.name: found_v2_5 = True
            
        print("\n--- 2. Verifying 'Gemini 3' Availability ---")
        if found_v3:
            print("? Gemini 3 models found in API list.")
        else:
            print("? Gemini 3 models NOT found in API list. (Checking aliases...)")

        # Test specific high-tier targets (Hypothetical & Current)
        targets = ["gemini-3-pro", "gemini-3-flash"]
        # Add the user-requested ones to test if they work as aliases
        targets.extend(["gemini-3-pro", "gemini-2.5-pro"])

        print("\n--- 3. Active Connectivity Test ---")
        for model_name in targets:
            print(f"Testing connectivity to '{model_name}'...", end=" ")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Ping. Reply with 'Pong'.")
                print(f"? SUCCESS. Response: {response.text.strip()}")
            except Exception as e:
                print(f"? FAILED. Error: {str(e)[:100]}...")

    except Exception as e:
        print(f"Fatal Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_connectivity())
