"""
Brief Quality Scorer — Upgraded
═══════════════════════════════
Now scores ACTIONABILITY, not just presence of fields.
A brief with "dark glassmorphic" style scores higher than "modern".
A brief with 6 specific sections scores higher than 3 generic ones.
"""

import logging

logger = logging.getLogger(__name__)


class BriefQualityScorer:
    """Scores design briefs on quality AND actionability."""

    def score_brief(self, brief: dict) -> dict:
        score = 0.0
        breakdown = {}

        # ── 1. Pattern Clarity (0.25) ──────────────────────────────
        style = brief.get("style", "")
        if style and style != "unknown":
            # More specific styles score higher
            specificity = min(len(style.split()) / 3.0, 1.0)
            style_score = 0.15 + (specificity * 0.10)
            score += style_score
            breakdown["style_clarity"] = round(style_score, 3)
        else:
            breakdown["style_clarity"] = 0.0

        # ── 2. Component Completeness (0.25) ───────────────────────
        sections = brief.get("sections", [])
        if len(sections) >= 5:
            comp_score = 0.25
        elif len(sections) >= 3:
            comp_score = 0.15
        elif len(sections) > 0:
            comp_score = 0.08
        else:
            comp_score = 0.0
        score += comp_score
        breakdown["component_completeness"] = round(comp_score, 3)

        # ── 3. Semantic Intent (0.15) ──────────────────────────────
        intent_score = 0.0
        if brief.get("tone"):
            intent_score += 0.05
        if brief.get("cta_style"):
            intent_score += 0.05
        if brief.get("content_theme"):
            intent_score += 0.05
        score += intent_score
        breakdown["semantic_intent"] = round(intent_score, 3)

        # ── 4. Market Context (0.15) ──────────────────────────────
        context_score = 0.0
        target = brief.get("target_market", "")
        if target and len(target.split()) >= 2:
            context_score += 0.08
        elif target:
            context_score += 0.03

        product_type = brief.get("product_type", "")
        if product_type and len(product_type.split()) >= 2:
            context_score += 0.07
        elif product_type:
            context_score += 0.03
        score += context_score
        breakdown["market_context"] = round(context_score, 3)

        # ── 5. Animation & Interaction (0.1) ──────────────────────
        animation = brief.get("animation_type", "")
        if animation and animation != "none":
            anim_score = 0.1
        else:
            anim_score = 0.0
        score += anim_score
        breakdown["animation"] = round(anim_score, 3)

        # ── 6. Demand Signal Strength (0.1) ───────────────────────
        demand = brief.get("demand_score", 0.0)
        demand_contribution = demand * 0.1
        score += demand_contribution
        breakdown["demand_signal"] = round(demand_contribution, 3)

        # ── Normalize ─────────────────────────────────────────────
        final_score = round(min(score, 1.0), 3)
        brief["quality_score"] = final_score
        brief["_quality_breakdown"] = breakdown

        logger.info(
            "Brief quality scored: %.3f (style=%.3f, sections=%.3f, intent=%.3f, context=%.3f)",
            final_score,
            breakdown.get("style_clarity", 0),
            breakdown.get("component_completeness", 0),
            breakdown.get("semantic_intent", 0),
            breakdown.get("market_context", 0),
        )

        return brief


brief_scorer = BriefQualityScorer()
