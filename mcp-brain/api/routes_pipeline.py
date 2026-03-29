from fastapi import APIRouter
from core.orchestrator import orchestrator

router = APIRouter(prefix='/pipeline')

@router.post('/start')
async def start_pipeline(input_data: str = ""):
    pipeline_id = await orchestrator.start_pipeline(input_data)
    return {"pipeline_id": pipeline_id, "status": "started"}

@router.post('/stop')
async def stop_pipeline():
    return {"status": "stop_requested"}

@router.get('/status')
async def pipeline_status(pipeline_id: str):
    status = orchestrator.get_pipeline_status(pipeline_id)
    return {"pipeline_id": pipeline_id, "status": status}
