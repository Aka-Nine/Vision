from .base_agent import BaseAgent

class StorageAgent(BaseAgent):
    def __init__(self):
        super().__init__("StorageAgent", "Stores data locally and remotely")

    async def process(self, task_input):
        return {"status": "success", "saved": True}
