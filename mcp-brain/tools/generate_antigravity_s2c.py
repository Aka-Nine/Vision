import sys
import asyncio
import base64
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from services.screenshot_to_code_client import ScreenshotToCodeClient
from services.website_capture import capture_website_video


async def main() -> int:
    url = "https://antigravity.google/"

    cap = await capture_website_video(url=url, out_dir="storage/visuals")
    with open(cap.video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode("utf-8")
    video_data_url = f"data:video/webm;base64,{video_b64}"

    client = ScreenshotToCodeClient(
        settings.s2c_backend_ws_url,
        stack=settings.s2c_stack,
        openai_api_key=settings.s2c_openai_api_key,
        openai_base_url=settings.s2c_openai_base_url,
        anthropic_api_key=settings.s2c_anthropic_api_key,
        gemini_api_key=settings.s2c_gemini_api_key or settings.gemini_api_key,
    )

    prompt = (
        "Recreate the UI and animations as closely as possible from the recording. "
        "Preserve layout, spacing, styling, and motion/scroll effects. "
        "ONLY change the text/copy content to new wording; keep the same hierarchy and similar text lengths. "
        "Do not mention Google."
    )

    result = await client.generate_from_video_data_url(video_data_url=video_data_url, prompt_text=prompt)

    template_name = f"antigravity-s2c-{int(time.time())}"
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_templates")
    tmpl_dir = os.path.join(templates_dir, template_name)
    os.makedirs(tmpl_dir, exist_ok=True)

    code = (result.variants[0] if result.variants else "").strip()
    if not code:
        raise RuntimeError("screenshot-to-code returned empty output")

    with open(os.path.join(tmpl_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(code)

    # Copy sources
    try:
        import shutil
        shutil.copy2(cap.screenshot_path, os.path.join(tmpl_dir, "source.png"))
        shutil.copy2(cap.video_path, os.path.join(tmpl_dir, "source.webm"))
    except Exception:
        pass

    print("template_name:", template_name)
    print("preview_url:", f"http://localhost:4000/template-preview/{template_name}")
    print("variants:", len(result.variants))
    print("models:", result.variant_models)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

