"""
Variation Engine — Fix #7
══════════════════════════
Anti-repetition engine that introduces controlled randomness
to prevent generating the same layout/spacing/arrangement every time.

Even with good briefs, without variation you get:
  - Same layout, same spacing, same component arrangement

This engine provides deterministic-but-varied output using seeds.
"""

import hashlib
import logging
from typing import Optional
from ui_ast.schema import VariationConfig

logger = logging.getLogger(__name__)

# ── Layout Variant Templates ────────────────────────────────────────

LAYOUT_VARIANTS = {
    "left-heavy": {
        "hero_alignment": "left",
        "hero_left_ratio": 0.6,
        "hero_right_ratio": 0.4,
        "feature_style": "alternating",
        "cta_alignment": "left",
    },
    "centered": {
        "hero_alignment": "center",
        "hero_left_ratio": 1.0,
        "hero_right_ratio": 0.0,
        "feature_style": "cards",
        "cta_alignment": "center",
    },
    "split": {
        "hero_alignment": "left",
        "hero_left_ratio": 0.5,
        "hero_right_ratio": 0.5,
        "feature_style": "bento",
        "cta_alignment": "center",
    },
    "offset": {
        "hero_alignment": "offset",
        "hero_left_ratio": 0.55,
        "hero_right_ratio": 0.45,
        "feature_style": "cards",
        "cta_alignment": "right",
    },
    "balanced": {
        "hero_alignment": "center",
        "hero_left_ratio": 0.5,
        "hero_right_ratio": 0.5,
        "feature_style": "cards",
        "cta_alignment": "center",
    },
}

CTA_STYLES = ["single", "dual", "inline", "stacked"]
FEATURE_STYLES = ["cards", "bento", "list", "alternating", "icon-grid"]
PRICING_STYLES = ["columns", "toggle", "comparison", "highlighted-center"]
TESTIMONIAL_STYLES = ["grid", "carousel", "single-spotlight", "masonry"]
ANIMATION_LEVELS = ["none", "subtle", "medium", "rich"]
COLOR_MODES = ["flat", "gradient", "glassmorphic", "neon"]


class VariationEngine:
    """Produces controlled variation configs from seeds and context."""

    def generate(
        self,
        seed: Optional[int] = None,
        product_type: str = "",
        demand_score: float = 0.5,
        source_count: int = 1,
    ) -> VariationConfig:
        """
        Generate a variation config that determines visual/layout style.

        Parameters
        ----------
        seed : int, optional
            Deterministic seed. Same seed → same variation.
            If None, a seed is derived from product_type.
        product_type : str
            Product/template type hint for contextual variation.
        demand_score : float
            Market demand (0-1). Higher demand → richer variation.
        source_count : int
            Number of data sources. More sources → more confidence in bold choices.
        """
        if seed is None:
            seed = self._derive_seed(product_type)

        # Use seed to pick from each variant dimension
        layout_variant = self._pick(list(LAYOUT_VARIANTS.keys()), seed, 0)
        cta_style = self._pick(CTA_STYLES, seed, 1)
        feature_style = self._pick(FEATURE_STYLES, seed, 2)
        pricing_style = self._pick(PRICING_STYLES, seed, 3)
        testimonial_style = self._pick(TESTIMONIAL_STYLES, seed, 4)

        # Animation intensity is demand-driven
        if demand_score > 0.8:
            animation_intensity = "rich"
        elif demand_score > 0.6:
            animation_intensity = "medium"
        elif demand_score > 0.3:
            animation_intensity = "subtle"
        else:
            animation_intensity = "none"

        # Color mode influenced by product type
        color_mode = self._infer_color_mode(product_type, seed)

        # Hero alignment from layout variant
        hero_alignment = LAYOUT_VARIANTS[layout_variant]["hero_alignment"]

        config = VariationConfig(
            variation_seed=seed,
            layout_variant=layout_variant,
            cta_style=cta_style,
            hero_alignment=hero_alignment,
            feature_style=feature_style,
            pricing_style=pricing_style,
            testimonial_style=testimonial_style,
            animation_intensity=animation_intensity,
            color_mode=color_mode,
        )

        logger.info(
            "Variation generated (seed=%d): layout=%s, features=%s, animation=%s, color=%s",
            seed, layout_variant, feature_style, animation_intensity, color_mode,
        )

        return config

    def get_layout_details(self, variant_name: str) -> dict:
        """Get detailed layout parameters for a variant."""
        return LAYOUT_VARIANTS.get(variant_name, LAYOUT_VARIANTS["balanced"])

    def _pick(self, options: list, seed: int, dimension: int) -> str:
        """Deterministically pick from a list using seed + dimension offset."""
        idx = (seed + dimension * 7) % len(options)
        return options[idx]

    def _derive_seed(self, text: str) -> int:
        """Derive a deterministic seed from text."""
        if not text:
            return 42
        h = hashlib.md5(text.encode()).hexdigest()
        return int(h[:8], 16) % 10000

    def _infer_color_mode(self, product_type: str, seed: int) -> str:
        """Infer color mode from product context."""
        pt = product_type.lower()
        if any(kw in pt for kw in ("ai", "ml", "neural", "cyber")):
            return "neon"
        if any(kw in pt for kw in ("glass", "blur", "frost")):
            return "glassmorphic"
        if any(kw in pt for kw in ("minimal", "clean", "light")):
            return "flat"
        # Default based on seed
        return self._pick(COLOR_MODES, seed, 10)
