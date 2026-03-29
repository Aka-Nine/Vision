from .base_agent import BaseAgent

class GenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__("GenerationAgent", "Generates code and assets")

    async def process(self, task_input):
        return {"status": "success", "code": "<div>Hello World</div>"}
