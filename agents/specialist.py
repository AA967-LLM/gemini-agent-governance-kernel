from core.agent import BaseAgent

class SpecialistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="The Specialist",
            role_description="Your job is to review code for syntax errors, null-safety issues, variable naming, and idiomatic correctness. Focus on the implementation details."
        )

    def review(self, code: str, context: str = ""):
        prompt = f"Please review the following code for implementation details and idiomatic correctness:\n\n{code}"
        return self.query(prompt, system_context=context)
