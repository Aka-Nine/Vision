"""
Dual-LLM Gateway — LLaMA (Local) + Gemini (Cloud)
═══════════════════════════════════════════════════
Central AI service that routes requests between:
  • LLaMA 3 8B via Ollama   — fast local inference for drafts, validation, structuring
  • Gemini 2.5 Pro via API  — high-quality cloud inference for creative/complex tasks

Strategy: "Draft-Refine" pipeline
  1. LLaMA produces a fast JSON draft locally (no API cost, no rate limits)
  2. Gemini refines/enhances only when needed (saves quota)
  3. Either can fallback to the other if one fails

System Specs Optimised For:
  CPU: Intel i3-1115G4 (2C/4T)
  RAM: 8 GB (LLaMA 3 8B Q4 fits in ~5GB)
  GPU: None (CPU-only inference)
  Model: llama3:latest via Ollama
"""

import json
import logging
import time
import asyncio
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    LLAMA_LOCAL = "llama_local"
    GEMINI_CLOUD = "gemini_cloud"
    DUAL = "dual"           # LLaMA draft → Gemini refine
    AUTO = "auto"           # pick best based on task


class LLMTaskType(str, Enum):
    """Task types with different routing strategies."""
    TREND_ANALYSIS = "trend_analysis"         # Gemini (needs vision)
    BRIEF_GENERATION = "brief_generation"     # Dual: LLaMA draft → Gemini refine
    CODE_REVIEW = "code_review"               # LLaMA only (fast, local)
    SECTION_PLANNING = "section_planning"     # LLaMA only (structured output)
    STYLE_SUGGESTION = "style_suggestion"     # Dual
    CONTENT_WRITING = "content_writing"       # Dual
    VALIDATION = "validation"                 # LLaMA only (fast)
    GENERAL = "general"                       # Auto-route


# ── Routing rules ───────────────────────────────────────────────────
TASK_ROUTING = {
    LLMTaskType.TREND_ANALYSIS:    LLMProvider.GEMINI_CLOUD,   # needs multi-modal vision
    LLMTaskType.BRIEF_GENERATION:  LLMProvider.DUAL,
    LLMTaskType.CODE_REVIEW:       LLMProvider.LLAMA_LOCAL,
    LLMTaskType.SECTION_PLANNING:  LLMProvider.LLAMA_LOCAL,
    LLMTaskType.STYLE_SUGGESTION:  LLMProvider.DUAL,
    LLMTaskType.CONTENT_WRITING:   LLMProvider.DUAL,
    LLMTaskType.VALIDATION:        LLMProvider.LLAMA_LOCAL,
    LLMTaskType.GENERAL:           LLMProvider.AUTO,
}


