"""
Brief Parser — Phase 3 Module
Reads design briefs produced by Phase 2 and converts them
into structured template specifications for the generator pipeline.
"""

import json
import os
import logging
import re

logger = logging.getLogger(__name__)

# ── Section-name normalisation map ──────────────────────────────────
SECTION_ALIASES = {
    "hero": "hero",
    "herosection": "hero",
    "hero_section": "hero",
    "features": "features",
    "featuregrid": "features",
    "feature_grid": "features",
    "pricing": "pricing",
    "pricingcard": "pricing",
    "pricing_card": "pricing",
    "testimonials": "testimonials",
    "testimonialcard": "testimonials",
    "testimonial_card": "testimonials",
    "cta": "cta",
    "ctabutton": "cta",
    "cta_button": "cta",
    "navbar": "navbar",
    "nav": "navbar",
    "navigation": "navbar",
    "footer": "footer",
    "header": "header",
    "dashboard": "dashboard",
    "sidebar": "sidebar",
    "stats": "stats",
    "charts": "charts",
    "faq": "faq",
    "contact": "contact",
}

# ── Layout heuristic rules ──────────────────────────────────────────
LAYOUT_RULES = {
    "landing_page": ["hero", "features", "pricing", "testimonials", "cta", "footer"],
    "dashboard": ["navbar", "sidebar", "stats", "charts", "footer"],
    "saas_landing": ["hero", "features", "pricing", "testimonials"],
    "portfolio": ["hero", "features", "testimonials", "contact"],
    "ecommerce": ["hero", "features", "pricing", "cta", "footer"],
    "mobile_app": ["header", "dashboard", "features", "footer"],
}

STYLE_PRESETS = {
    "dark glassmorphic": {
        "theme": "dark",
        "glass": True,
        "blur": "lg",
        "border_opacity": 0.1,
        "bg_opacity": 0.4,
        "accent_color": "#7c3aed",
        "surface_color": "#0f172a",
    },
    "modern dark gradient": {
        "theme": "dark",
        "glass": True,
        "blur": "xl",
        "border_opacity": 0.15,
        "bg_opacity": 0.5,
        "accent_color": "#6366f1",
        "surface_color": "#1e1b4b",
    },
    "light minimal": {
        "theme": "light",
        "glass": False,
        "blur": "none",
        "border_opacity": 0.08,
        "bg_opacity": 1.0,
        "accent_color": "#2563eb",
        "surface_color": "#ffffff",
    },
    "neon cyberpunk": {
        "theme": "dark",
        "glass": True,
        "blur": "xl",
        "border_opacity": 0.2,
        "bg_opacity": 0.35,
        "accent_color": "#06b6d4",
        "surface_color": "#020617",
    },
}

ANIMATION_PRESETS = {
    "scroll reveal": {
        "type": "scroll_reveal",
        "library": "framer-motion",
        "default_delay": 0.15,
        "stagger": True,
    },
    "fade in": {
        "type": "fade_in",
        "library": "framer-motion",
        "default_delay": 0.1,
        "stagger": False,
    },
    "slide up": {
        "type": "slide_up",
        "library": "framer-motion",
        "default_delay": 0.12,
        "stagger": True,
    },
}


class BriefParser:
    """Parse a Phase-2 design brief into a structured template specification."""

    def __init__(self):
        self.supported_layouts = list(LAYOUT_RULES.keys())

    # ── Public API ──────────────────────────────────────────────────
    async def parse(self, brief: dict) -> dict:
        """
        Accept a raw design brief dict and return a normalised
        template specification.
        """
        logger.info("Parsing design brief …")

        sections = self._normalise_sections(brief.get("sections", []))
        layout = self._infer_layout(brief, sections)
        style = self._resolve_style(brief.get("style", "dark glassmorphic"))
        animations = self._resolve_animations(brief.get("animation_type", "scroll reveal"))
        metadata = self._extract_metadata(brief)

        spec = {
            "layout": layout,
            "sections": sections,
            "style": style,
            "animations": animations,
            "metadata": metadata,
            "template_type": brief.get("template_type") or brief.get("product_type", "Landing Page"),
            "target_market": brief.get("target_market", "general"),
            "demand_score": brief.get("demand_score", 0.0),
            "raw_brief": brief,
        }

        logger.info(
            "Brief parsed → layout=%s  sections=%d  style=%s",
            spec["layout"],
            len(spec["sections"]),
            style.get("theme", "unknown"),
        )
        return spec

    # ── Internal helpers ────────────────────────────────────────────
    def _normalise_sections(self, raw_sections: list) -> list:
        """Normalise free-form section names to canonical identifiers."""
        normalised = []
        for s in raw_sections:
            key = re.sub(r"[^a-z0-9]", "", s.lower())
            canonical = SECTION_ALIASES.get(key, self._slugify(s))
            if canonical not in normalised:
                normalised.append(canonical)
        return normalised

    def _infer_layout(self, brief: dict, sections: list) -> str:
        """Pick the best matching layout template."""
        # Explicit layout from brief
        explicit = brief.get("layout") or brief.get("layout_type", "")
        for key in LAYOUT_RULES:
            if key in explicit.lower().replace(" ", "_"):
                return key

        # Score each layout by section overlap
        best, best_score = "landing_page", 0
        for layout, expected in LAYOUT_RULES.items():
            score = len(set(sections) & set(expected))
            if score > best_score:
                best, best_score = layout, score
        return best

    def _resolve_style(self, style_hint: str) -> dict:
        """Map a style descriptor to a concrete preset (or build a default)."""
        key = style_hint.lower().strip()
        if key in STYLE_PRESETS:
            return STYLE_PRESETS[key]

        # Fuzzy match
        for preset_key, preset_val in STYLE_PRESETS.items():
            if any(word in key for word in preset_key.split()):
                return preset_val

        # Fallback
        return STYLE_PRESETS["dark glassmorphic"]

    def _resolve_animations(self, anim_hint) -> dict:
        """Resolve animation hint to a preset."""
        if isinstance(anim_hint, list):
            anim_hint = anim_hint[0] if anim_hint else "scroll reveal"
        key = anim_hint.lower().strip() if isinstance(anim_hint, str) else "scroll reveal"
        return ANIMATION_PRESETS.get(key, ANIMATION_PRESETS["scroll reveal"])

    def _extract_metadata(self, brief: dict) -> dict:
        return {
            "provenance": brief.get("provenance", {}),
            "quality_score": brief.get("quality_score", 0.0),
            "error_in_llm": brief.get("error_in_llm"),
        }

    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
        return slug or "section"
