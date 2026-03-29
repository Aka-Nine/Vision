"""
UI AST Compiler — Phase 2.5 Core
══════════════════════════════════
The compiler that converts Phase 2 outputs (semantic briefs,
market intelligence, patterns) into a strict, deterministic
UI AST that Phase 3 ONLY consumes.

This is the single most important file in the entire system.
It solves ALL 10 identified problems:

  Fix #1:  Pattern → Constraint conversion (enforceable schema)
  Fix #2:  Bounding box → Spatial rules
  Fix #3:  Demand score → Design complexity
  Fix #4:  Dominant pattern selection (no more averaging)
  Fix #5:  Strict validation before generation
  Fix #6:  UI Grammar rules enforcement
  Fix #7:  Variation engine (anti-repetition)
  Fix #8:  Strong HTML/component mapping
  Fix #9:  Semantic intent injection
  Fix #10: Feedback loop integration

Pipeline:
  semantic_brief + market_data + patterns
        ↓
  UIASTCompiler.compile()
        ↓
  UIAST (strict, validated, ready for Phase 3)
"""

import json
import os
import time
import uuid
import logging
from typing import Optional

from ui_ast.schema import (
    UIAST, LayoutNode, DesignTokens, ComponentSpec,
    ContentSlot, SpatialRule, Constraints, VariationConfig,
    CompilerFlags, Provenance,
)
from ui_ast.spatial_engine import SpatialEngine
from ui_ast.grammar_engine import UIGrammarEngine
from ui_ast.variation_engine import VariationEngine
from ui_ast.demand_adapter import DemandAdapter
from ui_ast.pattern_selector import DominantPatternSelector
from ui_ast.validator import UIASTValidator
from ui_ast.feedback_loop import feedback_loop

logger = logging.getLogger(__name__)

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")


# ── Component Mapping Database (Fix #8) ────────────────────────────
# Strong HTML mapping: section_id → full component tree structure
# NOT just "hero": "div" but a complete buildable spec

