from .base_agent import BaseAgent

class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__("MarketAgent", "Analyzes market trends")

    async def process(self, task_input):
        return {"status": "success", "market_data": "trending designs found"}
