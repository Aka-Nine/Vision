import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import websockets


@dataclass
class ScreenshotToCodeResult:
    variant_models: List[str]
    variants: List[str]
    elapsed_seconds: float


class ScreenshotToCodeClient:
    def __init__(
        self,
        ws_url: str,
        *,
        stack: str,
        openai_api_key: str = "",
        openai_base_url: str = "",
        anthropic_api_key: str = "",
        gemini_api_key: str = "",
    ):
        self.ws_url = ws_url
        self.stack = stack
        self.openai_api_key = openai_api_key or None
        self.openai_base_url = openai_base_url or None
        self.anthropic_api_key = anthropic_api_key or None
        self.gemini_api_key = gemini_api_key or None

    async def generate_from_image_data_url(
        self,
        *,
        image_data_url: str,
        prompt_text: str = "",
    ) -> ScreenshotToCodeResult:
        """
        Calls screenshot-to-code backend via WebSocket (/generate-code).
        Returns all variants; callers can pick the best or first.
        """
        if not (self.openai_api_key or self.anthropic_api_key or self.gemini_api_key):
            raise ValueError("No screenshot-to-code API key configured (OpenAI/Anthropic/Gemini).")

        params: Dict[str, Any] = {
            "generationType": "create",
            "inputMode": "image",
            "prompt": {
                "text": prompt_text or "",
                "images": [image_data_url],
                "videos": [],
            },
            "history": [],
            "fileState": None,
            "optionCodes": [],
            "openAiApiKey": self.openai_api_key,
            "openAiBaseURL": self.openai_base_url,
            "screenshotOneApiKey": None,
            "isImageGenerationEnabled": False,
            "editorTheme": "espresso",
            "generatedCodeConfig": self.stack,
            "codeGenerationModel": "default",
            "isTermOfServiceAccepted": True,
            "anthropicApiKey": self.anthropic_api_key,
            "geminiApiKey": self.gemini_api_key,
        }

        started = time.time()
        variant_models: List[str] = []
        variants: Dict[int, str] = {}

        async with websockets.connect(self.ws_url, max_size=25 * 1024 * 1024) as ws:
            await ws.send(json.dumps(params))

            async for msg in ws:
                payload = json.loads(msg)
                msg_type = payload.get("type")
                variant_index = int(payload.get("variantIndex", 0) or 0)

                if msg_type == "variantModels":
                    variant_models = list((payload.get("data") or {}).get("models") or [])
                elif msg_type in ("chunk", "setCode"):
                    variants[variant_index] = payload.get("value") or ""
                elif msg_type == "error":
                    raise RuntimeError(payload.get("value") or "screenshot-to-code error")

        # Normalize contiguous list output
        max_idx = max(variants.keys(), default=0)
        out = [variants.get(i, "") for i in range(max_idx + 1)]
        return ScreenshotToCodeResult(
            variant_models=variant_models,
            variants=out,
            elapsed_seconds=round(time.time() - started, 2),
        )

    async def generate_from_video_data_url(
        self,
        *,
        video_data_url: str,
        prompt_text: str = "",
    ) -> ScreenshotToCodeResult:
        """
        Calls screenshot-to-code backend via WebSocket (/generate-code) in video mode.
        This is required to preserve motion/animations from the source recording.
        """
        if not (self.openai_api_key or self.anthropic_api_key or self.gemini_api_key):
            raise ValueError("No screenshot-to-code API key configured (OpenAI/Anthropic/Gemini).")

        params: Dict[str, Any] = {
            "generationType": "create",
            "inputMode": "video",
            "prompt": {
                "text": prompt_text or "",
                "images": [],
                "videos": [video_data_url],
            },
            "history": [],
            "fileState": None,
            "optionCodes": [],
            "openAiApiKey": self.openai_api_key,
            "openAiBaseURL": self.openai_base_url,
            "screenshotOneApiKey": None,
            "isImageGenerationEnabled": False,
            "editorTheme": "espresso",
            "generatedCodeConfig": self.stack,
            "codeGenerationModel": "default",
            "isTermOfServiceAccepted": True,
            "anthropicApiKey": self.anthropic_api_key,
            "geminiApiKey": self.gemini_api_key,
        }

        started = time.time()
        variant_models: List[str] = []
        variants: Dict[int, str] = {}

        async with websockets.connect(self.ws_url, max_size=80 * 1024 * 1024) as ws:
            await ws.send(json.dumps(params))

            async for msg in ws:
                payload = json.loads(msg)
                msg_type = payload.get("type")
                variant_index = int(payload.get("variantIndex", 0) or 0)

                if msg_type == "variantModels":
                    variant_models = list((payload.get("data") or {}).get("models") or [])
                elif msg_type in ("chunk", "setCode"):
                    variants[variant_index] = payload.get("value") or ""
                elif msg_type == "error":
                    raise RuntimeError(payload.get("value") or "screenshot-to-code error")

        max_idx = max(variants.keys(), default=0)
        out = [variants.get(i, "") for i in range(max_idx + 1)]
        return ScreenshotToCodeResult(
            variant_models=variant_models,
            variants=out,
            elapsed_seconds=round(time.time() - started, 2),
        )

