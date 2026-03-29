"""
Section Mapper — Phase 2.5 (Normalization Layer)
═════════════════════════════════════════════════
Standardises inconsistent section types from deep analysis
into canonical, UI-ready identifiers.

Example:
    hero_banner  → hero
    top_section  → hero
    feature_grid → features
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Comprehensive alias map ─────────────────────────────────────────
SECTION_ALIASES: dict[str, str] = {
    # Hero variants
    "hero": "hero",
    "hero_banner": "hero",
    "hero_section": "hero",
    "herosection": "hero",
    "top_section": "hero",
    "welcome_wrapper": "hero",
    "welcome_section": "hero",
    "landing_hero": "hero",
    "main_hero": "hero",
    "banner": "hero",
    "splash": "hero",
    "jumbotron": "hero",

    # Features variants
    "features": "features",
    "feature_grid": "features",
    "featuregrid": "features",
    "feature_explorer": "features",
    "feature_explorer_section": "features",
    "features_overview": "features",
    "capabilities": "features",
    "feature_cards": "features",

    # Video / Media variants
    "video": "video",
    "video_section": "video",
    "landing_video_section": "video",
    "video_showcase": "video",
    "product_video": "video",
    "media_showcase": "video",
    "demo_video": "video",

    # Use Cases / Carousel
    "use_cases": "use_cases",
    "use_cases_carousel": "use_cases",
    "landing_use_case_section": "use_cases",
    "case_studies": "use_cases",
    "showcase": "use_cases",

    # Pricing / Solutions
    "pricing": "pricing",
    "pricing_card": "pricing",
    "pricingcard": "pricing",
    "try_solutions_section": "pricing",
    "solutions": "pricing",
    "plans": "pricing",

    # CTA variants
    "cta": "cta",
    "cta_button": "cta",
    "ctabutton": "cta",
    "download_section": "cta",
    "download_section_container": "cta",
    "call_to_action": "cta",

    # Blog
    "blog": "blog",
    "latest_blogs": "blog",
    "landing_latest_blogs": "blog",
    "blog_section": "blog",
    "news": "blog",
    "articles": "blog",

    # About / Agent sections
    "about": "about",
    "about_section": "about",
    "agent_first_section": "about",
    "agent_first": "about",
    "introduction": "about",
    "mission": "about",

    # Testimonials
    "testimonials": "testimonials",
    "testimonial_card": "testimonials",
    "reviews": "testimonials",
    "social_proof": "testimonials",

    # Footer
    "footer": "footer",
    "footer_nav_section": "footer",
    "footer_navigation": "footer",
    "site_footer": "footer",

    # Navigation
    "navbar": "navbar",
    "nav": "navbar",
    "navigation": "navbar",
    "header": "header",

    # Particles / Decorative (filtered out)
    "particles": "_decorative",
    "main_particles_component_section": "_decorative",
    "morphing_particles_component_section": "_decorative",
    "backdrop": "_decorative",
    "download_section_backdrop": "_decorative",

    # Other
    "faq": "faq",
    "contact": "contact",
    "dashboard": "dashboard",
    "sidebar": "sidebar",
    "stats": "stats",
    "charts": "charts",
}

# ── Intent assignments per canonical section ────────────────────────
SECTION_INTENTS: dict[str, str] = {
    "hero": "primary_value_proposition",
    "features": "capability_highlight",
    "video": "product_showcase",
    "use_cases": "social_validation",
    "pricing": "conversion",
    "cta": "conversion",
    "blog": "content_marketing",
    "about": "brand_story",
    "testimonials": "social_proof",
    "footer": "navigation",
    "navbar": "navigation",
    "header": "navigation",
    "faq": "objection_handling",
    "contact": "lead_capture",
    "dashboard": "product_demo",
    "stats": "authority_signal",
}


class SectionMapper:
    """Normalize raw section identifiers to canonical types and assign intent."""

    def normalize(self, raw_type: str) -> str:
        """
        Map a raw section type (from CSS classes or scraper) to a canonical key.
        Returns '_decorative' for sections that should be filtered out.
        """
        key = self._slugify(raw_type)
        canonical = SECTION_ALIASES.get(key)

        if canonical:
            return canonical

        # Fuzzy: check if any alias is a substring
        for alias, canon in SECTION_ALIASES.items():
            if alias in key or key in alias:
                return canon

        # Keyword-based fallback
        if "hero" in key or "welcome" in key or "banner" in key:
            return "hero"
        if "feature" in key:
            return "features"
        if "video" in key or "media" in key:
            return "video"
        if "price" in key or "plan" in key or "solution" in key:
            return "pricing"
        if "cta" in key or "download" in key or "action" in key:
            return "cta"
        if "blog" in key or "article" in key or "news" in key:
            return "blog"
        if "footer" in key:
            return "footer"
        if "nav" in key or "header" in key:
            return "navbar"
        if "testimonial" in key or "review" in key:
            return "testimonials"
        if "particle" in key or "backdrop" in key:
            return "_decorative"

        logger.debug("Unknown section type '%s', passing through as-is", raw_type)
        return key

    def get_intent(self, canonical_type: str) -> str:
        """Return the semantic intent for a canonical section type."""
        return SECTION_INTENTS.get(canonical_type, "general_content")

    def should_filter(self, canonical_type: str) -> bool:
        """Return True if the section is purely decorative and should be excluded."""
        return canonical_type == "_decorative"

    @staticmethod
    def _slugify(text: str) -> str:
        return re.sub(r"[^a-z0-9_]", "_", text.lower().strip()).strip("_")