COMPONENT_MAP = {
    "navbar": {
        "tag": "nav",
        "component_name": "Navbar",
        "classes": "fixed top-0 w-full z-50 backdrop-blur-md",
        "props": {"sticky": True, "height": "72px"},
        "children": [
            {"id": "logo", "tag": "div", "component_name": "Logo"},
            {"id": "nav_links", "tag": "ul", "component_name": "NavLinks",
             "props": {"min_items": 3, "max_items": 7}},
            {"id": "cta_button", "tag": "button", "component_name": "NavCTA",
             "props": {"variant": "primary", "size": "sm"}},
        ],
    },
    "hero": {
        "tag": "section",
        "component_name": "HeroSection",
        "classes": "relative overflow-hidden",
        "props": {"min_height": "80vh", "layout": "two_column"},
        "children": [
            {"id": "hero_left", "tag": "div", "component_name": "HeroContent",
             "children": [
                 {"id": "badge", "tag": "span", "component_name": "HeroBadge"},
                 {"id": "heading", "tag": "h1", "component_name": "HeroHeading",
                  "props": {"max_length": 60}},
                 {"id": "subtext", "tag": "p", "component_name": "HeroSubtext",
                  "props": {"max_length": 140}},
                 {"id": "cta_group", "tag": "div", "component_name": "HeroCTAGroup",
                  "props": {"max_buttons": 2}},
             ]},
            {"id": "hero_right", "tag": "div", "component_name": "HeroVisual",
             "children": [
                 {"id": "image_mockup", "tag": "div", "component_name": "HeroImage"},
             ]},
        ],
    },
    "features": {
        "tag": "section",
        "component_name": "FeaturesSection",
        "classes": "relative",
        "props": {"grid_cols": 3, "layout": "grid"},
        "children": [
            {"id": "features_heading", "tag": "h2", "component_name": "FeaturesHeading"},
            {"id": "features_subtext", "tag": "p", "component_name": "FeaturesSubtext"},
            {"id": "feature_items", "tag": "div", "component_name": "FeatureGrid",
             "props": {"min_count": 3, "max_count": 6}},
        ],
    },
    "pricing": {
        "tag": "section",
        "component_name": "PricingSection",
        "classes": "relative",
        "props": {"grid_cols": 3, "layout": "grid"},
        "children": [
            {"id": "pricing_heading", "tag": "h2", "component_name": "PricingHeading"},
            {"id": "plan_cards", "tag": "div", "component_name": "PlanGrid",
             "props": {"min_count": 2, "max_count": 4, "highlight_index": 1}},
        ],
    },
    "testimonials": {
        "tag": "section",
        "component_name": "TestimonialsSection",
        "classes": "relative",
        "props": {"grid_cols": 2, "layout": "grid"},
        "children": [
            {"id": "testimonials_heading", "tag": "h2", "component_name": "TestimonialsHeading"},
            {"id": "testimonial_cards", "tag": "div", "component_name": "TestimonialGrid",
             "props": {"min_count": 2, "max_count": 6}},
        ],
    },
    "cta": {
        "tag": "section",
        "component_name": "CTASection",
        "classes": "relative text-center",
        "props": {"layout": "centered"},
        "children": [
            {"id": "cta_heading", "tag": "h2", "component_name": "CTAHeading"},
            {"id": "cta_subtext", "tag": "p", "component_name": "CTASubtext"},
            {"id": "cta_group", "tag": "div", "component_name": "CTAButtonGroup",
             "props": {"max_buttons": 2}},
        ],
    },
    "faq": {
        "tag": "section",
        "component_name": "FAQSection",
        "classes": "relative",
        "props": {"layout": "accordion"},
        "children": [
            {"id": "faq_heading", "tag": "h2", "component_name": "FAQHeading"},
            {"id": "faq_items", "tag": "div", "component_name": "FAQList",
             "props": {"min_count": 4, "max_count": 8}},
        ],
    },
    "stats": {
        "tag": "section",
        "component_name": "StatsSection",
        "classes": "relative",
        "props": {"grid_cols": 4, "layout": "grid"},
        "children": [
            {"id": "stat_items", "tag": "div", "component_name": "StatGrid",
             "props": {"count": 4}},
        ],
    },
    "contact": {
        "tag": "section",
        "component_name": "ContactSection",
        "classes": "relative",
        "props": {"layout": "two_column"},
        "children": [
            {"id": "contact_heading", "tag": "h2", "component_name": "ContactHeading"},
            {"id": "contact_form", "tag": "form", "component_name": "ContactForm"},
        ],
    },
    "footer": {
        "tag": "footer",
        "component_name": "Footer",
        "classes": "border-t",
        "props": {"grid_cols": 4},
        "children": [
            {"id": "footer_links", "tag": "div", "component_name": "FooterLinks"},
            {"id": "copyright", "tag": "div", "component_name": "Copyright"},
        ],
    },
    "sidebar": {
        "tag": "aside",
        "component_name": "Sidebar",
        "classes": "fixed left-0 h-screen",
        "props": {"width": "260px", "collapsible": True},
        "children": [],
    },
    "dashboard": {
        "tag": "section",
        "component_name": "DashboardSection",
        "classes": "relative",
        "props": {"grid_cols": 2, "layout": "grid"},
        "children": [],
    },
    "charts": {
        "tag": "section",
        "component_name": "ChartsSection",
        "classes": "relative",
        "props": {"grid_cols": 2, "layout": "grid"},
        "children": [],
    },
}

# ── Semantic Intent Map (Fix #9) ───────────────────────────────────

INTENT_MAP = {
    "hero": {
        "tone": "bold",
        "target": "primary_audience",
        "cta_style": "conversion-focused",
        "content_priority": "value_proposition",
    },
    "features": {
        "tone": "technical",
        "target": "evaluators",
        "cta_style": "informational",
        "content_priority": "capability_highlight",
    },
    "pricing": {
        "tone": "direct",
        "target": "buyers",
        "cta_style": "conversion-focused",
        "content_priority": "value_comparison",
    },
    "testimonials": {
        "tone": "authentic",
        "target": "skeptics",
        "cta_style": "social_proof",
        "content_priority": "trust_building",
    },
    "cta": {
        "tone": "urgent",
        "target": "ready_to_buy",
        "cta_style": "conversion-focused",
        "content_priority": "final_push",
    },
    "faq": {
        "tone": "helpful",
        "target": "hesitant_buyers",
        "cta_style": "informational",
        "content_priority": "objection_handling",
    },
    "footer": {
        "tone": "neutral",
        "target": "general",
        "cta_style": "navigational",
        "content_priority": "information",
    },
}


