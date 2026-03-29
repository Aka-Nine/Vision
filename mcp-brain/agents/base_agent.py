import asyncio
from core.event_bus import event_bus

class BaseAgent:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.status = "idle"

    async def run(self, task_input):
        self.status = "running"
        await self.log_activity("agent_started", {"input": task_input})
        
        await asyncio.sleep(0.1)  # Simulate work
        output = await self.process(task_input)
        
        self.status = "completed"
        await self.log_activity("agent_finished", {"output": output})
        return output

    async def process(self, task_input):
        raise NotImplementedError

    async def validate_output(self, output):
        return True

    async def log_activity(self, event_type, data):
        data["agent"] = self.name
        await event_bus.emit(event_type, data)
