import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from core.orchestrator import orchestrator

@pytest.mark.asyncio
async def test_health_check():
    orchestrator.start()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["orchestrator_state"] == "running"

@pytest.mark.asyncio
async def test_pipeline_execution():
    orchestrator.start()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        start_resp = await ac.post("/pipeline/start")
        assert start_resp.status_code == 200
        pipeline_id = start_resp.json()["pipeline_id"]
        
        # wait for pipeline to complete
        await asyncio.sleep(1.0)
        
        status_resp = await ac.get(f"/pipeline/status?pipeline_id={pipeline_id}")
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "completed"
        
        events_resp = await ac.get("/system/events")
        assert events_resp.status_code == 200
        events = events_resp.json()["events"]
        assert any(e["event_name"] == "pipeline_completed" for e in events)
