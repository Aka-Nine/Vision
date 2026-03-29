"""
Demand Adapter — Fix #3
════════════════════════
Uses demand score, trend velocity, and source reputation
to ACTUALLY influence the generated design's complexity,
animation level, and component density.

Without this, the generator ignores market signals and
produces the same UI regardless of demand context.
"""

import logging
from typing import Optional
from ui_ast.schema import DesignTokens

logger = logging.getLogger(__name__)


# ── Complexity Tiers ────────────────────────────────────────────────

COMPLEXITY_TIERS = {
    "minimal": {
        "max_sections": 4,
        "feature_count": 3,
        "animation_type": "fade-in",
        "animation_duration": "0.4s",
        "use_particles": False,
        "use_gradient_mesh": False,
        "use_micro_interactions": False,
        "card_style": "flat",
        "typography_scale": "compact",
    },
    "standard": {
        "max_sections": 6,
        "feature_count": 4,
        "animation_type": "fade-up",
        "animation_duration": "0.6s",
        "use_particles": False,
        "use_gradient_mesh": True,
        "use_micro_interactions": True,
        "card_style": "elevated",
        "typography_scale": "standard",
    },
    "rich": {
        "max_sections": 8,
        "feature_count": 6,
        "animation_type": "scroll-reveal",
        "animation_duration": "0.8s",
        "use_particles": True,
        "use_gradient_mesh": True,
        "use_micro_interactions": True,
        "card_style": "glassmorphic",
        "typography_scale": "large",
    },
    "premium": {
        "max_sections": 12,
        "feature_count": 6,
        "animation_type": "orchestrated",
        "animation_duration": "1.0s",
        "use_particles": True,
        "use_gradient_mesh": True,
        "use_micro_interactions": True,
        "card_style": "glassmorphic-premium",
        "typography_scale": "hero",
    },
}

# ── Typography Scale Presets ────────────────────────────────────────

TYPOGRAPHY_SCALES = {
    "compact": {
        "heading_scale": ["36px", "28px", "22px", "18px"],
        "body_size": "14px",
        "font_weight_heading": "700",
    },
    "standard": {
        "heading_scale": ["48px", "36px", "28px", "22px"],
        "body_size": "16px",
        "font_weight_heading": "800",
    },
    "large": {
        "heading_scale": ["56px", "42px", "32px", "24px"],
        "body_size": "18px",
        "font_weight_heading": "800",
    },
    "hero": {
        "heading_scale": ["72px", "56px", "42px", "28px"],
        "body_size": "18px",
        "font_weight_heading": "900",
    },
}


class DemandAdapter:
    """Translates market demand signals into concrete design constraints."""

    def compute_complexity(
        self,
        demand_score: float = 0.5,
        trend_velocity: float = 0.0,
        competition_score: float = 0.5,
        source_count: int = 1,
    ) -> dict:
        """
        Determine the design complexity tier and specific constraints
        based on market demand signals.

        Parameters
        ----------
        demand_score : float (0-1)
            How much market demand exists for this template type.
        trend_velocity : float
            Rate of trend growth (higher = rising trend).
        competition_score : float (0-1)
            How competitive the market is (higher = more competition).
        source_count : int
            Number of data sources that confirmed this trend.

        Returns
        -------
        dict with 'tier', 'constraints', and 'design_modifiers'
        """
        # ── Calculate composite score ──
        composite = (
            demand_score * 0.4
            + min(trend_velocity / 100, 1.0) * 0.2
            + (1.0 - competition_score) * 0.2  # Less competition = more opportunity
            + min(source_count / 5, 1.0) * 0.2
        )

        # ── Map to complexity tier ──
        if composite >= 0.8:
            tier = "premium"
        elif composite >= 0.6:
            tier = "rich"
        elif composite >= 0.35:
            tier = "standard"
        else:
            tier = "minimal"

        constraints = COMPLEXITY_TIERS[tier].copy()
        typo_scale = TYPOGRAPHY_SCALES[constraints.pop("typography_scale")]

        result = {
            "tier": tier,
            "composite_score": round(composite, 3),
            "constraints": constraints,
            "typography": typo_scale,
            "signals": {
                "demand_score": demand_score,
                "trend_velocity": trend_velocity,
                "competition_score": competition_score,
                "source_count": source_count,
            },
        }

        logger.info(
            "Demand adapter: composite=%.3f → tier=%s (demand=%.2f, velocity=%.1f, competition=%.2f)",
            composite, tier, demand_score, trend_velocity, competition_score,
        )

        return result

    def adapt_design_tokens(
        self,
        base_tokens: DesignTokens,
        complexity: dict,
    ) -> DesignTokens:
        """
        Modify design tokens based on computed complexity.
        Higher demand → richer animations, larger typography, more spacing.
        """
        tier = complexity.get("tier", "standard")
        constraints = complexity.get("constraints", {})
        typo = complexity.get("typography", {})

        # Update animation
        base_tokens.animation["type"] = constraints.get("animation_type", "fade-up")
        base_tokens.animation["duration"] = constraints.get("animation_duration", "0.6s")

        # Update typography scale
        if typo:
            base_tokens.typography["heading_scale"] = typo.get(
                "heading_scale", base_tokens.typography["heading_scale"]
            )
            base_tokens.typography["body_size"] = typo.get(
                "body_size", base_tokens.typography["body_size"]
            )
            base_tokens.typography["font_weight_heading"] = typo.get(
                "font_weight_heading", base_tokens.typography["font_weight_heading"]
            )

        # Adjust spacing for premium tiers
        if tier in ("rich", "premium"):
            base_tokens.spacing["section_padding"] = "100px"
            base_tokens.spacing["gap"] = "32px"
        elif tier == "minimal":
            base_tokens.spacing["section_padding"] = "60px"
            base_tokens.spacing["gap"] = "16px"

        return base_tokens

    def get_section_limits(self, complexity: dict) -> dict:
        """Get limits for section content based on complexity."""
        tier = complexity.get("tier", "standard")
        constraints = complexity.get("constraints", {})

        return {
            "max_sections": constraints.get("max_sections", 6),
            "feature_count": constraints.get("feature_count", 4),
            "max_ctas_per_section": 2 if tier in ("rich", "premium") else 1,
            "use_particles": constraints.get("use_particles", False),
            "use_gradient_mesh": constraints.get("use_gradient_mesh", False),
            "use_micro_interactions": constraints.get("use_micro_interactions", False),
            "card_style": constraints.get("card_style", "elevated"),
        }
