"""
Content Ranker — Phase 2.5 (Decision Engine)
═════════════════════════════════════════════
Scores and selects the best content for each section using:
  • Clarity      — Is the text clear and readable?
  • Length       — Does it fall in the ideal range?
  • Keyword      — Does it contain strong, relevant keywords?
  • Relevance    — Does it match the section's intent?
  • Uniqueness   — Is it distinct from other sections?

Prevents weak or noisy content from entering the final UI.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Scoring weights ─────────────────────────────────────────────────
WEIGHTS = {
    "clarity": 0.25,
    "length": 0.15,
    "keyword_strength": 0.25,
    "relevance": 0.20,
    "uniqueness": 0.15,
}

# ── Power keywords by intent ───────────────────────────────────────
INTENT_KEYWORDS: dict[str, list[str]] = {
    "primary_value_proposition": [
        "build", "create", "launch", "experience", "transform",
        "next-gen", "powerful", "fastest", "revolutionary", "liftoff",
        "accelerate", "unleash", "supercharge",
    ],
    "capability_highlight": [
        "feature", "capability", "integration", "automate", "smart",
        "advanced", "intelligent", "built-in", "seamless", "robust",
        "configurable", "real-time",
    ],
    "product_showcase": [
        "demo", "watch", "see", "explore", "discover",
        "preview", "showcase", "in action", "walkthrough",
    ],
    "social_validation": [
        "use case", "case study", "built for", "designed for",
        "trusted by", "used by", "developers", "teams",
    ],
    "conversion": [
        "download", "start", "try", "get", "free", "pricing",
        "plan", "subscribe", "buy", "begin", "available",
    ],
    "social_proof": [
        "testimonial", "review", "said", "love", "amazing",
        "game-changing", "recommend", "trust",
    ],
    "content_marketing": [
        "blog", "article", "read", "learn", "latest",
        "news", "update", "introducing", "announcing",
    ],
    "brand_story": [
        "about", "mission", "vision", "story", "who we are",
        "founded", "team", "belief", "purpose",
    ],
}

# ── Minimum acceptable scores ──────────────────────────────────────
MIN_CONFIDENCE = 0.3


class ContentRanker:
    """Score and select the best content for each section."""

    def score_heading(self, heading: Optional[str], intent: str) -> float:
        """Score a heading on a 0.0–1.0 scale."""
        if not heading or not heading.strip():
            return 0.0

        text = heading.strip()
        scores = {
            "clarity": self._clarity_score(text),
            "length": self._heading_length_score(text),
            "keyword_strength": self._keyword_score(text, intent),
            "relevance": self._relevance_score(text, intent),
            "uniqueness": 0.8,  # Baseline, adjusted during multi-section ranking
        }

        weighted = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
        return round(min(1.0, max(0.0, weighted)), 3)

    def score_description(self, description: Optional[str], intent: str) -> float:
        """Score a description on a 0.0–1.0 scale."""
        if not description or not description.strip():
            return 0.0

        text = description.strip()
        scores = {
            "clarity": self._clarity_score(text),
            "length": self._description_length_score(text),
            "keyword_strength": self._keyword_score(text, intent),
            "relevance": self._relevance_score(text, intent),
            "uniqueness": 0.8,
        }

        weighted = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
        return round(min(1.0, max(0.0, weighted)), 3)

    def score_cta(self, cta: Optional[str], intent: str) -> float:
        """Score a CTA button text on a 0.0–1.0 scale."""
        if not cta or not cta.strip():
            return 0.0

        text = cta.strip()

        # Filter out icon-text CTAs (arrow icons from material design)
        if text.startswith("keyboard_arrow") or len(text) < 2:
            return 0.0

        scores = {
            "clarity": self._clarity_score(text),
            "length": self._cta_length_score(text),
            "keyword_strength": self._keyword_score(text, intent),
            "relevance": self._cta_relevance_score(text, intent),
            "uniqueness": 0.8,
        }

        weighted = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
        return round(min(1.0, max(0.0, weighted)), 3)

    def select_best(self, candidates: list[dict], key: str = "score") -> Optional[dict]:
        """Select the highest-scoring candidate that meets minimum confidence."""
        valid = [c for c in candidates if c.get(key, 0) >= MIN_CONFIDENCE]
        if not valid:
            return candidates[0] if candidates else None
        return max(valid, key=lambda c: c.get(key, 0))

    def rank_all(self, candidates: list[dict], key: str = "score") -> list[dict]:
        """Rank all candidates by score, highest first."""
        return sorted(candidates, key=lambda c: c.get(key, 0), reverse=True)

    # ── Scoring sub-functions ───────────────────────────────────────

    def _clarity_score(self, text: str) -> float:
        """Measure readability. Penalise gibberish, code-like tokens, all-caps."""
        # Penalise very short tokens
        if len(text) < 3:
            return 0.1

        # Penalise code-like patterns (CSS classes, JSON, etc.)
        code_patterns = [r"\{", r"\}", r"\[", r"\]", r"ng-c\d+", r"_ngcontent", r"\\"]
        code_penalty = sum(1 for p in code_patterns if re.search(p, text))
        if code_penalty > 0:
            return max(0.1, 0.5 - code_penalty * 0.15)

        # Penalise ALL CAPS blocks
        words = text.split()
        caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / max(len(words), 1)
        if caps_ratio > 0.5:
            return 0.5

        # Reward well-formed sentences
        has_spaces = " " in text
        has_proper_case = text[0].isupper()
        return 0.6 + (0.2 if has_spaces else 0) + (0.2 if has_proper_case else 0)

    def _heading_length_score(self, text: str) -> float:
        """Ideal heading: 4–12 words."""
        word_count = len(text.split())
        if 4 <= word_count <= 12:
            return 1.0
        if 2 <= word_count < 4:
            return 0.7
        if 12 < word_count <= 20:
            return 0.6
        if word_count == 1:
            return 0.3
        return 0.2  # Too long (>20)

    def _description_length_score(self, text: str) -> float:
        """Ideal description: 10–40 words."""
        word_count = len(text.split())
        if 10 <= word_count <= 40:
            return 1.0
        if 5 <= word_count < 10:
            return 0.7
        if 40 < word_count <= 60:
            return 0.6
        if word_count < 5:
            return 0.3
        return 0.3

    def _cta_length_score(self, text: str) -> float:
        """Ideal CTA: 1–5 words."""
        word_count = len(text.split())
        if 1 <= word_count <= 5:
            return 1.0
        if word_count > 5:
            return 0.5
        return 0.3

    def _keyword_score(self, text: str, intent: str) -> float:
        """Check presence of intent-relevant keywords."""
        keywords = INTENT_KEYWORDS.get(intent, [])
        if not keywords:
            return 0.5  # Neutral if no keywords defined

        text_lower = text.lower()
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits >= 3:
            return 1.0
        if hits >= 2:
            return 0.85
        if hits >= 1:
            return 0.65
        return 0.3

    def _relevance_score(self, text: str, intent: str) -> float:
        """How well does the text match the expected purpose?"""
        # Already partially covered by keyword score;
        # this adds heuristic boosts/penalties
        text_lower = text.lower()

        # Penalise obviously misplaced content
        if intent == "primary_value_proposition" and any(
            w in text_lower for w in ["footer", "copyright", "privacy"]
        ):
            return 0.1

        if intent == "conversion" and len(text.split()) > 15:
            return 0.4  # CTAs should be short

        # Boost for action-oriented hero content
        if intent == "primary_value_proposition" and any(
            w in text_lower for w in ["build", "create", "launch", "experience", "liftoff"]
        ):
            return 1.0

        return 0.6  # Default relevance

    def _cta_relevance_score(self, text: str, intent: str) -> float:
        """Score CTA relevance — penalise navigation-like text."""
        text_lower = text.lower()

        # Filter out navigation-style CTAs
        nav_words = ["blog", "pricing", "docs", "changelog", "press", "releases",
                     "product", "use cases"]
        if text_lower in nav_words:
            return 0.2

        # Boost genuine action CTAs
        action_words = ["download", "start", "try", "get", "explore", "view",
                        "begin", "subscribe", "learn more", "sign up", "notify"]
        if any(w in text_lower for w in action_words):
            return 1.0

        return 0.5
