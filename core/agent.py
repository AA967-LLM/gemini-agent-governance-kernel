import os
import requests
import time
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.model_chain = [
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]

    def query(self, prompt: str, system_context: Optional[str] = None) -> str:
        """Base query method using the Resilient Chain."""
        if not self.groq_key:
            return f"Error: GROQ_API_KEY missing for agent {self.name}."

        full_system_role = f"You are {self.name}. {self.role_description}"
        if system_context:
            full_system_role += f"\nContext: {system_context}"

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }

        errors = []
        for model in self.model_chain:
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": full_system_role},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                
                errors.append(f"{model}: {response.status_code}")
                time.sleep(0.5)
            except Exception as e:
                errors.append(f"{model} Exception: {str(e)}")

        return f"Agent {self.name} failed all models in chain. Errors: {', '.join(errors)}"
