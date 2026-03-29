from fastapi import APIRouter
from core.orchestrator import orchestrator
from core.event_bus import event_bus

router = APIRouter(prefix='/system')

@router.get('/health')
async def system_health():
    return {"status": "ok", "orchestrator_state": orchestrator.system_status}

@router.get('/events')
async def get_events():
    return {"events": event_bus.get_events()}
