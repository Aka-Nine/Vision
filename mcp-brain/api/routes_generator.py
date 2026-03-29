"""
Generator API Routes — Phase 3
POST /generator/build        — trigger template generation from a brief
GET  /generator/templates    — list all generated templates
GET  /generator/template/{n} — get a specific template's metadata
"""
import os, json, logging, base64
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from pipelines.template_pipeline import TemplatePipeline
from storage.metadata_store import metadata_store
from app.config import settings
from services.screenshot_to_code_client import ScreenshotToCodeClient
from services.website_capture import capture_website_video

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generator")

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_templates")
REGISTRY_PATH = os.path.join(TEMPLATES_DIR, "template_registry.json")


class BuildRequest(BaseModel):
    brief: Optional[dict] = None
    brief_index: Optional[int] = None  # pick a brief by index from market_data.json


class BuildFromUrlRequest(BaseModel):
    url: str
    prompt: Optional[str] = ""


@router.post("/build")
async def build_template(req: BuildRequest):
    """Trigger template generation from a design brief."""
    brief = req.brief

    if brief is None and req.brief_index is not None:
        briefs = metadata_store.get_design_briefs()
        if 0 <= req.brief_index < len(briefs):
            brief = briefs[req.brief_index]
        else:
            raise HTTPException(status_code=400, detail=f"Invalid brief_index: {req.brief_index}. Available: 0-{len(briefs)-1}")

    if brief is None:
        # Default: use the latest design brief
        briefs = metadata_store.get_design_briefs()
        if not briefs:
            raise HTTPException(status_code=400, detail="No design briefs available. Run the market pipeline first.")
        brief = briefs[-1]

    pipeline = TemplatePipeline()
    pipeline_id, result = await pipeline.run(brief)

    return {
        "pipeline_id": pipeline_id,
        "status": "completed",
        "template_name": result.get("template_name"),
        "components_generated": result.get("components_generated"),
        "generation_time": result.get("generation_time_seconds"),
        "package": result.get("package", {}).get("zip_path"),
    }

