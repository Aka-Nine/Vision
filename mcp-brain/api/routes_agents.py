from fastapi import APIRouter
from core.orchestrator import orchestrator

router = APIRouter(prefix='/agents')

@router.get('/status')
async def agents_status():
    return {"status": "ok", "active_agents": []}
