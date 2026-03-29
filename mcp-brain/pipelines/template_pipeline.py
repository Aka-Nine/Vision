"""
Template Pipeline — Phase 3 (Generative UI Upgraded)
Wraps TemplateGeneratorAgent in retry logic, state tracking, and event emission.
Now acts as the sole autonomous UI generator.
"""
import uuid, asyncio, logging
from agents.template_generator_agent import TemplateGeneratorAgent
from core.event_bus import event_bus
from pipelines.state_tracker import state_tracker
from monitoring.metrics import metrics

logger = logging.getLogger(__name__)

PIPELINE_STAGES = [
    "brief_parsing",
    "project_building",
    "style_generation",
    "layout_building",
    "component_generation",
    "asset_generation",
    "code_validation",
    "preview_generation",
    "packaging",
]


class TemplatePipeline:
    def __init__(self):
        self.generator_agent = TemplateGeneratorAgent()
        self.max_retries = 3

    async def run(
        self,
        brief: dict,
        semantic_brief: dict = None,
    ) -> tuple:
        """
        Parameters
        ----------
        brief : dict — a single design brief from market_data.json
        semantic_brief : dict — Phase 2.5 semantic brief (optional)

        Returns
        -------
        (pipeline_id, result)
        """
        pipeline_id = str(uuid.uuid4())
        metrics.increment_pipeline_run()
        state_tracker.create_pipeline(pipeline_id)

        await event_bus.emit("pipeline_started", {
            "pipeline_id": pipeline_id,
            "type": "template_generation",
        })

        attempt = 0
        while attempt < self.max_retries:
            try:
                state_tracker.update_stage(pipeline_id, "running", "started")

                result = await self.generator_agent.run({
                    "brief": brief,
                    "semantic_brief": semantic_brief,
                })

                state_tracker.update_stage(pipeline_id, "completed", "running")
                state_tracker.complete_pipeline(pipeline_id)
                metrics.increment_pipeline_success()

                await event_bus.emit("pipeline_completed", {
                    "pipeline_id": pipeline_id,
                    "result": result,
                    "generator": "template",
                })
                return pipeline_id, result

            except Exception as e:
                attempt += 1
                state_tracker.update_stage(pipeline_id, f"retrying_{attempt}", "failed_attempt")
                logger.error("Template pipeline attempt %d failed: %s", attempt, e)

                if attempt >= self.max_retries:
                    state_tracker.fail_pipeline(pipeline_id, str(e))
                    metrics.increment_pipeline_failure()
                    await event_bus.emit("pipeline_failed", {
                        "pipeline_id": pipeline_id,
                        "error": str(e),
                    })
                    raise

                await asyncio.sleep(2 ** attempt)



