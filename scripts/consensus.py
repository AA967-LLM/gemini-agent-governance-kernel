import os
import requests
import json
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class CouncilEngine:
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        # Resilient Chain: List of models to try in order of preference
        self.model_chain = [
            "llama-3.3-70b-versatile",
            "llama3-70b-8192", 
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]
        self.default_model = self.model_chain[0]
        
    def _query_groq(self, prompt: str, system_role: str) -> str:
        if not self.groq_key:
            return "Error: GROQ_API_KEY not found in .env file."
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }

        # Iterate through the resilient chain
        errors = []
        for model in self.model_chain:
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                
                # If rate limited (429) or server error (5xx), try next model
                # If 400 (Bad Request), it might be the model name, so also try next.
                error_msg = f"Model {model} failed: {response.status_code} - {response.text}"
                errors.append(error_msg)
                print(f"Warning: {error_msg}. Switching to next model in chain...")
                time.sleep(1) # Brief pause before retry
                
            except Exception as e:
                error_msg = f"Model {model} exception: {str(e)}"
                errors.append(error_msg)
                print(f"Warning: {error_msg}. Switching to next model in chain...")

        return f"All models in Resilient Chain failed. Errors:\n" + "\n".join(errors)

    def ask_critic(self, prompt: str) -> str:
        """The Critic: Logical and architectural review."""
        system_role = "You are The Critic. Your job is to review code for high-level logical flaws, architectural anti-patterns, and security risks. Be harsh but fair."
        return self._query_groq(prompt, system_role)

    def ask_specialist(self, prompt: str) -> str:
        """The Specialist: Code-level verification."""
        system_role = "You are The Specialist. Your job is to review code for syntax errors, null-safety issues, variable naming, and idiomatic correctness. Focus on the implementation details."
        return self._query_groq(prompt, system_role)

    def get_consensus(self, draft_code: str, context: str) -> Dict[str, str]:
        """Runs the draft through both roles (simulated by different personas on Groq)."""
        critic_prompt = f"Context: {context}\nReview this code:\n{draft_code}"
        specialist_prompt = f"Review this code:\n{draft_code}"
        
        return {
            "critic": self.ask_critic(critic_prompt),
            "specialist": self.ask_specialist(specialist_prompt)
        }

if __name__ == "__main__":
    engine = CouncilEngine()
    print("Groq-Only Council Engine initialized (Resilient Chain Active).")