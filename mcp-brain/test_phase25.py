"""
Test Phase 2.5 — Semantic Content Engine
═══════════════════════════════════════════
Standalone test that processes the existing deep analysis data
through the Semantic Content Engine and validates the output.
"""

import asyncio
import json
import sys
import os
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def test_semantic_engine():
    """Test the Semantic Content Engine with real data."""
    from semantic_content_engine.engine import SemanticContentEngine

    print("\n")
    print("═" * 70)
    print("  🧠 PHASE 2.5 TEST: Semantic Content Engine")
    print("═" * 70)
    print()

    engine = SemanticContentEngine()

    # ── Test 1: Process with auto-loaded deep analysis ──────────────
    print("━━━ Test 1: Auto-load latest deep analysis ━━━")

    # Simulate brief data (from Phase 2)
    brief_data = {
        "product_type": "AI SaaS template Template",
        "target_market": "AI startups",
        "style": "modern dark gradient",
        "demand_score": 0.91,
    }

    trend_data = {
        "trends": [
            {"trend": "UI for: antigravity.google", "popularity_score": 0.88, "source": "hacker_news_free_api"},
        ]
    }

    result = await engine.process(
        deep_analysis=None,  # Auto-loads from storage
        trend_data=trend_data,
        brief_data=brief_data,
    )

    # ── Report ──────────────────────────────────────────────────────
    stats = result.get("_stats", {})
    validation = result.get("_validation", {})

    print()
    print("╔" + "═" * 68 + "╗")
    print("║  ✅ SEMANTIC ENGINE OUTPUT" + " " * 42 + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║  Total Sections     : {stats.get('total_sections', 0)}" + " " * (45 - len(str(stats.get('total_sections', 0)))) + "║")
    print(f"║  Avg Confidence     : {stats.get('avg_confidence', 0):.3f}" + " " * 40 + "║")
    print(f"║  Above Threshold    : {stats.get('sections_above_threshold', 0)}" + " " * (45 - len(str(stats.get('sections_above_threshold', 0)))) + "║")
    print(f"║  Below Threshold    : {stats.get('sections_below_threshold', 0)}" + " " * (45 - len(str(stats.get('sections_below_threshold', 0)))) + "║")
    print(f"║  Validation Valid   : {validation.get('is_valid', False)}" + " " * (45 - len(str(validation.get('is_valid', False)))) + "║")
    print("╠" + "═" * 68 + "╣")

    sections = result.get("sections", [])
    for i, section in enumerate(sections):
        sec_type = section.get("type", "unknown")
        intent = section.get("intent", "unknown")
        content = section.get("content", {})
        meta = section.get("meta", {})

        heading = content.get("heading", "—")
        heading_short = (heading[:50] + "...") if heading and len(heading) > 50 else (heading or "—")
        subtext = content.get("subtext", "—")
        subtext_short = (subtext[:45] + "...") if subtext and len(subtext) > 45 else (subtext or "—")
        cta = content.get("cta") or "—"
        confidence = meta.get("confidence", 0)
        source = meta.get("source") or "unknown"

        print(f"║  [{i+1}] {sec_type:15s} │ {intent:28s} │ {confidence:.2f} ║")
        print(f"║      Heading: {heading_short:52s} ║")
        print(f"║      Subtext: {subtext_short:52s} ║")
        print(f"║      CTA: {cta:32s} Source: {source:13s} ║")
        if i < len(sections) - 1:
            print("║  " + "─" * 64 + "  ║")

    print("╠" + "═" * 68 + "╣")

    # Validation issues
    issues = validation.get("issues", [])
    if issues:
        print("║  Validation Issues:" + " " * 48 + "║")
        for issue in issues:
            issue_short = issue[:64]
            print(f"║    {issue_short}" + " " * max(0, 64 - len(issue_short)) + "║")
    else:
        print("║  ✅ No validation issues" + " " * 43 + "║")

    print("╚" + "═" * 68 + "╝")

    # ── Save output for inspection ──────────────────────────────────
    output_path = "storage/test_semantic_brief.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n  📄 Full output saved → {output_path}")

    # ── Acceptance criteria checks ──────────────────────────────────
    print("\n━━━ Acceptance Criteria Check ━━━\n")

    checks = []

    # Check 1: Hero section has real heading
    hero = next((s for s in sections if s["type"] == "hero"), None)
    if hero and hero["content"].get("heading"):
        checks.append(("✅", "Hero has real extracted heading"))
    else:
        checks.append(("❌", "Hero section missing or has no heading"))

    # Check 2: No placeholder text
    placeholder_keywords = ["placeholder", "lorem ipsum", "your text here", "content for"]
    has_placeholder = False
    for s in sections:
        for field in ["heading", "subtext"]:
            val = (s.get("content", {}).get(field) or "").lower()
            if any(p in val for p in placeholder_keywords):
                has_placeholder = True
    checks.append(("✅" if not has_placeholder else "❌", "No placeholder text anywhere"))

    # Check 3: Context-aware CTAs
    ctas_with_content = [s for s in sections if s["content"].get("cta")]
    checks.append(("✅" if ctas_with_content else "❌", f"Context-aware CTAs found: {len(ctas_with_content)}"))

    # Check 4: Section types normalized
    raw_types = [s.get("type") for s in sections]
    canonical_types = {"hero", "features", "video", "use_cases", "pricing", "cta", "blog", "about",
                       "testimonials", "footer", "navbar", "header", "faq", "contact", "dashboard"}
    normalized_count = sum(1 for t in raw_types if t in canonical_types or t.endswith("_alt"))
    checks.append(("✅" if normalized_count > 0 else "❌", f"Section types normalized: {normalized_count}/{len(raw_types)}"))

    # Check 5: Confidence scores
    all_have_confidence = all(s["meta"]["confidence"] > 0 for s in sections)
    checks.append(("✅" if all_have_confidence else "❌", "Confidence scores assigned to all sections"))

    # Check 6: Deduplication worked
    checks.append(("✅" if len(sections) < 20 else "⚠️", f"Deduplication reduced to {len(sections)} sections"))

    # Check 7: No crashes on real data
    checks.append(("✅", "Pipeline completed without crashes"))

    for icon, msg in checks:
        print(f"  {icon} {msg}")

    all_passed = all(c[0] == "✅" for c in checks)
    print()
    if all_passed:
        print("  🎉 ALL ACCEPTANCE CRITERIA PASSED!")
    else:
        print("  ⚠️  Some criteria need attention")

    print()
    print("═" * 70)
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_semantic_engine())
    sys.exit(0 if success else 1)
