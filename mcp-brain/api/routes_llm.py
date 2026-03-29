"""
LLM Gateway API Routes
GET  /llm/stats      — usage statistics for both LLM providers
POST /llm/query      — direct query to the dual-LLM gateway
GET  /llm/models     — list available local models
"""
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from core.llm_gateway import llm_gateway, LLMTaskType, LLMProvider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm")


class LLMQueryRequest(BaseModel):
    prompt: str
    task_type: Optional[str] = "general"
    provider: Optional[str] = None
    json_mode: Optional[bool] = True
    system_prompt: Optional[str] = ""


@router.get("/stats")
async def get_llm_stats():
    """Return usage statistics for both LLM providers."""
    return {"status": "ok", "stats": llm_gateway.get_stats()}


@router.post("/query")
async def query_llm(req: LLMQueryRequest):
    """Direct query to the dual-LLM gateway."""
    try:
        task = LLMTaskType(req.task_type)
    except ValueError:
        task = LLMTaskType.GENERAL

    provider = None
    if req.provider:
        try:
            provider = LLMProvider(req.provider)
        except ValueError:
            pass

    response = await llm_gateway.query(
        prompt=req.prompt,
        task_type=task,
        provider=provider,
        json_mode=req.json_mode,
        system_prompt=req.system_prompt or "",
    )
    return {"status": "ok", **response}


@router.get("/models")
async def list_models():
    """List available local Ollama models."""
    try:
        import ollama
        models = ollama.list()
        model_list = []
        if hasattr(models, 'models'):
            for m in models.models:
                model_list.append({
                    "name": m.model,
                    "size_bytes": m.size if hasattr(m, 'size') else None,
                    "modified": str(m.modified_at) if hasattr(m, 'modified_at') else None,
                })
        return {"status": "ok", "models": model_list, "active_model": llm_gateway.llama_model}
    except Exception as e:
        return {"status": "error", "error": str(e), "models": []}
