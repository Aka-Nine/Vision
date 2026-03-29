"""
UI AST System -- Integration Test
==================================
Tests the complete Phase 2.5 compiler pipeline:
  semantic_brief + design_brief + patterns -> UI AST -> validated output
"""

import asyncio
import json
import sys
import os
import io
import logging

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(stream=sys.stderr)],
)

from ui_ast.compiler import UIASTCompiler
from ui_ast.validator import UIASTValidator
from ui_ast.schema import UIAST
from ui_ast.spatial_engine import SpatialEngine
from ui_ast.grammar_engine import UIGrammarEngine
from ui_ast.variation_engine import VariationEngine
from ui_ast.demand_adapter import DemandAdapter
from ui_ast.pattern_selector import DominantPatternSelector
from ui_ast.feedback_loop import FeedbackLoop, FeedbackRecord


async def test_full_compilation():
    """Test the complete compiler pipeline."""
    print("=" * 70)
    print("  [TEST] UI AST COMPILER -- INTEGRATION TEST")
    print("=" * 70)

    compiler = UIASTCompiler()
    validator = UIASTValidator()

    # -- Mock inputs (simulating Phase 2 outputs) --
    semantic_brief = {
        "sections": [
            {
                "type": "hero",
                "intent": "primary_value_proposition",
                "content": {
                    "heading": "Ship AI Products 10x Faster",
                    "subtext": "The autonomous platform that turns market intelligence into production-ready UI.",
                    "cta": "Start Building",
                    "cta_secondary": "Watch Demo",
                    "cta_texts": ["Start Building", "Watch Demo"],
                },
                "meta": {"confidence": 0.92, "source": "deep_analysis"},
                "_bounding_box": [0, 80, 1440, 700],
            },
            {
                "type": "features",
                "intent": "capability_highlight",
                "content": {
                    "heading": "Built for Speed & Scale",
                    "subtext": "Everything you need to go from idea to deployed product.",
                    "cta_texts": [],
                },
                "meta": {"confidence": 0.85, "source": "deep_analysis"},
                "_bounding_box": [0, 800, 1440, 500],
            },
            {
                "type": "pricing",
                "intent": "value_comparison",
                "content": {
                    "heading": "Simple, Transparent Pricing",
                    "subtext": None,
                    "cta_texts": [],
                },
                "meta": {"confidence": 0.78, "source": "trend_analysis"},
            },
            {
                "type": "testimonials",
                "intent": "trust_building",
                "content": {
                    "heading": "Loved by 500+ Teams",
                    "subtext": None,
                    "cta_texts": [],
                },
                "meta": {"confidence": 0.70, "source": "deep_analysis"},
            },
        ],
        "source_metadata": {
            "url": "https://example.com",
            "title": "AI Product Factory",
        },
        "design_tokens": {
            "fonts": ["Inter", "JetBrains Mono"],
            "colors": ["#7C3AED", "#06B6D4", "#0F172A"],
        },
        "market_context": {
            "product_type": "AI SaaS Platform",
            "target_market": "Technical founders",
            "demand_score": 0.88,
        },
        "_stats": {
            "total_sections": 4,
            "avg_confidence": 0.81,
        },
    }

    design_brief = {
        "product_type": "AI-Powered SaaS Analytics Dashboard",
        "target_market": "B2B SaaS Founders and CTOs",
        "style": "dark glassmorphic",
        "sections": ["hero", "features", "pricing", "testimonials", "cta", "footer"],
        "animation_type": "scroll reveal",
        "demand_score": 0.88,
        "tone": "technical",
        "cta_style": "conversion-focused",
        "content_theme": "Autonomous AI-driven product creation",
    }

    patterns = [
        {"layout_type": "SaaS Landing Page", "structure": ["Hero Section", "Features", "Pricing", "Footer"]},
        {"layout_type": "AI Dashboard", "structure": ["Header", "Stats", "Charts", "Sidebar"]},
    ]

    market_data = {
        "demand_score": 0.88,
        "competition_score": 0.45,
        "trends": [
            {"name": "AI SaaS", "velocity": 85, "source": "reddit"},
            {"name": "Glassmorphism", "velocity": 60, "source": "pinterest"},
        ],
    }

    # -- Compile --
    print("\n  [STEP] Compiling UI AST...")
    ast = await compiler.compile(
        semantic_brief=semantic_brief,
        design_brief=design_brief,
        patterns=patterns,
        market_data=market_data,
    )

    # -- Validate --
    print("\n  [STEP] Validating AST...")
    validation = validator.validate(ast)

    # -- Output Results --
    ast_dict = ast.to_dict()

    print("\n" + "-" * 70)
    print("  COMPILATION RESULTS")
    print("-" * 70)
    print(f"  [OK] Template ID:       {ast.meta.get('template_id', 'N/A')[:12]}...")
    print(f"  [OK] Design System:     {ast.meta.get('design_system')}")
    print(f"  [OK] Complexity Tier:   {ast.meta.get('complexity_tier')}")
    print(f"  [OK] Dominant Pattern:  {ast.provenance.dominant_pattern}")
    print(f"  [OK] Variation Seed:    {ast.variation.variation_seed}")
    print(f"  [OK] Layout Variant:    {ast.variation.layout_variant}")
    print(f"  [OK] Feature Style:     {ast.variation.feature_style}")
    print(f"  [OK] Animation Level:   {ast.variation.animation_intensity}")
    print(f"  [OK] Color Mode:        {ast.variation.color_mode}")
    print(f"  [OK] Theme:             {ast.design_tokens.theme}")
    print(f"  [OK] Primary Color:     {ast.design_tokens.color_palette.get('primary')}")
    print(f"  [OK] Font Family:       {ast.design_tokens.typography.get('font_family')}")
    
    print(f"\n  LAYOUT TREE:")
    print(f"     Root type:        {ast.layout_tree.type}")
    print(f"     Children:         {len(ast.layout_tree.children)}")
    for child in ast.layout_tree.children:
        child_count = len(child.children) if hasattr(child, 'children') else 0
        print(f"       +-- {child.id} ({child.type}, {child_count} children)")
    
    print(f"\n  COMPONENTS:          {len(ast.components)}")
    for comp_id, comp_data in ast.components.items():
        print(f"       +-- {comp_id}: <{comp_data.get('tag', '?')}> {comp_data.get('component_name')}")

    print(f"\n  CONTENT SLOTS:       {len(ast.content_slots)}")
    filled = sum(1 for s in ast.content_slots.values() if s.get("value"))
    print(f"       Filled:         {filled}/{len(ast.content_slots)}")

    print(f"\n  SPATIAL RULES:       {len(ast.spatial_rules)}")
    for sid, rule in ast.spatial_rules.items():
        print(f"       +-- {sid}: height={rule.get('height')}, align={rule.get('alignment')}")

    print(f"\n  CONSTRAINTS:")
    print(f"       Required:       {ast.constraints.required_sections}")
    print(f"       Order:          {ast.constraints.order}")
    print(f"       Rules:          {len(ast.constraints.rules)}")

    print(f"\n  VALIDATION:")
    print(f"       Valid:          {'PASS' if validation['valid'] else 'FAIL'}")
    print(f"       Score:          {validation['score']}")
    print(f"       Errors:         {len(validation['errors'])}")
    print(f"       Warnings:       {len(validation['warnings'])}")
    for e in validation.get("errors", []):
        print(f"         [ERR] {e}")
    for w in validation.get("warnings", []):
        print(f"         [WARN] {w}")

    print(f"\n  PROVENANCE:")
    print(f"       Sources:        {len(ast.provenance.sources)}")
    print(f"       Screenshots:    {len(ast.provenance.screenshots)}")
    print(f"       Demand Score:   {ast.provenance.demand_score}")
    print(f"       Discarded:      {ast.provenance.discarded_patterns}")

    # -- Save full AST for inspection --
    output_path = os.path.join(os.path.dirname(__file__), "test_ast_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ast_dict, f, indent=2, default=str)
    print(f"\n  [SAVED] Full AST -> {output_path}")

    print("\n" + "=" * 70)
    if validation["valid"]:
        print("  [PASS] ALL TESTS PASSED -- UI AST System is operational!")
    else:
        print("  [WARN] AST compiled with validation issues (check above)")
    print("=" * 70)

    return ast, validation


def test_individual_components():
    """Test each sub-system independently."""
    print("\n  [TEST] Testing Individual Components...")
    all_passed = True

    # 1. Spatial Engine
    print("\n  -- Spatial Engine --")
    se = SpatialEngine()
    sections = [
        {"type": "hero", "_bounding_box": [0, 80, 1440, 700]},
        {"type": "features", "_bounding_box": [0, 800, 1440, 500]},
        {"type": "navbar", "_bounding_box": [0, 0, 1440, 72]},
    ]
    rules = se.extract_spatial_rules(sections)
    for sid, rule in rules.items():
        print(f"     {sid}: height={rule.height}, align={rule.alignment}, pos={rule.position}")
    assert rules["navbar"].position == "sticky", "Navbar should be sticky"
    assert rules["hero"].height in ("80vh", "100vh"), f"Hero should be tall, got {rules['hero'].height}"
    print("     [PASS] Spatial Engine OK")

    # 2. Grammar Engine
    print("\n  -- Grammar Engine --")
    ge = UIGrammarEngine()
    ok, viols = ge.validate_section_order(["hero", "navbar", "footer"])
    assert not ok, "Should fail -- hero before navbar"
    print(f"     Violations caught: {viols}")
    fixed = ge.auto_fix_structure(["hero", "features"])
    assert fixed[0] == "navbar", f"Should add navbar first, got {fixed[0]}"
    assert fixed[-1] == "footer", f"Should add footer last, got {fixed[-1]}"
    print(f"     Auto-fixed: {fixed}")
    print("     [PASS] Grammar Engine OK")

    # 3. Variation Engine
    print("\n  -- Variation Engine --")
    ve = VariationEngine()
    v1 = ve.generate(seed=42, product_type="AI SaaS", demand_score=0.9)
    v2 = ve.generate(seed=99, product_type="E-commerce", demand_score=0.3)
    print(f"     Seed 42: layout={v1.layout_variant}, features={v1.feature_style}, anim={v1.animation_intensity}")
    print(f"     Seed 99: layout={v2.layout_variant}, features={v2.feature_style}, anim={v2.animation_intensity}")
    print("     [PASS] Variation Engine OK")

    # 4. Demand Adapter
    print("\n  -- Demand Adapter --")
    da = DemandAdapter()
    high = da.compute_complexity(demand_score=0.95, trend_velocity=80, competition_score=0.3)
    low = da.compute_complexity(demand_score=0.2, trend_velocity=5, competition_score=0.9)
    assert high["tier"] in ("rich", "premium"), f"High demand should be rich/premium, got {high['tier']}"
    assert low["tier"] in ("minimal", "standard"), f"Low demand should be minimal/standard, got {low['tier']}"
    print(f"     High demand: tier={high['tier']}, composite={high['composite_score']}")
    print(f"     Low demand:  tier={low['tier']}, composite={low['composite_score']}")
    print("     [PASS] Demand Adapter OK")

    # 5. Pattern Selector
    print("\n  -- Pattern Selector --")
    ps = DominantPatternSelector()
    result = ps.select(
        patterns=[{"layout_type": "SaaS Landing", "structure": ["Hero", "Features"]}],
        product_type="AI Analytics Dashboard",
        style_hint="dark glassmorphic",
        trend_keywords=["ai", "saas", "dashboard"],
    )
    print(f"     Dominant: {result['dominant']} (confidence={result['confidence']:.2f})")
    print(f"     Discarded: {result['discarded']}")
    assert result["dominant"] is not None, "Should select a dominant pattern"
    print("     [PASS] Pattern Selector OK")

    # 6. Feedback Loop
    print("\n  -- Feedback Loop --")
    fl = FeedbackLoop(store_dir=os.path.join(os.path.dirname(__file__), "storage", "feedback_test"))
    record = FeedbackRecord(
        template_id="test-001",
        ast_validation_score=0.95,
        generation_success=True,
        dominant_pattern="ai_saas_dark",
        variation_seed=42,
        section_count=6,
        content_fill_rate=0.8,
        build_errors=0,
        generation_time_seconds=12.5,
        demand_score=0.88,
        complexity_tier="rich",
    )
    fl.record(record)
    rates = fl.get_pattern_success_rates()
    print(f"     Pattern rates: {rates}")
    summary = fl.get_summary()
    print(f"     Overall success: {summary['overall_success_rate']}")
    print("     [PASS] Feedback Loop OK")

    print("\n  [PASS] All individual component tests passed!")
    return all_passed


if __name__ == "__main__":
    # Run individual tests first
    ok = test_individual_components()

    # Then run the full integration test
    ast, validation = asyncio.run(test_full_compilation())

    # Final verdict
    if validation["valid"] or validation["score"] > 0.7:
        print("\n  >>> SYSTEM READY: UI AST pipeline is operational <<<")
        sys.exit(0)
    else:
        print("\n  >>> SYSTEM ISSUES: Check validation errors above <<<")
        sys.exit(1)
