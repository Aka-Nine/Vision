import asyncio
from pipelines.market_pipeline import MarketPipeline
from storage.metadata_store import metadata_store
import json

async def run_test():
    print("Starting Market Intelligence Pipeline...")
    pipeline = MarketPipeline()
    pipeline_id, result = await pipeline.run("Test real gemini integration")
    
    print("\n=== PIPELINE COMPLETED ===")
    print("Pipeline ID:", pipeline_id)
    print("\n--- Final Brief ---")
    print(json.dumps(result.get("brief", {}), indent=2))
    
    print("\n--- Checking Storage (market_data.json) ---")
    with open("market_data.json", "r") as f:
        data = json.load(f)
        print("Trends stored:", len(data['trends']))
        print("Briefs stored:", len(data['design_briefs']))

if __name__ == "__main__":
    asyncio.run(run_test())
