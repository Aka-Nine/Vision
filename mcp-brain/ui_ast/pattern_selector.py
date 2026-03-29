"""
Dominant Pattern Selector — Fix #4
════════════════════════════════════
Instead of merging ALL extracted patterns (which produces
an "average of everything" generic SaaS page), this module
selects ONE dominant identity and discards the rest.

Without this:
  Input:  5 different patterns from 5 sources
  Output: "safe, boring, generic SaaS landing page"

With this:
  Input:  5 different patterns → 1 dominant selected
  Output: Strong, coherent visual identity
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Known Design Identity Archetypes ────────────────────────────────

IDENTITY_ARCHETYPES = {
    "glass_dashboard": {
        "theme": "dark",
        "glass": True,
        "color_palette": {
            "primary": "#7C3AED",
            "secondary": "#06B6D4",
            "background": "#0F172A",
            "surface": "rgba(255,255,255,0.05)",
            "text_primary": "#FFFFFF",
            "text_secondary": "#94A3B8",
            "accent_gradient_start": "#7C3AED",
            "accent_gradient_end": "#06B6D4",
        },
        "border_radius": "16px",
        "shadow": "0 25px 50px -12px rgba(0,0,0,0.4)",
        "keywords": ["glass", "dashboard", "blur", "transparent", "frost"],
    },
    "ai_saas_dark": {
        "theme": "dark",
        "glass": True,
        "color_palette": {
            "primary": "#6366F1",
            "secondary": "#EC4899",
            "background": "#020617",
            "surface": "rgba(255,255,255,0.03)",
            "text_primary": "#F8FAFC",
            "text_secondary": "#64748B",
            "accent_gradient_start": "#6366F1",
            "accent_gradient_end": "#EC4899",
        },
        "border_radius": "12px",
        "shadow": "0 20px 40px -12px rgba(99,102,241,0.15)",
        "keywords": ["ai", "saas", "dark", "neural", "machine", "automation"],
    },
    "neon_cyberpunk": {
        "theme": "dark",
        "glass": True,
        "color_palette": {
            "primary": "#06B6D4",
            "secondary": "#F97316",
            "background": "#020617",
            "surface": "rgba(6,182,212,0.05)",
            "text_primary": "#FFFFFF",
            "text_secondary": "#67E8F9",
            "accent_gradient_start": "#06B6D4",
            "accent_gradient_end": "#F97316",
        },
        "border_radius": "8px",
        "shadow": "0 0 30px rgba(6,182,212,0.2)",
        "keywords": ["neon", "cyber", "glow", "futuristic", "tech"],
    },
    "clean_modern": {
        "theme": "light",
        "glass": False,
        "color_palette": {
            "primary": "#2563EB",
            "secondary": "#059669",
            "background": "#FFFFFF",
            "surface": "#F8FAFC",
            "text_primary": "#0F172A",
            "text_secondary": "#64748B",
            "accent_gradient_start": "#2563EB",
            "accent_gradient_end": "#7C3AED",
        },
        "border_radius": "12px",
        "shadow": "0 4px 6px -1px rgba(0,0,0,0.1)",
        "keywords": ["clean", "minimal", "modern", "light", "simple", "white"],
    },
    "sports_tech": {
        "theme": "light",
        "glass": False,
        "color_palette": {
            "primary": "#FF5A24",
            "secondary": "#0D0D0D",
            "background": "#F4F4F5",
            "surface": "#FFFFFF",
            "text_primary": "#0D0D0D",
            "text_secondary": "#71717A",
            "accent_gradient_start": "#FF5A24",
            "accent_gradient_end": "#F97316",
        },
        "border_radius": "24px",
        "shadow": "0 1px 3px rgba(0,0,0,0.08)",
        "keywords": ["sport", "fitness", "energy", "bold", "orange", "bento"],
    },
    "enterprise_saas": {
        "theme": "dark",
        "glass": True,
        "color_palette": {
            "primary": "#3B82F6",
            "secondary": "#8B5CF6",
            "background": "#0B1120",
            "surface": "rgba(255,255,255,0.04)",
            "text_primary": "#E2E8F0",
            "text_secondary": "#94A3B8",
            "accent_gradient_start": "#3B82F6",
            "accent_gradient_end": "#8B5CF6",
        },
        "border_radius": "12px",
        "shadow": "0 25px 50px -12px rgba(0,0,0,0.5)",
        "keywords": ["enterprise", "b2b", "platform", "analytics", "data"],
    },
}


class DominantPatternSelector:
    """Selects a single dominant design identity instead of averaging all patterns."""

    def select(
        self,
        patterns: list[dict],
        product_type: str = "",
        style_hint: str = "",
        trend_keywords: list[str] = None,
    ) -> dict:
        """
        Select the dominant pattern from a list of extracted patterns.

        Returns
        -------
        dict with:
          - dominant: str (archetype name)
          - identity: dict (full design identity)
          - discarded: list[str] (rejected archetype names)
          - confidence: float
        """
        if trend_keywords is None:
            trend_keywords = []

        # Combine all signals into a keyword set
        all_keywords = set()
        all_keywords.update(kw.lower() for kw in trend_keywords)
        all_keywords.update(product_type.lower().split())
        all_keywords.update(style_hint.lower().split())

        # Also extract keywords from patterns
        for p in patterns:
            layout_type = p.get("layout_type", "")
            all_keywords.update(layout_type.lower().replace("_", " ").split())
            for s in p.get("structure", []):
                all_keywords.update(s.lower().replace("_", " ").split())

        # Score each archetype
        scores = {}
        for arch_name, arch_data in IDENTITY_ARCHETYPES.items():
            arch_keywords = set(arch_data.get("keywords", []))
            overlap = len(all_keywords & arch_keywords)
            # Bonus for exact product type match
            if arch_name.replace("_", " ") in product_type.lower():
                overlap += 3
            scores[arch_name] = overlap

        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Pick the winner
        if ranked and ranked[0][1] > 0:
            dominant_name = ranked[0][0]
            confidence = min(ranked[0][1] / 5.0, 1.0)
        else:
            # Default to ai_saas_dark if no keywords match
            dominant_name = "ai_saas_dark"
            confidence = 0.3

        dominant_identity = IDENTITY_ARCHETYPES[dominant_name].copy()
        dominant_identity.pop("keywords", None)

        discarded = [name for name, _ in ranked[1:] if scores[name] > 0]

        logger.info(
            "Pattern selection: dominant='%s' (confidence=%.2f), discarded=%s",
            dominant_name, confidence, discarded,
        )

        return {
            "dominant": dominant_name,
            "identity": dominant_identity,
            "discarded": discarded,
            "confidence": confidence,
            "all_scores": dict(ranked),
        }

    def apply_identity_to_tokens(self, identity: dict) -> dict:
        """Convert a selected identity to DesignTokens-compatible dict."""
        return {
            "theme": identity.get("theme", "dark"),
            "color_palette": identity.get("color_palette", {}),
            "border_radius": identity.get("border_radius", "12px"),
            "shadow": identity.get("shadow", ""),
        }
