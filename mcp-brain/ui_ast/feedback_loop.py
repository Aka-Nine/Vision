"""
Feedback Loop — Fix #10
════════════════════════
Closes the loop: Output scoring → fed back into the ranking system.

Without this, the pipeline is:
  Scrape → Analyze → Generate → Done ❌

With this:
  Scrape → Analyze → Generate → Score → Feed Back → Improve ✅

Tracks:
  - Generation success/failure rates per pattern
  - AST validation scores over time
  - Which dominant patterns produce the best outputs
  - Content slot fill quality
"""

import json
import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FEEDBACK_STORE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "storage", "feedback"
)


class FeedbackRecord:
    """A single feedback entry for one generation cycle."""

    def __init__(
        self,
        template_id: str,
        ast_validation_score: float = 0.0,
        generation_success: bool = False,
        dominant_pattern: str = "",
        variation_seed: int = 0,
        section_count: int = 0,
        content_fill_rate: float = 0.0,
        build_errors: int = 0,
        generation_time_seconds: float = 0.0,
        demand_score: float = 0.0,
        complexity_tier: str = "",
    ):
        self.template_id = template_id
        self.timestamp = time.time()
        self.ast_validation_score = ast_validation_score
        self.generation_success = generation_success
        self.dominant_pattern = dominant_pattern
        self.variation_seed = variation_seed
        self.section_count = section_count
        self.content_fill_rate = content_fill_rate
        self.build_errors = build_errors
        self.generation_time_seconds = generation_time_seconds
        self.demand_score = demand_score
        self.complexity_tier = complexity_tier

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "timestamp": self.timestamp,
            "ast_validation_score": self.ast_validation_score,
            "generation_success": self.generation_success,
            "dominant_pattern": self.dominant_pattern,
            "variation_seed": self.variation_seed,
            "section_count": self.section_count,
            "content_fill_rate": self.content_fill_rate,
            "build_errors": self.build_errors,
            "generation_time_seconds": self.generation_time_seconds,
            "demand_score": self.demand_score,
            "complexity_tier": self.complexity_tier,
        }


class FeedbackLoop:
    """
    Collects generation outcomes and feeds them back into
    the pattern selection and demand adaptation systems.
    """

    def __init__(self, store_dir: str = FEEDBACK_STORE):
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)
        self._history: list[dict] = []
        self._load_history()

    def record(self, feedback: FeedbackRecord):
        """Record a new feedback entry."""
        entry = feedback.to_dict()
        self._history.append(entry)
        self._save_entry(entry)

        logger.info(
            "Feedback recorded: template=%s success=%s pattern=%s score=%.2f",
            feedback.template_id,
            feedback.generation_success,
            feedback.dominant_pattern,
            feedback.ast_validation_score,
        )

    def get_pattern_success_rates(self) -> dict[str, float]:
        """
        Calculate success rate per dominant pattern.
        Used by pattern_selector to prefer patterns with higher success.
        """
        pattern_stats: dict[str, dict] = {}

        for entry in self._history:
            pattern = entry.get("dominant_pattern", "unknown")
            if pattern not in pattern_stats:
                pattern_stats[pattern] = {"success": 0, "total": 0}

            pattern_stats[pattern]["total"] += 1
            if entry.get("generation_success"):
                pattern_stats[pattern]["success"] += 1

        rates = {}
        for pattern, stats in pattern_stats.items():
            rates[pattern] = (
                round(stats["success"] / max(stats["total"], 1), 3)
            )

        return rates

    def get_avg_validation_score(self, last_n: int = 10) -> float:
        """Get average AST validation score for recent generations."""
        recent = self._history[-last_n:] if self._history else []
        if not recent:
            return 0.0
        scores = [e.get("ast_validation_score", 0) for e in recent]
        return round(sum(scores) / len(scores), 3)

    def get_best_performing_seed(self, pattern: str) -> Optional[int]:
        """Find the variation seed that produced the best output for a pattern."""
        pattern_entries = [
            e for e in self._history
            if e.get("dominant_pattern") == pattern and e.get("generation_success")
        ]
        if not pattern_entries:
            return None

        best = max(pattern_entries, key=lambda e: e.get("ast_validation_score", 0))
        return best.get("variation_seed")

    def get_complexity_tier_performance(self) -> dict[str, dict]:
        """Analyze which complexity tiers succeed most often."""
        tier_stats: dict[str, dict] = {}

        for entry in self._history:
            tier = entry.get("complexity_tier", "unknown")
            if tier not in tier_stats:
                tier_stats[tier] = {
                    "success": 0, "total": 0,
                    "avg_time": 0.0, "avg_errors": 0.0,
                }

            tier_stats[tier]["total"] += 1
            if entry.get("generation_success"):
                tier_stats[tier]["success"] += 1
            tier_stats[tier]["avg_time"] += entry.get("generation_time_seconds", 0)
            tier_stats[tier]["avg_errors"] += entry.get("build_errors", 0)

        # Compute averages
        for tier, stats in tier_stats.items():
            n = max(stats["total"], 1)
            stats["avg_time"] = round(stats["avg_time"] / n, 2)
            stats["avg_errors"] = round(stats["avg_errors"] / n, 2)
            stats["success_rate"] = round(stats["success"] / n, 3)

        return tier_stats

    def should_adjust_complexity(self) -> Optional[str]:
        """
        Based on recent feedback, suggest complexity adjustment.
        Returns "increase", "decrease", or None.
        """
        recent = self._history[-5:] if len(self._history) >= 5 else self._history
        if not recent:
            return None

        recent_success_rate = sum(
            1 for e in recent if e.get("generation_success")
        ) / len(recent)

        avg_errors = sum(e.get("build_errors", 0) for e in recent) / len(recent)

        if recent_success_rate < 0.4 or avg_errors > 3:
            return "decrease"
        elif recent_success_rate > 0.9 and avg_errors < 1:
            return "increase"

        return None

    def get_summary(self) -> dict:
        """Get a summary of all feedback data."""
        total = len(self._history)
        if total == 0:
            return {"total_generations": 0, "overall_success_rate": 0.0}

        successes = sum(1 for e in self._history if e.get("generation_success"))

        return {
            "total_generations": total,
            "overall_success_rate": round(successes / total, 3),
            "avg_validation_score": self.get_avg_validation_score(total),
            "pattern_success_rates": self.get_pattern_success_rates(),
            "tier_performance": self.get_complexity_tier_performance(),
            "suggested_adjustment": self.should_adjust_complexity(),
        }

    # ── Storage ─────────────────────────────────────────────────────

    def _load_history(self):
        """Load feedback history from disk."""
        history_path = os.path.join(self.store_dir, "feedback_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
                logger.info("Loaded %d feedback entries", len(self._history))
            except Exception as e:
                logger.warning("Failed to load feedback history: %s", e)
                self._history = []

    def _save_entry(self, entry: dict):
        """Append a feedback entry to persistent storage."""
        history_path = os.path.join(self.store_dir, "feedback_history.json")
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2)
        except Exception as e:
            logger.error("Failed to save feedback: %s", e)


# Module-level singleton
feedback_loop = FeedbackLoop()
