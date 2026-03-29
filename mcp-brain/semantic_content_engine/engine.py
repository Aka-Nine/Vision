"""
Semantic Content Engine — Phase 2.5 (Core Processor)
═══════════════════════════════════════════════════════
The central orchestrator that converts raw scraped data
into structured, UI-ready semantic briefs.

Pipeline:
  deep_analysis.json
        ↓
  Section Mapper (normalize types)
        ↓
  Content Fuser (merge multi-source data)
        ↓
  Content Ranker (score + select best)
        ↓
  Intent Engine (assign meaning)
        ↓
  semantic_brief.json
"""

import glob
import json
import os
import logging
from typing import Optional

from semantic_content_engine.section_mapper import SectionMapper
from semantic_content_engine.content_ranker import ContentRanker
from semantic_content_engine.content_fuser import ContentFuser
from semantic_content_engine.intent_engine import IntentInferenceEngine

logger = logging.getLogger(__name__)

# ── Minimum acceptable confidence ──────────────────────────────────
MIN_SECTION_CONFIDENCE = 0.5
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")


class SemanticContentEngine:
    """
    Core processor for Phase 2.5.
    Transforms raw deep analysis + market data into
    context-aware, UI-ready structured content.
    """

    def __init__(self):
        self.section_mapper = SectionMapper()
        self.content_ranker = ContentRanker()
        self.content_fuser = ContentFuser()
        self.intent_engine = IntentInferenceEngine()

    async def process(
        self,
        deep_analysis: Optional[dict] = None,
        trend_data: Optional[dict] = None,
        brief_data: Optional[dict] = None,
    ) -> dict:
        """
        Main entry point. Processes raw data into a semantic brief.

        Parameters
        ----------
        deep_analysis : dict, optional
            Raw deep analysis JSON (from phase 2 scraping).
            If None, loads the latest from storage.
        trend_data : dict, optional
            Trend/market signals.
        brief_data : dict, optional
            LLM-generated design brief.

        Returns
        -------
        dict — Semantic brief ready for Phase 3 template generator.
        """
        logger.info("═══ Phase 2.5: Semantic Content Engine — Processing ═══")

        # ── Step 1: Load deep analysis if not provided ──────────────
        if deep_analysis is None:
            deep_analysis = self._load_latest_deep_analysis()

        if not deep_analysis or "sections" not in deep_analysis:
            logger.warning("No deep analysis data available. Generating minimal semantic brief.")
            return self._generate_fallback_brief(brief_data)

        raw_sections = deep_analysis.get("sections", [])
        logger.info("Processing %d raw sections from deep analysis", len(raw_sections))

        # ── Step 2: Normalize section types ─────────────────────────
        normalized = self._normalize_sections(raw_sections)
        logger.info("Normalized to %d unique semantic sections (after filtering decorative)", len(normalized))

        # ── Step 3: Fuse multi-source content ───────────────────────
        fused = self.content_fuser.fuse_sections(normalized, trend_data, brief_data)

        # ── Step 4: Score and select best content per section ───────
        semantic_sections = self._rank_and_select(fused)

        # ── Step 5: Assign intent ───────────────────────────────────
        for section in semantic_sections:
            section["intent"] = self.intent_engine.infer(
                section["type"], section.get("content", {})
            )
            # Validate that content matches intent
            is_valid, missing = self.intent_engine.validate_content_for_intent(
                section["intent"], section.get("content", {})
            )
            if not is_valid:
                logger.debug(
                    "Section '%s' missing elements for intent '%s': %s",
                    section["type"], section["intent"], missing,
                )

        # ── Step 6: Deduplicate sections ────────────────────────────
        semantic_sections = self._deduplicate_sections(semantic_sections)

        # ── Step 7: Assemble final brief ────────────────────────────
        semantic_brief = self._assemble_brief(
            semantic_sections, deep_analysis, trend_data, brief_data
        )

        # ── Step 8: Validate output ─────────────────────────────────
        validation = self._validate_brief(semantic_brief)
        semantic_brief["_validation"] = validation

        if not validation["is_valid"]:
            logger.warning(
                "Semantic brief validation issues: %s",
                validation["issues"],
            )

        # ── Step 9: Save to storage ─────────────────────────────────
        self._save_brief(semantic_brief)

        logger.info(
            "═══ Phase 2.5 Complete: %d sections, avg confidence %.2f ═══",
            len(semantic_sections),
            semantic_brief.get("_stats", {}).get("avg_confidence", 0),
        )

        return semantic_brief

    # ── Step 2: Normalize ───────────────────────────────────────────

    def _normalize_sections(self, raw_sections: list[dict]) -> list[dict]:
        """Normalize section types and filter out decorative elements."""
        normalized = []

        for section in raw_sections:
            # Derive raw type from classes or component_type
            raw_type = self._get_raw_type(section)
            canonical = self.section_mapper.normalize(raw_type)

            # Skip decorative sections (particles, backdrops, etc.)
            if self.section_mapper.should_filter(canonical):
                logger.debug("Filtered decorative section: %s", raw_type)
                continue

            section["_original_type"] = raw_type
            section["type"] = canonical
            normalized.append(section)

        return normalized

    def _get_raw_type(self, section: dict) -> str:
        """Extract the best raw type identifier from a section."""
        # Prefer CSS class names (more specific)
        classes = section.get("classes", [])
        if classes:
            # Use the first meaningful class
            for cls in classes:
                if cls and not cls.startswith("ng-") and len(cls) > 3:
                    return cls

        # Fall back to component_type or tag
        return section.get("component_type", section.get("tag", "section"))

    # ── Step 4: Rank and select ─────────────────────────────────────

    def _rank_and_select(self, fused_sections: list[dict]) -> list[dict]:
        """Score all content candidates and pick the best for each section."""
        result = []

        for section in fused_sections:
            pool = section.get("_content_pool", {})
            intent = self.section_mapper.get_intent(section["type"])

            # ── Select best heading ─────────────────────────────────
            heading_candidates = []
            for h in pool.get("headings", []):
                score = self.content_ranker.score_heading(h["text"], intent)
                heading_candidates.append({**h, "score": score})

            # Also score the section's direct heading
            direct_heading = section.get("heading")
            if direct_heading and not any(
                h["text"] == direct_heading for h in heading_candidates
            ):
                score = self.content_ranker.score_heading(direct_heading, intent)
                heading_candidates.append({
                    "text": direct_heading,
                    "source": "deep_analysis",
                    "trust": 0.95,
                    "score": score,
                })

            best_heading = self.content_ranker.select_best(heading_candidates)

            # ── Select best description ─────────────────────────────
            desc_candidates = []
            for d in pool.get("descriptions", []):
                score = self.content_ranker.score_description(d["text"], intent)
                desc_candidates.append({**d, "score": score})

            direct_desc = section.get("description")
            if direct_desc and not any(
                d["text"] == direct_desc for d in desc_candidates
            ):
                score = self.content_ranker.score_description(direct_desc, intent)
                desc_candidates.append({
                    "text": direct_desc,
                    "source": "deep_analysis",
                    "trust": 0.95,
                    "score": score,
                })

            best_desc = self.content_ranker.select_best(desc_candidates)

            # ── Select best CTAs ────────────────────────────────────
            cta_candidates = []
            for c in pool.get("ctas", []):
                score = self.content_ranker.score_cta(c["text"], intent)
                if score > 0:  # Filter out zero-scored CTAs (icons, etc.)
                    cta_candidates.append({**c, "score": score})

            ranked_ctas = self.content_ranker.rank_all(cta_candidates)
            best_ctas = [c["text"] for c in ranked_ctas[:3]]  # Max 3 CTAs

            # ── Calculate section confidence ────────────────────────
            scores = []
            if best_heading:
                scores.append(best_heading.get("score", 0))
            if best_desc:
                scores.append(best_desc.get("score", 0))
            if ranked_ctas:
                scores.append(ranked_ctas[0].get("score", 0))

            confidence = round(sum(scores) / max(len(scores), 1), 3)

            # ── Determine primary source ────────────────────────────
            source_priority = ["deep_analysis", "screenshot_to_code", "trend_analysis", "market_brief"]
            primary_source = "fallback"
            for src in source_priority:
                if best_heading and best_heading.get("source") == src:
                    primary_source = src
                    break
                if best_desc and best_desc.get("source") == src:
                    primary_source = src
                    break

            result.append({
                "type": section["type"],
                "intent": self.section_mapper.get_intent(section["type"]),
                "content": {
                    "heading": best_heading["text"] if best_heading else None,
                    "subtext": best_desc["text"] if best_desc else None,
                    "cta": best_ctas[0] if best_ctas else None,
                    "cta_secondary": best_ctas[1] if len(best_ctas) > 1 else None,
                    "cta_texts": best_ctas,
                },
                "meta": {
                    "confidence": confidence,
                    "source": primary_source,
                    "heading_score": best_heading.get("score", 0) if best_heading else 0,
                    "description_score": best_desc.get("score", 0) if best_desc else 0,
                    "cta_count": len(best_ctas),
                    "source_count": section.get("_source_count", 1),
                },
                # Preserve layout metadata
                "_bounding_box": section.get("bounding_box"),
                "_scroll_y": section.get("scroll_y"),
                "_classes": section.get("classes", []),
            })

        return result

    # ── Step 6: Deduplicate ─────────────────────────────────────────

    def _deduplicate_sections(self, sections: list[dict]) -> list[dict]:
        """Remove duplicate sections (same type + similar content)."""
        seen = {}
        deduped = []

        for section in sections:
            key = section["type"]
            heading = (section.get("content", {}).get("heading") or "").lower().strip()

            if key in seen:
                existing = seen[key]
                existing_heading = (existing.get("content", {}).get("heading") or "").lower().strip()

                # Keep the one with higher confidence
                if section["meta"]["confidence"] > existing["meta"]["confidence"]:
                    # Replace existing
                    deduped = [s for s in deduped if s["type"] != key]
                    deduped.append(section)
                    seen[key] = section
                    logger.debug("Dedup: replaced '%s' with higher-confidence version", key)
                elif heading and heading != existing_heading:
                    # Different heading — might be a genuinely different section
                    # Append with a numeric suffix
                    section["type"] = f"{key}_alt"
                    deduped.append(section)
                else:
                    logger.debug("Dedup: skipped duplicate '%s'", key)
            else:
                seen[key] = section
                deduped.append(section)

        if len(deduped) < len(sections):
            logger.info(
                "Deduplication: %d → %d sections",
                len(sections), len(deduped),
            )

        return deduped

    # ── Step 7: Assemble brief ──────────────────────────────────────

    def _assemble_brief(
        self,
        sections: list[dict],
        deep_analysis: dict,
        trend_data: Optional[dict],
        brief_data: Optional[dict],
    ) -> dict:
        """Assemble the final semantic brief."""
        # Calculate aggregate stats
        confidences = [s["meta"]["confidence"] for s in sections]
        avg_confidence = round(sum(confidences) / max(len(confidences), 1), 3)

        return {
            "sections": sections,
            "source_metadata": {
                "url": deep_analysis.get("url"),
                "title": deep_analysis.get("title"),
                "meta_description": deep_analysis.get("meta_description"),
            },
            "design_tokens": {
                "fonts": deep_analysis.get("fonts", []),
                "colors": deep_analysis.get("colors", []),
                "animations": deep_analysis.get("animations", []),
            },
            "market_context": {
                "trends": (trend_data or {}).get("trends", []),
                "product_type": (brief_data or {}).get("product_type"),
                "target_market": (brief_data or {}).get("target_market"),
                "demand_score": (brief_data or {}).get("demand_score"),
                "style": (brief_data or {}).get("style"),
            },
            "_stats": {
                "total_sections": len(sections),
                "avg_confidence": avg_confidence,
                "sections_above_threshold": sum(
                    1 for c in confidences if c >= MIN_SECTION_CONFIDENCE
                ),
                "sections_below_threshold": sum(
                    1 for c in confidences if c < MIN_SECTION_CONFIDENCE
                ),
            },
        }

    # ── Step 8: Validate ────────────────────────────────────────────

    def _validate_brief(self, brief: dict) -> dict:
        """Validate the semantic brief for quality and completeness."""
        issues = []
        sections = brief.get("sections", [])

        # Check: at least 1 section exists
        if not sections:
            issues.append("CRITICAL: No sections in semantic brief")

        # Check: hero section has a real heading
        hero_sections = [s for s in sections if s["type"] == "hero"]
        if hero_sections:
            hero = hero_sections[0]
            if not hero.get("content", {}).get("heading"):
                issues.append("WARNING: Hero section has no heading")
            if hero["meta"]["confidence"] < MIN_SECTION_CONFIDENCE:
                issues.append(
                    f"WARNING: Hero confidence too low ({hero['meta']['confidence']:.2f})"
                )
        else:
            issues.append("NOTE: No hero section found")

        # Check: no content duplication across sections
        headings = [
            s.get("content", {}).get("heading", "").lower()
            for s in sections
            if s.get("content", {}).get("heading")
        ]
        if len(headings) != len(set(headings)):
            issues.append("WARNING: Duplicate headings detected across sections")

        # Check: avg confidence meets threshold
        avg_conf = brief.get("_stats", {}).get("avg_confidence", 0)
        if avg_conf < MIN_SECTION_CONFIDENCE:
            issues.append(
                f"WARNING: Average confidence below threshold ({avg_conf:.2f} < {MIN_SECTION_CONFIDENCE})"
            )

        return {
            "is_valid": not any(i.startswith("CRITICAL") for i in issues),
            "issues": issues,
            "section_count": len(sections),
            "avg_confidence": avg_conf,
        }

    # ── Fallback ────────────────────────────────────────────────────

    def _generate_fallback_brief(self, brief_data: Optional[dict]) -> dict:
        """Generate a minimal semantic brief when no deep analysis is available."""
        product_type = (brief_data or {}).get("product_type", "SaaS Landing Page")
        target_market = (brief_data or {}).get("target_market", "Tech startups")

        fallback_sections = [
            {
                "type": "hero",
                "intent": "primary_value_proposition",
                "content": {
                    "heading": f"Build with {product_type}",
                    "subtext": f"The next-generation platform built for {target_market}.",
                    "cta": "Get Started",
                    "cta_secondary": "Learn More",
                    "cta_texts": ["Get Started", "Learn More"],
                },
                "meta": {
                    "confidence": 0.4,
                    "source": "fallback",
                    "heading_score": 0.4,
                    "description_score": 0.4,
                    "cta_count": 2,
                    "source_count": 0,
                },
            },
            {
                "type": "features",
                "intent": "capability_highlight",
                "content": {
                    "heading": "Powerful Features",
                    "subtext": None,
                    "cta": None,
                    "cta_secondary": None,
                    "cta_texts": [],
                },
                "meta": {
                    "confidence": 0.3,
                    "source": "fallback",
                    "heading_score": 0.3,
                    "description_score": 0,
                    "cta_count": 0,
                    "source_count": 0,
                },
            },
        ]

        return {
            "sections": fallback_sections,
            "source_metadata": {"url": None, "title": None},
            "design_tokens": {"fonts": [], "colors": [], "animations": []},
            "market_context": {
                "product_type": product_type,
                "target_market": target_market,
            },
            "_stats": {
                "total_sections": len(fallback_sections),
                "avg_confidence": 0.35,
                "sections_above_threshold": 0,
                "sections_below_threshold": len(fallback_sections),
            },
            "_is_fallback": True,
        }

    # ── Storage helpers ─────────────────────────────────────────────

    def _load_latest_deep_analysis(self) -> Optional[dict]:
        """Load the most recent deep analysis file from storage."""
        pattern = os.path.join(STORAGE_DIR, "deep_analysis", "**", "*_analysis.json")
        files = sorted(glob.glob(pattern, recursive=True))

        if not files:
            logger.warning("No deep analysis files found in storage.")
            return None

        latest = files[-1]
        logger.info("Loading deep analysis: %s", latest)

        try:
            with open(latest, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "sections" in data and len(data["sections"]) > 0:
                return data
            logger.warning("Deep analysis file has no sections: %s", latest)
            return None
        except Exception as e:
            logger.error("Failed to load deep analysis: %s", e)
            return None

    def _save_brief(self, brief: dict):
        """Save the semantic brief to storage."""
        output_dir = os.path.join(STORAGE_DIR, "semantic_briefs")
        os.makedirs(output_dir, exist_ok=True)

        import time
        filename = f"semantic_brief_{int(time.time())}.json"
        path = os.path.join(output_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, default=str)

        logger.info("Semantic brief saved → %s", path)