@router.post("/from-screenshot")
async def build_from_screenshot(
    screenshot: UploadFile = File(...),
    prompt: str = "",
):
    """
    Generate code from a screenshot using the local screenshot-to-code service,
    then store it as a previewable template under generated_templates/.
    """
    if screenshot.content_type not in ("image/png", "image/jpeg", "image/webp"):
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {screenshot.content_type}")

    raw = await screenshot.read()
    b64 = base64.b64encode(raw).decode("utf-8")
    data_url = f"data:{screenshot.content_type};base64,{b64}"

    client = ScreenshotToCodeClient(
        settings.s2c_backend_ws_url,
        stack=settings.s2c_stack,
        openai_api_key=settings.s2c_openai_api_key,
        openai_base_url=settings.s2c_openai_base_url,
        anthropic_api_key=settings.s2c_anthropic_api_key,
        gemini_api_key=settings.s2c_gemini_api_key or settings.gemini_api_key,
    )

    try:
        result = await client.generate_from_image_data_url(image_data_url=data_url, prompt_text=prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Persist as a simple HTML template (first variant)
    template_name = f"s2c-{int(__import__('time').time())}"
    tmpl_dir = os.path.join(TEMPLATES_DIR, template_name)
    os.makedirs(tmpl_dir, exist_ok=True)

    code = (result.variants[0] if result.variants else "").strip()
    if not code:
        raise HTTPException(status_code=500, detail="screenshot-to-code returned empty code")

    with open(os.path.join(tmpl_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(code)

    # Append minimal registry entry
    entry = {
        "template_name": template_name,
        "version": "1.0",
        "framework": settings.s2c_stack,
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "source_brief": "screenshot_to_code",
        "components": 0,
        "template_type": "Screenshot-to-Code Output",
        "target_market": "N/A",
        "demand_score": None,
        "sections": [],
        "style_theme": "unknown",
        "validation": {"valid": True, "warnings": 0},
    }

    registry = []
    if os.path.isfile(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f) or []
        except Exception:
            registry = []
    registry.append(entry)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    return {
        "status": "completed",
        "template_name": template_name,
        "stack": settings.s2c_stack,
        "variants": len(result.variants),
        "generation_time_seconds": result.elapsed_seconds,
        "preview_url": f"/template-preview/{template_name}",
    }


@router.post("/from-url")
async def build_from_url(req: BuildFromUrlRequest):
    """
    Visit a URL, record a short interaction video (to preserve animations),
    then generate code via screenshot-to-code video mode.
    """
    url = (req.url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must start with http:// or https://")

    # Capture a short video + screenshot of the real site with deep analysis.
    try:
        cap = await capture_website_video(
            url=url, 
            out_dir="storage/visuals", 
            record_seconds=10, 
            deep_analyze=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"capture failed: {type(e).__name__}: {e!r}")

    try:
        with open(cap.video_path, "rb") as f:
            vb64 = base64.b64encode(f.read()).decode("utf-8")
        video_data_url = f"data:video/webm;base64,{vb64}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"video load failed: {e}")

    # Prompt: preserve animations/layout, only change copy.
    hard_prompt = (
        "Recreate the UI and animations as closely as possible from the recording. "
        "Preserve layout, spacing, styling, and motion/scroll effects. "
        "ONLY change the text/copy content to new wording; keep the same hierarchy and text lengths similar."
    )
    prompt = (req.prompt or "").strip()
    final_prompt = hard_prompt if not prompt else f"{hard_prompt}\n\nCustom text guidance:\n{prompt}"

    client = ScreenshotToCodeClient(
        settings.s2c_backend_ws_url,
        stack=settings.s2c_stack,
        openai_api_key=settings.s2c_openai_api_key,
        openai_base_url=settings.s2c_openai_base_url,
        anthropic_api_key=settings.s2c_anthropic_api_key,
        gemini_api_key=settings.s2c_gemini_api_key or settings.gemini_api_key,
    )

    try:
        result = await client.generate_from_video_data_url(video_data_url=video_data_url, prompt_text=final_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"s2c failed: {e}")

    template_name = f"s2c-url-{int(__import__('time').time())}"
    tmpl_dir = os.path.join(TEMPLATES_DIR, template_name)
    os.makedirs(tmpl_dir, exist_ok=True)

    code = (result.variants[0] if result.variants else "").strip()
    if not code:
        raise HTTPException(status_code=500, detail="screenshot-to-code returned empty code")

    with open(os.path.join(tmpl_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(code)

    # Store the captured artifacts alongside the output for traceability.
    try:
        import shutil
        shutil.copy2(cap.screenshot_path, os.path.join(tmpl_dir, "source.png"))
        shutil.copy2(cap.video_path, os.path.join(tmpl_dir, "source.webm"))
    except Exception:
        pass

    entry = {
        "template_name": template_name,
        "version": "1.0",
        "framework": settings.s2c_stack,
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "source_brief": "screenshot_to_code_url",
        "components": 0,
        "template_type": "Screenshot-to-Code (URL recording)",
        "target_market": "N/A",
        "demand_score": None,
        "sections": [],
        "style_theme": "unknown",
        "validation": {"valid": True, "warnings": 0},
        "source_url": cap.final_url,
    }

    registry = []
    if os.path.isfile(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f) or []
        except Exception:
            registry = []
    registry.append(entry)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    return {
        "status": "completed",
        "template_name": template_name,
        "stack": settings.s2c_stack,
        "variants": len(result.variants),
        "generation_time_seconds": result.elapsed_seconds,
        "preview_url": f"/template-preview/{template_name}",
        "source_url": cap.final_url,
    }


@router.get("/templates")
async def list_templates():
    """List all generated templates from the registry."""
    if not os.path.isfile(REGISTRY_PATH):
        return {"status": "ok", "templates": []}
    with open(REGISTRY_PATH) as f:
        try:
            registry = json.load(f)
        except json.JSONDecodeError:
            registry = []
    return {"status": "ok", "count": len(registry), "templates": registry}


@router.get("/template/{name}")
async def get_template(name: str):
    """Get metadata for a specific generated template."""
    if not os.path.isfile(REGISTRY_PATH):
        raise HTTPException(status_code=404, detail="No templates have been generated yet")
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)
    for entry in registry:
        if entry.get("template_name") == name:
            return {"status": "ok", "template": entry}
    raise HTTPException(status_code=404, detail=f"Template '{name}' not found")
