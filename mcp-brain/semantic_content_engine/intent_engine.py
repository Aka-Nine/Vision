"""
Intent Inference Engine — Phase 2.5
════════════════════════════════════
Assigns semantic meaning (intent) to each section and validates
that content matches its assigned purpose.

Example:
    Hero     → Value Proposition
    Features → Capability Highlight
    Pricing  → Conversion
    Video    → Product Showcase
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Intent definitions ──────────────────────────────────────────────
INTENT_DEFINITIONS = {
    "primary_value_proposition": {
        "description": "The main pitch — what the product does and why it matters",
        "expected_elements": ["heading", "subtext", "cta"],
        "heading_style": "bold, action-oriented, 5-10 words",
        "priority": 1,
    },
    "capability_highlight": {
        "description": "Showcase specific features or capabilities",
        "expected_elements": ["heading", "feature_items"],
        "heading_style": "descriptive, benefit-focused",
        "priority": 2,
    },
    "product_showcase": {
        "description": "Visual demonstration of the product in action",
        "expected_elements": ["video", "heading"],
        "heading_style": "short, invitation to explore",
        "priority": 3,
    },
    "social_validation": {
        "description": "Show who uses it and how they benefit",
        "expected_elements": ["heading", "case_items"],
        "heading_style": "community-focused",
        "priority": 4,
    },
    "conversion": {
        "description": "Drive the user to take action (download, buy, sign up)",
        "expected_elements": ["heading", "cta"],
        "heading_style": "urgent, action-oriented",
        "priority": 5,
    },
    "social_proof": {
        "description": "Testimonials, reviews, trust signals",
        "expected_elements": ["heading", "testimonial_items"],
        "heading_style": "trust-building",
        "priority": 6,
    },
    "content_marketing": {
        "description": "Blog posts, articles, thought leadership",
        "expected_elements": ["heading", "article_items"],
        "heading_style": "informational",
        "priority": 7,
    },
    "brand_story": {
        "description": "About section, team, mission, values",
        "expected_elements": ["heading", "description"],
        "heading_style": "personal, authentic",
        "priority": 8,
    },
    "navigation": {
        "description": "Navigation links, site map",
        "expected_elements": ["nav_links"],
        "heading_style": "none",
        "priority": 99,
    },
    "general_content": {
        "description": "Generic content section",
        "expected_elements": ["heading", "description"],
        "heading_style": "standard",
        "priority": 50,
    },
}

# ── Content signals that help refine intent ─────────────────────────
INTENT_SIGNALS = {
    "primary_value_proposition": [
        "experience", "build", "create", "launch", "transform",
        "next-gen", "revolutionary", "liftoff", "welcome",
    ],
    "capability_highlight": [
        "feature", "capability", "explore", "editor", "autocompletion",
        "code", "configurable", "agent",
    ],
    "conversion": [
        "download", "start", "try", "get started", "free",
        "subscribe", "begin", "available", "pricing", "plan",
    ],
    "social_validation": [
        "built for", "trust", "developers", "teams", "era",
        "enterprise", "hobbyist", "professional",
    ],
    "content_marketing": [
        "blog", "introducing", "latest", "read", "article",
        "announcing", "news",
    ],
}


class IntentInferenceEngine:
    """Assign semantic intent to sections based on type and content analysis."""

    def infer(self, canonical_type: str, content: dict) -> str:
        """
        Determine the intent of a section by combining its canonical type
        with content analysis.

        Parameters
        ----------
        canonical_type : str — Normalized section type (from SectionMapper)
        content : dict — Section content (heading, description, ctas)

        Returns
        -------
        str — Intent identifier
        """
        from semantic_content_engine.section_mapper import SECTION_INTENTS

        # Start with the type-based intent
        base_intent = SECTION_INTENTS.get(canonical_type, "general_content")

        # Refine using content analysis
        refined = self._refine_with_content(base_intent, content)

        if refined != base_intent:
            logger.debug(
                "Refined intent: %s → %s (based on content analysis)",
                base_intent, refined,
            )

        return refined

    def get_definition(self, intent: str) -> dict:
        """Return the full intent definition."""
        return INTENT_DEFINITIONS.get(intent, INTENT_DEFINITIONS["general_content"])

    def validate_content_for_intent(self, intent: str, content: dict) -> tuple[bool, list[str]]:
        """
        Check if the content fulfils the requirements for its assigned intent.

        Returns
        -------
        (is_valid, missing_elements)
        """
        defn = self.get_definition(intent)
        expected = defn.get("expected_elements", [])
        missing = []

        for element in expected:
            if element == "heading" and not content.get("heading"):
                missing.append("heading")
            elif element == "subtext" and not content.get("subtext"):
                missing.append("subtext")
            elif element == "cta" and not content.get("cta"):
                missing.append("cta")

        return len(missing) == 0, missing

    def _refine_with_content(self, base_intent: str, content: dict) -> str:
        """Use actual content to refine the initial intent assignment."""
        # Combine all text for signal matching
        all_text = " ".join(filter(None, [
            content.get("heading", ""),
            content.get("description", ""),
            " ".join(content.get("cta_texts", [])),
        ])).lower()

        if not all_text.strip():
            return base_intent

        # Score each possible intent against the content
        best_intent = base_intent
        best_score = 0

        for intent, signals in INTENT_SIGNALS.items():
            score = sum(1 for s in signals if s in all_text)
            if score > best_score:
                best_score = score
                best_intent = intent

        # Only override if we have strong content signals AND the base was generic
        if best_score >= 2 and base_intent == "general_content":
            return best_intent

        return base_intent
