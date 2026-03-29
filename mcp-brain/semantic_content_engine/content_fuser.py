"""
Content Fuser — Phase 2.5 (Multi-Source Intelligence)
═════════════════════════════════════════════════════
Merges data from multiple intelligence sources:
  • Deep site scraping (sections, headings, CTAs)
  • Trend analysis (Reddit/HN popularity signals)
  • Market briefs (LLM-synthesized data)
  • Screenshot-to-code insights (future)

Produces a unified content pool for each section.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Source trust weights ────────────────────────────────────────────
SOURCE_TRUST = {
    "deep_analysis": 0.95,       # Direct scraping = highest trust
    "screenshot_to_code": 0.85,  # Visual AI analysis
    "trend_analysis": 0.70,      # Indirect signals
    "market_brief": 0.60,        # LLM-synthesized
    "fallback": 0.30,            # Generic defaults
}


class ContentFuser:
    """Merge content from multiple intelligence sources."""

    def fuse_sections(
        self,
        deep_sections: list[dict],
        trend_data: Optional[dict] = None,
        brief_data: Optional[dict] = None,
    ) -> list[dict]:
        """
        Merge deep analysis sections with trend and brief data.

        Parameters
        ----------
        deep_sections : list[dict]
            Sections extracted from deep site scraping.
        trend_data : dict, optional
            Trend/popularity signals from HN, Reddit, etc.
        brief_data : dict, optional
            LLM-generated design brief data.

        Returns
        -------
        list[dict] — Enriched sections with multi-source content pools.
        """
        enriched = []

        for section in deep_sections:
            content_pool = {
                "headings": [],
                "descriptions": [],
                "ctas": [],
            }

            # ── Source 1: Deep Analysis (primary) ───────────────────
            heading = section.get("heading")
            if heading and heading.strip():
                content_pool["headings"].append({
                    "text": heading.strip(),
                    "source": "deep_analysis",
                    "trust": SOURCE_TRUST["deep_analysis"],
                })

            desc = section.get("description")
            if desc and desc.strip():
                content_pool["descriptions"].append({
                    "text": desc.strip(),
                    "source": "deep_analysis",
                    "trust": SOURCE_TRUST["deep_analysis"],
                })

            for cta in section.get("cta_texts", []):
                if cta and cta.strip():
                    content_pool["ctas"].append({
                        "text": cta.strip(),
                        "source": "deep_analysis",
                        "trust": SOURCE_TRUST["deep_analysis"],
                    })

            # ── Source 2: Trend Data (secondary boost) ──────────────
            if trend_data:
                self._inject_trend_signals(content_pool, trend_data, section)

            # ── Source 3: Brief Data (LLM-synthesized fallback) ─────
            if brief_data:
                self._inject_brief_data(content_pool, brief_data, section)

            enriched.append({
                **section,
                "_content_pool": content_pool,
                "_source_count": self._count_sources(content_pool),
            })

        logger.info(
            "Fused %d sections from %d sources",
            len(enriched),
            len(set(s for sec in enriched for pool in sec.get("_content_pool", {}).values()
                     for item in pool for s in [item.get("source", "")])),
        )
        return enriched

    def _inject_trend_signals(self, pool: dict, trend_data: dict, section: dict):
        """Enrich with context from trend analysis."""
        # Extract product/brand context from trend titles
        trends = trend_data.get("trends", [])
        if not trends:
            return

        # Use the most popular trend as context
        top_trend = max(trends, key=lambda t: t.get("popularity_score", 0), default=None)
        if not top_trend:
            return

        trend_name = top_trend.get("trend", "")
        if trend_name and "UI for:" in trend_name:
            product_name = trend_name.replace("UI for:", "").strip()
            # Add product context as a low-score heading candidate
            # (will be used if deep analysis has no heading)
            pool["headings"].append({
                "text": product_name,
                "source": "trend_analysis",
                "trust": SOURCE_TRUST["trend_analysis"],
            })

    def _inject_brief_data(self, pool: dict, brief_data: dict, section: dict):
        """Inject LLM-generated brief content as fallback candidates."""
        # The brief contains high-level product/market info
        product_type = brief_data.get("product_type", "")
        target_market = brief_data.get("target_market", "")

        if product_type and not pool["headings"]:
            pool["headings"].append({
                "text": f"{product_type} for {target_market}",
                "source": "market_brief",
                "trust": SOURCE_TRUST["market_brief"],
            })

    def _count_sources(self, pool: dict) -> int:
        """Count unique sources across all content in the pool."""
        sources = set()
        for key in ["headings", "descriptions", "ctas"]:
            for item in pool.get(key, []):
                sources.add(item.get("source", "unknown"))
        return len(sources)
