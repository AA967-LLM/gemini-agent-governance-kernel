from agents.critic import CriticAgent
from agents.specialist import SpecialistAgent
from typing import Dict

class Council:
    def __init__(self):
        self.critic = CriticAgent()
        self.specialist = SpecialistAgent()

    def deliberate(self, code: str, context: str = "General Review") -> Dict[str, str]:
        """Runs the consensus process across all council members."""
        results = {
            "critic": self.critic.review(code, context),
            "specialist": self.specialist.review(code, context)
        }
        return results
