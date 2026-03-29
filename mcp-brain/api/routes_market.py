from fastapi import APIRouter
from pipelines.market_pipeline import MarketPipeline
from storage.metadata_store import metadata_store

router = APIRouter(prefix='/market')

@router.post('/analyze')
async def analyze_market(input_data: str = ""):
    pipeline = MarketPipeline()
    # Execute the market intelligence pipeline
    pipeline_id, result = await pipeline.run(input_data)
    return {"pipeline_id": pipeline_id, "status": "completed", "brief": result.get("brief", {})}

@router.get('/trends')
async def get_trends():
    return {"status": "ok", "trends": metadata_store.get_trends()}

@router.get('/design_briefs')
async def get_design_briefs():
    return {"status": "ok", "briefs": metadata_store.get_design_briefs()}
