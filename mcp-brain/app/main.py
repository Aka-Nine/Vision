import sys
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.orchestrator import orchestrator
from api import routes_pipeline, routes_agents, routes_monitoring, routes_storage, routes_market, routes_generator, routes_llm

# Playwright requires subprocess support; on Windows ensure Proactor loop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

@asynccontextmanager
async def lifespan(app: FastAPI):
    orchestrator.start()
    yield
    print("Shutting down orchestrator...")

app = FastAPI(title='MCP Brain', lifespan=lifespan)

app.include_router(routes_pipeline.router)
app.include_router(routes_agents.router)
app.include_router(routes_monitoring.router)
app.include_router(routes_storage.router)
app.include_router(routes_market.router)
app.include_router(routes_generator.router)
app.include_router(routes_llm.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

