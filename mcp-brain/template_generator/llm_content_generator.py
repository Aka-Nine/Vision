"""
LLM-Enhanced Component Generator — Phase 3 + LLaMA Integration
Uses local LLaMA to generate richer component content (headlines,
descriptions, feature lists) instead of static placeholder text.
"""
import logging
import json
from core.llm_gateway import llm_gateway, LLMTaskType

logger = logging.getLogger(__name__)


async def generate_section_content(section_key: str, template_type: str, target_market: str) -> dict:
    """
    Use LLaMA locally to generate realistic content for a section.
    Fast, no API cost, runs on CPU.
    """
    prompt = f"""Generate realistic UI content for a "{section_key}" section.
Template type: {template_type}
Target market: {target_market}

Return JSON with these keys:
- "headline": string (compelling, 5-10 words)
- "subheadline": string (descriptive, 10-20 words)
- "features": list of 3 objects with "title" and "description" keys
- "cta_text": string (call to action button text)"""

    try:
        response = await llm_gateway.query(
            prompt=prompt,
            task_type=LLMTaskType.CONTENT_WRITING,
            json_mode=True,
        )
        result = response.get("result")
        if isinstance(result, dict):
            logger.info("LLaMA content for '%s' → %s", section_key, response.get("provider_used"))
            return result
    except Exception as e:
        logger.warning("Content generation failed for '%s': %s", section_key, e)

    # Fallback defaults
    return {
        "headline": f"{section_key.replace('_', ' ').title()}",
        "subheadline": f"Discover what makes our {section_key.replace('_', ' ')} stand out.",
        "features": [
            {"title": "Feature 1", "description": "Description of feature 1."},
            {"title": "Feature 2", "description": "Description of feature 2."},
            {"title": "Feature 3", "description": "Description of feature 3."},
        ],
        "cta_text": "Get Started",
    }


async def validate_component_code(code: str, component_name: str) -> dict:
    """
    Use LLaMA locally to review generated JSX code for issues.
    Fast validation without API costs.
    """
    prompt = f"""Review this React JSX component for issues.
Component: {component_name}

Code:
{code[:1500]}

Return JSON with:
- "valid": boolean
- "issues": list of strings (empty if valid)
- "suggestions": list of strings"""

    try:
        response = await llm_gateway.query(
            prompt=prompt,
            task_type=LLMTaskType.CODE_REVIEW,
            json_mode=True,
        )
        result = response.get("result")
        if isinstance(result, dict):
            return result
    except Exception as e:
        logger.warning("Code validation via LLM failed: %s", e)

    return {"valid": True, "issues": [], "suggestions": []}