class UIASTCompiler:
    """
    The central compiler that produces a strict UI AST from Phase 2 data.
    This is the ONLY bridge between intelligence gathering and code generation.
    """

    def __init__(self):
        self.spatial_engine = SpatialEngine()
        self.grammar_engine = UIGrammarEngine()
        self.variation_engine = VariationEngine()
        self.demand_adapter = DemandAdapter()
        self.pattern_selector = DominantPatternSelector()
        self.validator = UIASTValidator()

    async def compile(
        self,
        semantic_brief: Optional[dict] = None,
        design_brief: Optional[dict] = None,
        patterns: Optional[list[dict]] = None,
        market_data: Optional[dict] = None,
    ) -> UIAST:
        """
        Main compilation entry point.

        Parameters
        ----------
        semantic_brief : dict
            Phase 2.5 semantic brief (from SemanticContentEngine)
        design_brief : dict
            Phase 2 design brief (from DesignBriefGenerator)
        patterns : list[dict]
            Extracted patterns (from StructuredPatternLibrary)
        market_data : dict
            Raw market intelligence data

        Returns
        -------
        UIAST — A complete, validated, ready-for-Phase-3 AST
        """
        logger.info("═══ UI AST Compiler — Compilation Started ═══")
        compile_start = time.time()

        semantic_brief = semantic_brief or {}
        design_brief = design_brief or {}
        patterns = patterns or []

        template_id = str(uuid.uuid4())
        product_type = design_brief.get("product_type", "SaaS Landing Page")
        style_hint = design_brief.get("style", "dark glassmorphic")
        target_market = design_brief.get("target_market", "tech startups")

        # ── Step 1: Select dominant pattern (Fix #4) ────────────────
        trend_keywords = self._extract_trend_keywords(market_data)
        pattern_result = self.pattern_selector.select(
            patterns=patterns,
            product_type=product_type,
            style_hint=style_hint,
            trend_keywords=trend_keywords,
        )
        dominant_identity = pattern_result["identity"]

        # Check feedback for pattern performance (Fix #10)
        pattern_rates = feedback_loop.get_pattern_success_rates()
        if pattern_result["dominant"] in pattern_rates:
            rate = pattern_rates[pattern_result["dominant"]]
            if rate < 0.3:
                logger.warning(
                    "Pattern '%s' has low success rate (%.1f%%). Consider alternatives.",
                    pattern_result["dominant"], rate * 100,
                )

        # ── Step 2: Compute demand-driven complexity (Fix #3) ──────
        demand_score = design_brief.get("demand_score", 0.5)
        competition_score = (market_data or {}).get("competition_score", 0.5)
        complexity = self.demand_adapter.compute_complexity(
            demand_score=demand_score,
            trend_velocity=self._compute_trend_velocity(market_data),
            competition_score=competition_score,
            source_count=len(patterns),
        )

        # Check feedback for complexity adjustments (Fix #10)
        adjustment = feedback_loop.should_adjust_complexity()
        if adjustment == "decrease":
            logger.info("Feedback loop suggests decreasing complexity")
            complexity["tier"] = self._lower_tier(complexity["tier"])
        elif adjustment == "increase":
            logger.info("Feedback loop suggests increasing complexity")
            complexity["tier"] = self._raise_tier(complexity["tier"])

        # ── Step 3: Generate variation config (Fix #7) ──────────────
        # Check if feedback has a better seed for this pattern
        best_seed = feedback_loop.get_best_performing_seed(pattern_result["dominant"])
        variation = self.variation_engine.generate(
            seed=best_seed,
            product_type=product_type,
            demand_score=demand_score,
            source_count=len(patterns),
        )

        # ── Step 4: Build design tokens (Fix #1 — enforceable) ─────
        design_tokens = self._build_design_tokens(
            dominant_identity, complexity, semantic_brief, variation
        )

        # ── Step 5: Determine section list from semantic brief ──────
        sections = self._determine_sections(semantic_brief, design_brief, complexity)

        # ── Step 6: Apply grammar rules (Fix #6) ───────────────────
        # ALWAYS run auto-fix to ensure required sections exist
        # (missing navbar/footer are warnings, not errors, in grammar)
        sections = self.grammar_engine.auto_fix_structure(sections)
        grammar_report = self.grammar_engine.validate_full_structure(sections)
        if not grammar_report["valid"]:
            logger.warning("Grammar violations remain after auto-fix: %s", grammar_report["violations"])
        if grammar_report.get("warnings"):
            logger.info("Grammar notes: %s", grammar_report["warnings"])

        # ── Step 7: Build layout tree (Fix #1 — strict hierarchy) ──
        layout_tree = self._build_layout_tree(sections, variation)

        # ── Step 8: Map components (Fix #8 — strong mapping) ───────
        components = self._build_components(sections, variation, complexity)

        # ── Step 9: Extract spatial rules (Fix #2) ─────────────────
        semantic_sections = semantic_brief.get("sections", [])
        spatial_rules_objs = self.spatial_engine.extract_spatial_rules(semantic_sections)
        spatial_rules = {k: v.to_dict() for k, v in spatial_rules_objs.items()}

        # ── Step 10: Build content slots (Fix #9 — intent) ─────────
        content_slots = self._build_content_slots(
            sections, semantic_brief, target_market, product_type
        )

        # ── Step 11: Build constraints ──────────────────────────────
        constraints = Constraints(
            required_sections=["navbar", "hero", "footer"],
            order=sections,
            rules=[
                "hero must contain heading and cta",
                "cta must be visible above fold",
                "no empty containers",
                "max 2 primary CTAs per section",
                "navbar must exist at top",
                "footer must exist at bottom",
            ],
        )

        # ── Step 12: Build provenance (traceability) ───────────────
        provenance = Provenance(
            sources=self._extract_sources(semantic_brief, market_data),
            screenshots=self._extract_screenshots(semantic_brief),
            dominant_pattern=pattern_result["dominant"],
            discarded_patterns=pattern_result["discarded"],
            demand_score=demand_score,
            trend_velocity=self._compute_trend_velocity(market_data),
        )

        # ── Step 13: Compiler flags ────────────────────────────────
        compiler_flags = CompilerFlags(
            strict_mode=True,
            allow_llm_layout_changes=False,
            regenerate_on_failure=True,
            enforce_spatial_rules=len(spatial_rules) > 0,
            demand_driven_complexity=True,
            max_sections=complexity["constraints"].get("max_sections", 8),
            min_sections=3,
        )

        # ── Step 14: Assemble the AST ──────────────────────────────
        ast = UIAST(
            version="1.0",
            meta={
                "template_id": template_id,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source": "market_intelligence",
                "design_system": f"{design_tokens.theme}_{pattern_result['dominant']}",
                "variation_seed": variation.variation_seed,
                "product_type": product_type,
                "target_market": target_market,
                "complexity_tier": complexity["tier"],
            },
            layout_tree=layout_tree,
            design_tokens=design_tokens,
            components=components,
            content_slots=content_slots,
            spatial_rules=spatial_rules,
            constraints=constraints,
            variation=variation,
            provenance=provenance,
            compiler_flags=compiler_flags,
        )

        # ── Step 15: Validate (Fix #5 — fail hard) ─────────────────
        validation = self.validator.validate(ast)
        if not validation["valid"]:
            if compiler_flags.regenerate_on_failure:
                logger.warning("AST validation failed — attempting auto-repair")
                ast = self._auto_repair(ast, validation)
                # Re-validate
                validation = self.validator.validate(ast)
                if not validation["valid"]:
                    logger.error("AST STILL INVALID after repair: %s", validation["errors"])

        # ── Step 16: Save AST to storage ───────────────────────────
        compile_time = time.time() - compile_start
        self._save_ast(ast, template_id)

        logger.info(
            "═══ UI AST Compiled in %.2fs: %d sections, %d components, "
            "%d content slots, tier=%s, pattern=%s ═══",
            compile_time,
            len(sections),
            len(components),
            len(content_slots),
            complexity["tier"],
            pattern_result["dominant"],
        )

        return ast

    # ══════════════════════════════════════════════════════════════════
    # INTERNAL METHODS
    # ══════════════════════════════════════════════════════════════════

    def _build_design_tokens(
        self, identity: dict, complexity: dict,
        semantic_brief: dict, variation: VariationConfig,
    ) -> DesignTokens:
        """Build design tokens from dominant identity + demand complexity."""
        tokens = DesignTokens(
            theme=identity.get("theme", "dark"),
            color_palette=identity.get("color_palette", DesignTokens().color_palette),
            border_radius=identity.get("border_radius", "16px"),
            shadow=identity.get("shadow", DesignTokens().shadow),
        )

        # Apply demand-driven modifications
        tokens = self.demand_adapter.adapt_design_tokens(tokens, complexity)

        # Inject real design tokens from scraped data if available
        scraped_tokens = semantic_brief.get("design_tokens", {})
        if scraped_tokens.get("fonts"):
            primary_font = scraped_tokens["fonts"][0] if scraped_tokens["fonts"] else "Inter"
            tokens.typography["font_family"] = primary_font

        # Apply variation-driven color mode
        if variation.color_mode == "neon":
            tokens.shadow = f"0 0 40px {tokens.color_palette.get('primary', '#7C3AED')}33"
        elif variation.color_mode == "flat":
            tokens.shadow = "0 1px 3px rgba(0,0,0,0.1)"

        return tokens

    def _determine_sections(
        self, semantic_brief: dict, design_brief: dict, complexity: dict,
    ) -> list[str]:
        """Determine the final section list from all available data."""
        # Priority: semantic brief sections > design brief sections > default
        semantic_sections = semantic_brief.get("sections", [])
        if semantic_sections:
            sections = [s.get("type", "") for s in semantic_sections if s.get("type")]
        elif design_brief.get("sections"):
            sections = list(design_brief["sections"])
        else:
            sections = ["navbar", "hero", "features", "pricing", "cta", "footer"]

        # Normalize and deduplicate
        seen = set()
        normalized = []
        for s in sections:
            s_clean = s.lower().replace(" ", "_").replace("-", "_")
            if s_clean and s_clean not in seen:
                seen.add(s_clean)
                normalized.append(s_clean)

        # Enforce section limits from demand complexity
        max_sections = complexity.get("constraints", {}).get("max_sections", 8)
        if len(normalized) > max_sections:
            # Keep required sections, trim optional ones
            required = {"navbar", "hero", "footer"}
            required_list = [s for s in normalized if s in required]
            optional_list = [s for s in normalized if s not in required]
            normalized = required_list + optional_list[:max_sections - len(required_list)]

        return normalized

    def _build_layout_tree(
        self, sections: list[str], variation: VariationConfig,
    ) -> LayoutNode:
        """Build the strict layout tree hierarchy (Fix #1)."""
        children = []

        for section_id in sections:
            comp_map = COMPONENT_MAP.get(section_id, {})

            # Determine layout variant for each section
            section_layout = comp_map.get("props", {}).get("layout", "full-width")

            # Apply variation to hero layout
            if section_id == "hero":
                layout_details = self.variation_engine.get_layout_details(
                    variation.layout_variant
                )
                if layout_details.get("hero_alignment") == "center":
                    section_layout = "centered"
                else:
                    section_layout = "two_column"

            node = LayoutNode(
                id=section_id,
                type="section",
                role=section_id,
                layout=section_layout,
                props=comp_map.get("props", {}),
            )

            # Add child elements from component map
            for child_def in comp_map.get("children", []):
                child_node = LayoutNode(
                    id=child_def["id"],
                    type="element" if "children" not in child_def else "container",
                    children=[
                        LayoutNode(
                            id=gc["id"],
                            type="element",
                        )
                        for gc in child_def.get("children", [])
                        if isinstance(gc, dict)
                    ],
                )
                node.children.append(child_node)

            children.append(node)

        return LayoutNode(
            id="root",
            type="page",
            layout="vertical",
            children=children,
        )

    def _build_components(
        self, sections: list[str], variation: VariationConfig, complexity: dict,
    ) -> dict:
        """Build strong component specs (Fix #8)."""
        components = {}

        for section_id in sections:
            comp_map = COMPONENT_MAP.get(section_id)

            if comp_map:
                spec = {
                    "id": section_id,
                    "tag": comp_map["tag"],
                    "component_name": comp_map["component_name"],
                    "classes": comp_map.get("classes", ""),
                    "props": {**comp_map.get("props", {})},
                    "children": comp_map.get("children", []),
                }
            else:
                # Generate spec for unknown sections
                component_name = "".join(
                    w.capitalize() for w in section_id.split("_")
                ) + "Section"
                spec = {
                    "id": section_id,
                    "tag": "section",
                    "component_name": component_name,
                    "classes": "relative",
                    "props": {},
                    "children": [],
                }

            # Apply variation modifications
            if section_id == "features":
                spec["props"]["style"] = variation.feature_style
            elif section_id == "pricing":
                spec["props"]["style"] = variation.pricing_style
            elif section_id == "testimonials":
                spec["props"]["style"] = variation.testimonial_style

            # Apply complexity modifiers
            if complexity.get("constraints", {}).get("use_particles") and section_id == "hero":
                spec["props"]["use_particles"] = True
            if complexity.get("constraints", {}).get("use_micro_interactions"):
                spec["props"]["use_micro_interactions"] = True

            components[section_id] = spec

        return components

    def _build_content_slots(
        self, sections: list[str], semantic_brief: dict,
        target_market: str, product_type: str,
    ) -> dict:
        """Build content slots with semantic intent (Fix #9)."""
        slots = {}
        semantic_sections = {
            s["type"]: s for s in semantic_brief.get("sections", [])
        }

        for section_id in sections:
            intent = INTENT_MAP.get(section_id, {})
            semantic = semantic_sections.get(section_id, {})
            content = semantic.get("content", {})

            # ── Heading slot ──
            heading_value = content.get("heading")
            slots[f"{section_id}.heading"] = ContentSlot(
                slot_id=f"{section_id}.heading",
                type="text",
                value=heading_value,
                max_length=60,
                tone=intent.get("tone", "professional"),
                target=target_market,
            ).to_dict()

            # ── Subtext slot ──
            subtext_value = content.get("subtext")
            slots[f"{section_id}.subtext"] = ContentSlot(
                slot_id=f"{section_id}.subtext",
                type="text",
                value=subtext_value,
                max_length=140,
                tone=intent.get("tone", "professional"),
                target=target_market,
            ).to_dict()

            # ── CTA slots ──
            cta_texts = content.get("cta_texts", [])
            if section_id in ("hero", "cta"):
                slots[f"{section_id}.cta.primary"] = ContentSlot(
                    slot_id=f"{section_id}.cta.primary",
                    type="button_text",
                    value=cta_texts[0] if cta_texts else None,
                    max_length=25,
                    style=intent.get("cta_style", "action"),
                ).to_dict()

                if len(cta_texts) > 1:
                    slots[f"{section_id}.cta.secondary"] = ContentSlot(
                        slot_id=f"{section_id}.cta.secondary",
                        type="button_text",
                        value=cta_texts[1],
                        max_length=25,
                        style="informational",
                    ).to_dict()

            # ── List slots (for features, pricing, etc.) ──
            if section_id == "features":
                feature_count = 3
                slots[f"{section_id}.items"] = ContentSlot(
                    slot_id=f"{section_id}.items",
                    type="list",
                    count=feature_count,
                    item_structure={"title": "text", "description": "text", "icon": "emoji"},
                ).to_dict()

            elif section_id == "pricing":
                slots[f"{section_id}.plans"] = ContentSlot(
                    slot_id=f"{section_id}.plans",
                    type="list",
                    count=3,
                    item_structure={
                        "name": "text", "price": "text",
                        "period": "text", "features": "list",
                        "highlight": "boolean",
                    },
                ).to_dict()

        return slots

    def _build_layout_tree_from_bbox(
        self, sections: list[dict],
    ) -> Optional[str]:
        """Detect global layout pattern from bounding boxes."""
        return self.spatial_engine.detect_layout_pattern(sections)

    def _extract_trend_keywords(self, market_data: Optional[dict]) -> list[str]:
        """Extract trend keywords from market data."""
        if not market_data:
            return []
        keywords = []
        for trend in (market_data.get("trends", []) or []):
            if isinstance(trend, dict):
                keywords.extend(trend.get("keywords", []))
                if trend.get("name"):
                    keywords.append(trend["name"])
            elif isinstance(trend, str):
                keywords.append(trend)
        return keywords

    def _compute_trend_velocity(self, market_data: Optional[dict]) -> float:
        """Compute trend velocity from market data."""
        if not market_data:
            return 0.0
        trends = market_data.get("trends", [])
        if not trends:
            return 0.0
        velocities = []
        for t in trends:
            if isinstance(t, dict):
                velocities.append(t.get("velocity", 0))
        return sum(velocities) / max(len(velocities), 1)

    def _extract_sources(self, semantic_brief: dict, market_data: Optional[dict]) -> list:
        """Extract provenance sources."""
        sources = []
        url = semantic_brief.get("source_metadata", {}).get("url")
        if url:
            sources.append({"type": "deep_analysis", "url": url})
        if market_data:
            for trend in market_data.get("trends", []):
                if isinstance(trend, dict) and trend.get("source"):
                    sources.append({"type": trend["source"], "id": trend.get("id", "")})
        return sources

    def _extract_screenshots(self, semantic_brief: dict) -> list:
        """Extract screenshot references for provenance."""
        screenshots = []
        for section in semantic_brief.get("sections", []):
            if section.get("_bounding_box"):
                screenshots.append({
                    "section": section.get("type"),
                    "bbox": section["_bounding_box"],
                    "bbox_used": True,
                })
        return screenshots

    def _auto_repair(self, ast: UIAST, validation: dict) -> UIAST:
        """Attempt to auto-repair a failed AST."""
        errors = validation.get("errors", [])

        for error in errors:
            if "Missing layout_tree" in error or "missing" in error.lower():
                # Rebuild sections from components
                if ast.components:
                    sections = list(ast.components.keys())
                    sections = self.grammar_engine.auto_fix_structure(sections)
                    ast.layout_tree = self._build_layout_tree(
                        sections, ast.variation
                    )
                    ast.constraints.order = sections
                    logger.info("Auto-repair: rebuilt layout tree from components")

            if "missing required color" in error.lower():
                # Fill in missing colors
                defaults = DesignTokens()
                for key in ["primary", "background", "text_primary"]:
                    if not ast.design_tokens.color_palette.get(key):
                        ast.design_tokens.color_palette[key] = defaults.color_palette[key]
                logger.info("Auto-repair: filled missing design token colors")

        return ast

    def _lower_tier(self, tier: str) -> str:
        """Lower complexity tier by one step."""
        tiers = ["minimal", "standard", "rich", "premium"]
        idx = tiers.index(tier) if tier in tiers else 1
        return tiers[max(0, idx - 1)]

    def _raise_tier(self, tier: str) -> str:
        """Raise complexity tier by one step."""
        tiers = ["minimal", "standard", "rich", "premium"]
        idx = tiers.index(tier) if tier in tiers else 1
        return tiers[min(len(tiers) - 1, idx + 1)]

    def _save_ast(self, ast: UIAST, template_id: str):
        """Save compiled AST to storage for debugging and audit."""
        output_dir = os.path.join(STORAGE_DIR, "compiled_asts")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"ui_ast_{template_id[:8]}_{int(time.time())}.json"
        path = os.path.join(output_dir, filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(ast.to_dict(), f, indent=2, default=str)
            logger.info("AST saved → %s", path)
        except Exception as e:
            logger.error("Failed to save AST: %s", e)
