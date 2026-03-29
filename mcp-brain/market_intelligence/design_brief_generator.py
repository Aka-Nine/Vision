"""
Design Brief Generator — Fix #9 (Semantic Intent Injection)
════════════════════════════════════════════════════════════
Upgraded to inject semantic intent (tone, target_user, cta_style)
into the design brief, ensuring the generator doesn't produce
"Welcome to our platform" when it should say
"AI-powered analytics for SaaS founders".
"""

import json
import logging
from core.llm_gateway import llm_gateway, LLMTaskType

logger = logging.getLogger(__name__)


class DesignBriefGenerator:
    def __init__(self):
        self.gateway = llm_gateway

    async def generate(self, trends: dict, designs: dict, analysis: dict, patterns: dict, demand: dict, references: dict):
        system_prompt = """You are an expert Product Manager configuring a Design Brief for a UI component code generator.
Synthesize the following aggregated market intelligence data into a final structured JSON Design Brief.
The final JSON must have exactly these keys:
- "product_type" (string, specific e.g. "AI Analytics Dashboard", NOT just "SaaS Template")
- "target_market" (string, specific e.g. "B2B SaaS Founders", NOT just "startups")
- "style" (string, e.g. "dark glassmorphic")
- "sections" (array of strings representing UI sections in order)
- "animation_type" (string)
- "demand_score" (float 0-1)
- "tone" (string: "technical", "casual", "enterprise", "bold")
- "cta_style" (string: "conversion-focused", "informational", "social_proof")
- "content_theme" (string: 1-sentence description of the product's core value)
- "unique_selling_point" (string: what makes this product different)"""

        prompt = f"""Synthesize this market intelligence into a Design Brief:

Trends: {json.dumps(trends)}
Designs: {json.dumps(designs)}
Patterns: {json.dumps(patterns)}
Demand: {json.dumps(demand)}

CRITICAL: Be SPECIFIC. Don't say "SaaS Template" — say exactly what KIND of SaaS.
Don't say "modern dark" — describe the EXACT visual identity.
Don't say "startups" — say which KIND of startups.

Return ONLY valid JSON with the required keys."""

        try:
            response = await self.gateway.query(
                prompt=prompt,
                task_type=LLMTaskType.BRIEF_GENERATION,
                system_prompt=system_prompt,
                json_mode=True,
            )

            result = response.get("result")
            provider = response.get("provider_used", "unknown")
            logger.info("Design brief generated via: %s", provider)

            if isinstance(result, dict):
                # Preserve demand score from explicit calculations
                if "demand_score" not in result:
                    result["demand_score"] = demand.get("demand_score", 0.85)

                # Ensure semantic intent fields exist (Fix #9)
                result.setdefault("tone", self._infer_tone(result))
                result.setdefault("cta_style", "conversion-focused")
                result.setdefault("content_theme", self._infer_content_theme(result))
                result.setdefault("unique_selling_point", "")

                result["_llm_provider"] = provider
                result["_llama_draft"] = response.get("llama_draft")
                return result

            # Fallback if result isn't a dict
            return self._fallback(demand, patterns, provider)

        except Exception as e:
            logger.error("Design brief generation failed: %s", e)
            return self._fallback(demand, patterns, f"error: {e}")

    def _fallback(self, demand, patterns, provider_info="fallback"):
        return {
            "product_type": f"{demand.get('template_type', 'AI SaaS')} Template",
            "target_market": "AI-first startups and SaaS founders",
            "style": "modern dark gradient",
            "sections": patterns.get("structure", ["hero", "features", "pricing", "testimonials"]),
            "animation_type": "scroll reveal",
            "demand_score": demand.get("demand_score", 0.85),
            "tone": "technical",
            "cta_style": "conversion-focused",
            "content_theme": "Build faster with AI-powered tools",
            "unique_selling_point": "Market intelligence driven design",
            "_llm_provider": provider_info,
        }

    def _infer_tone(self, brief: dict) -> str:
        """Infer tone from product type and target market."""
        pt = (brief.get("product_type", "") + " " + brief.get("target_market", "")).lower()
        if any(kw in pt for kw in ("enterprise", "b2b", "corporate")):
            return "enterprise"
        if any(kw in pt for kw in ("developer", "api", "sdk", "code")):
            return "technical"
        if any(kw in pt for kw in ("creator", "social", "community")):
            return "casual"
        return "bold"

    def _infer_content_theme(self, brief: dict) -> str:
        """Generate a content theme from brief context."""
        pt = brief.get("product_type", "SaaS Platform")
        tm = brief.get("target_market", "tech teams")
        return f"The next-generation {pt} built for {tm}"
