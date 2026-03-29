from core.pipeline_engine import pipeline_engine
from core.task_queue import task_queue
from agents.base_agent import BaseAgent

class Orchestrator:
    def __init__(self):
        self.system_status = "initializing"
        self.agents_active = []

    def start(self):
        task_queue.start_workers()
        self.system_status = "running"

    async def start_pipeline(self, input_data=""):
        return await pipeline_engine.trigger_pipeline(input_data)

    def get_pipeline_status(self, pipeline_id):
        return pipeline_engine.get_status(pipeline_id)

orchestrator = Orchestrator()
