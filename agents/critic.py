from core.agent import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="The Critic",
            role_description="Your job is to review code for high-level logical flaws, architectural anti-patterns, and security risks. Be harsh but fair."
        )

    def review(self, code: str, context: str = ""):
        prompt = f"Please review the following code for architectural integrity:\n\n{code}"
        return self.query(prompt, system_context=context)
