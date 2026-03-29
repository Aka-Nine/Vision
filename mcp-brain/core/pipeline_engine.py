import asyncio
import uuid
from core.event_bus import event_bus
from core.task_queue import task_queue
from agents.market_agent import MarketAgent
from agents.generation_agent import GenerationAgent
from agents.testing_agent import TestingAgent
from agents.publishing_agent import PublishingAgent
from agents.storage_agent import StorageAgent

class PipelineEngine:
    def __init__(self):
        self.pipelines = {}
    
    async def execute_pipeline(self, pipeline_id, input_data):
        self.pipelines[pipeline_id] = "running"
        await event_bus.emit("pipeline_started", {"pipeline_id": pipeline_id})
        try:
            market_agent = MarketAgent()
            market_result = await market_agent.run(input_data)
            
            gen_agent = GenerationAgent()
            gen_result = await gen_agent.run(market_result)
            
            test_agent = TestingAgent()
            test_result = await test_agent.run(gen_result)
            if test_result.get("status") != "success":
                raise Exception("Testing failed")
                
            pub_agent = PublishingAgent()
            pub_result = await pub_agent.run(test_result)
            
            store_agent = StorageAgent()
            await store_agent.run(pub_result)
            
            self.pipelines[pipeline_id] = "completed"
            await event_bus.emit("pipeline_completed", {"pipeline_id": pipeline_id, "result": pub_result})
        except Exception as e:
            self.pipelines[pipeline_id] = "failed"
            await event_bus.emit("error_detected", {"pipeline_id": pipeline_id, "error": str(e)})

    async def trigger_pipeline(self, input_data=""):
        pipeline_id = str(uuid.uuid4())
        self.pipelines[pipeline_id] = "queued"
        await task_queue.enqueue(pipeline_id, self.execute_pipeline, pipeline_id, input_data)
        return pipeline_id

    def get_status(self, pipeline_id):
        return self.pipelines.get(pipeline_id, "not_found")

pipeline_engine = PipelineEngine()
