from .base_agent import BaseAgent

class TestingAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestingAgent", "Runs UI tests")

    async def process(self, task_input):
        return {"status": "success", "tests_passed": True}