class DualLLMGateway:
    """
    Unified interface to query LLaMA local and/or Gemini cloud models.
    Supports Draft-Refine pipeline for combined results.
    """

    def __init__(self):
        self.llama_model = "mcp-brain:latest"
        self.gemini_model_name = "gemini-2.5-pro"
        self._gemini_model = None
        self._ollama_available = None
        self._gemini_available = None
        self.stats = {
            "llama_calls": 0, "llama_failures": 0,
            "gemini_calls": 0, "gemini_failures": 0,
            "dual_calls": 0,
            "total_llama_time": 0.0, "total_gemini_time": 0.0,
        }

    # ── Lazy initialisers ───────────────────────────────────────────
    def _init_gemini(self):
        if self._gemini_model is not None:
            return self._gemini_model
        try:
            import google.generativeai as genai
            from app.config import settings
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self._gemini_model = genai.GenerativeModel(self.gemini_model_name)
                self._gemini_available = True
                logger.info("Gemini %s initialised", self.gemini_model_name)
            else:
                self._gemini_available = False
                logger.warning("No Gemini API key — cloud disabled")
        except Exception as e:
            self._gemini_available = False
            logger.warning("Gemini init failed: %s", e)
        return self._gemini_model

    async def _check_ollama(self) -> bool:
        if self._ollama_available is not None:
            return self._ollama_available
        try:
            import ollama
            models = ollama.list()
            available_names = [m.model for m in models.models] if hasattr(models, 'models') else []
            # Check for our custom mcp-brain model, or any llama variant
            self._ollama_available = any(
                ("mcp-brain" in str(n) or "llama" in str(n))
                for n in available_names
            )
            if self._ollama_available:
                logger.info("Ollama ready — model: %s", self.llama_model)
            else:
                logger.warning("Ollama running but no suitable model found. Available: %s", available_names)
        except Exception as e:
            self._ollama_available = False
            logger.warning("Ollama not available: %s", e)
        return self._ollama_available

    # ── Public API ──────────────────────────────────────────────────

    async def query(
        self,
        prompt: str,
        task_type: LLMTaskType = LLMTaskType.GENERAL,
        provider: Optional[LLMProvider] = None,
        json_mode: bool = True,
        system_prompt: str = "",
    ) -> dict:
        """
        Send prompt to the appropriate LLM(s).

        Returns
        -------
        dict with keys: result, provider_used, llama_draft, gemini_refined, time_seconds
        """
        route = provider or TASK_ROUTING.get(task_type, LLMProvider.AUTO)

        if route == LLMProvider.AUTO:
            route = await self._auto_route()

        if route == LLMProvider.DUAL:
            return await self._dual_query(prompt, system_prompt, json_mode)
        elif route == LLMProvider.LLAMA_LOCAL:
            return await self._llama_query(prompt, system_prompt, json_mode)
        elif route == LLMProvider.GEMINI_CLOUD:
            return await self._gemini_query(prompt, system_prompt, json_mode)
        else:
            return await self._dual_query(prompt, system_prompt, json_mode)

    # ── Dual "Draft-Refine" ─────────────────────────────────────────

    async def _dual_query(self, prompt: str, system_prompt: str, json_mode: bool) -> dict:
        """LLaMA drafts → Gemini refines (or vice-versa on failure)."""
        self.stats["dual_calls"] += 1

        # Step 1: LLaMA draft
        llama_draft = None
        llama_ok = await self._check_ollama()
        if llama_ok:
            draft_result = await self._llama_query(
                prompt, system_prompt, json_mode
            )
            if draft_result.get("result"):
                llama_draft = draft_result["result"]

        # Step 2: Gemini refine using the LLaMA draft as context
        gemini_refined = None
        self._init_gemini()
        if self._gemini_available and llama_draft:
            refine_prompt = self._build_refine_prompt(prompt, llama_draft)
            refine_result = await self._gemini_query(
                refine_prompt, system_prompt, json_mode
            )
            if refine_result.get("result"):
                gemini_refined = refine_result["result"]

        # Determine best result
        if gemini_refined:
            final = gemini_refined
            used = "dual (llama_draft + gemini_refine)"
        elif llama_draft:
            final = llama_draft
            used = "llama_local (gemini unavailable)"
        else:
            # Both failed — try Gemini standalone
            standalone = await self._gemini_query(prompt, system_prompt, json_mode)
            final = standalone.get("result")
            used = "gemini_cloud (llama unavailable)"

        return {
            "result": final,
            "provider_used": used,
            "llama_draft": llama_draft,
            "gemini_refined": gemini_refined,
        }

    # ── LLaMA via Ollama ────────────────────────────────────────────

    async def _llama_query(self, prompt: str, system_prompt: str, json_mode: bool) -> dict:
        """Query LLaMA 3 through Ollama (CPU inference)."""
        available = await self._check_ollama()
        if not available:
            return {"result": None, "provider_used": "llama_local", "error": "Ollama not available"}

        start = time.time()
        self.stats["llama_calls"] += 1

        try:
            import ollama

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            options = {"temperature": 0.3, "num_predict": 2048}
            if json_mode:
                response = ollama.chat(
                    model=self.llama_model,
                    messages=messages,
                    format="json",
                    options=options,
                )
            else:
                response = ollama.chat(
                    model=self.llama_model,
                    messages=messages,
                    options=options,
                )

            elapsed = time.time() - start
            self.stats["total_llama_time"] += elapsed
            text = response["message"]["content"]

            if json_mode:
                try:
                    parsed = json.loads(text)
                    return {"result": parsed, "provider_used": "llama_local", "time_seconds": round(elapsed, 2)}
                except json.JSONDecodeError:
                    return {"result": text, "provider_used": "llama_local", "time_seconds": round(elapsed, 2)}
            else:
                return {"result": text, "provider_used": "llama_local", "time_seconds": round(elapsed, 2)}

        except Exception as e:
            self.stats["llama_failures"] += 1
            elapsed = time.time() - start
            logger.error("LLaMA query failed (%.1fs): %s", elapsed, e)
            return {"result": None, "provider_used": "llama_local", "error": str(e)}

    # ── Gemini via Google API ───────────────────────────────────────

    async def _gemini_query(self, prompt: str, system_prompt: str, json_mode: bool) -> dict:
        """Query Gemini through Google Generative AI API."""
        self._init_gemini()
        if not self._gemini_available:
            return {"result": None, "provider_used": "gemini_cloud", "error": "Gemini not available"}

        start = time.time()
        self.stats["gemini_calls"] += 1

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        if json_mode:
            full_prompt += "\n\nReturn ONLY pure valid JSON. No markdown wrappers."

        try:
            response = self._gemini_model.generate_content(full_prompt)
            elapsed = time.time() - start
            self.stats["total_gemini_time"] += elapsed

            text = response.text.strip()
            if text.startswith("```json"):
                text = text.split("```json", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

            if json_mode:
                try:
                    parsed = json.loads(text)
                    return {"result": parsed, "provider_used": "gemini_cloud", "time_seconds": round(elapsed, 2)}
                except json.JSONDecodeError:
                    return {"result": text, "provider_used": "gemini_cloud", "time_seconds": round(elapsed, 2)}
            else:
                return {"result": text, "provider_used": "gemini_cloud", "time_seconds": round(elapsed, 2)}

        except Exception as e:
            self.stats["gemini_failures"] += 1
            elapsed = time.time() - start
            logger.error("Gemini query failed (%.1fs): %s", elapsed, e)
            return {"result": None, "provider_used": "gemini_cloud", "error": str(e)}

    # ── Helpers ─────────────────────────────────────────────────────

    async def _auto_route(self) -> LLMProvider:
        """Pick provider based on availability."""
        ollama_ok = await self._check_ollama()
        self._init_gemini()
        if ollama_ok and self._gemini_available:
            return LLMProvider.DUAL
        elif self._gemini_available:
            return LLMProvider.GEMINI_CLOUD
        elif ollama_ok:
            return LLMProvider.LLAMA_LOCAL
        raise RuntimeError("No LLM provider available (Ollama down + Gemini unconfigured)")

    def _build_refine_prompt(self, original_prompt: str, llama_draft) -> str:
        """Build a refinement prompt for Gemini using LLaMA's draft."""
        draft_str = json.dumps(llama_draft, indent=2) if isinstance(llama_draft, (dict, list)) else str(llama_draft)
        return f"""You are a senior AI product architect. A junior AI assistant has drafted a response.
Review, enhance, and improve it. Fix any errors, add missing detail, and make it production-quality.

## Original Task
{original_prompt}

## Draft Response (from local AI)
{draft_str}

## Your Job
Produce an improved, final version. Keep the same JSON structure but make it significantly better.
Return ONLY the improved JSON."""

    def get_stats(self) -> dict:
        """Return usage statistics for monitoring."""
        return {
            **self.stats,
            "avg_llama_time": (
                round(self.stats["total_llama_time"] / max(self.stats["llama_calls"], 1), 2)
            ),
            "avg_gemini_time": (
                round(self.stats["total_gemini_time"] / max(self.stats["gemini_calls"], 1), 2)
            ),
        }


# ── Singleton ───────────────────────────────────────────────────────
llm_gateway = DualLLMGateway()
