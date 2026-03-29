import uuid
import asyncio
from agents.market_intelligence_agent import MarketIntelligenceAgent
from core.event_bus import event_bus
from pipelines.state_tracker import state_tracker
from monitoring.metrics import metrics

class MarketPipeline:
    def __init__(self):
        self.market_agent = MarketIntelligenceAgent()
        self.max_retries = 3

    async def run(self, input_data: str):
        pipeline_id = str(uuid.uuid4())
        metrics.increment_pipeline_run()
        state_tracker.create_pipeline(pipeline_id)
        
        await event_bus.emit("pipeline_started", {"pipeline_id": pipeline_id, "type": "market_intelligence"})
        
        attempt = 0
        while attempt < self.max_retries:
            try:
                state_tracker.update_stage(pipeline_id, "running", "started")
                
                # Execute Phase 2: Market Intelligence Engine
                result = await self.market_agent.run({"input": input_data})
                
                state_tracker.update_stage(pipeline_id, "completed", "running")
                state_tracker.complete_pipeline(pipeline_id)
                metrics.increment_pipeline_success()
                
                await event_bus.emit("pipeline_completed", {"pipeline_id": pipeline_id, "result": result})
                return pipeline_id, result
            except Exception as e:
                attempt += 1
                state_tracker.update_stage(pipeline_id, f"retrying_{attempt}", "failed_attempt")
                
                if attempt >= self.max_retries:
                    state_tracker.fail_pipeline(pipeline_id, str(e))
                    metrics.increment_pipeline_failure()
                    await event_bus.emit("pipeline_failed", {"pipeline_id": pipeline_id, "error": str(e)})
                    raise e
                    
                await asyncio.sleep(2 ** attempt) # Exponential backoff
