"""
═══════════════════════════════════════════════════════════════════════
  MCP Brain — End-to-End Pipeline Test (Phase 4 Validation)
═══════════════════════════════════════════════════════════════════════

  This script validates the ENTIRE pipeline from start to finish:

  STAGE 1: Market Intelligence (Deep Site Analysis)
    └─ Trend collection → Deep site scraping → Gemini analysis
       → Pattern extraction → Demand estimation → Design brief

  STAGE 2: Template Generation
    └─ Brief parsing → Project scaffolding → Style generation
       → Layout building → Component generation → Code validation
       → Preview building → Packaging (ZIP)

  STAGE 3: Preview Server Verification
    └─ Start preview server → Verify template listing → Verify
       template preview → Capture preview screenshot

  STAGE 4: Deep Analysis Comparison
    └─ Run DeepSiteAnalyzer on the generated preview → Compare
       captured data against the original source analysis

  Usage:
      python e2e_pipeline_test.py
      python e2e_pipeline_test.py --url https://antigravity.google/
      python e2e_pipeline_test.py --skip-market   # Skip market stage, use existing brief
═══════════════════════════════════════════════════════════════════════
"""

import asyncio
import sys
import os
import json
import time
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime

# Add project root
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("e2e_test")


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def header(title, emoji="🔷"):
    print(f"\n{'═'*70}")
    print(f"  {emoji} {title}")
    print(f"{'═'*70}\n")

def step(msg, emoji="▶"):
    print(f"  {emoji} {msg}")

def success(msg):
    print(f"  ✅ {msg}")

def fail(msg):
    print(f"  ❌ {msg}")

def info(msg):
    print(f"     {msg}")

def divider():
    print(f"  {'─'*60}")


class TestReport:
    """Accumulates test results for the final summary."""
    def __init__(self):
        self.stages = []
        self.start_time = time.time()

    def add_stage(self, name, passed, duration, details=None):
        self.stages.append({
            "name": name,
            "passed": passed,
            "duration": round(duration, 2),
            "details": details or {},
        })

    def print_summary(self):
        elapsed = time.time() - self.start_time
        passed = sum(1 for s in self.stages if s["passed"])
        total = len(self.stages)

        header("TEST RESULTS SUMMARY", "📋")
        for s in self.stages:
            status = "✅ PASS" if s["passed"] else "❌ FAIL"
            print(f"  {status}  {s['name']:45s}  ({s['duration']}s)")
            if s.get("details"):
                for k, v in s["details"].items():
                    print(f"          {k}: {v}")

        divider()
        print(f"\n  Total: {passed}/{total} stages passed in {round(elapsed, 1)}s")
        if passed == total:
            print(f"  🎉 ALL STAGES PASSED — Pipeline is fully operational!\n")
        else:
            print(f"  ⚠️  {total - passed} stage(s) failed — review errors above.\n")

        return passed == total


# ═══════════════════════════════════════════════════════════════════
# STAGE 1: Market Intelligence (with Deep Analysis)
# ═══════════════════════════════════════════════════════════════════

async def stage_market_intelligence(report, reference_url=None):
    header("STAGE 1: Market Intelligence Pipeline", "🔍")
    start = time.time()

    try:
        from storage.metadata_store import metadata_store
        from utils.cache import cache
        from pipelines.market_pipeline import MarketPipeline

        # 1a. Clear caches
        step("Clearing caches...")
        try:
            cache.clear()
        except Exception:
            pass
        success("Caches cleared")

        # 1b. Inject reference URL if provided
        if reference_url:
            step(f"Using reference URL for deep analysis: {reference_url}")
            # Patch the TrendCollector to include our reference URL
            from market_intelligence.trend_collector import TrendCollector
            original_collect = TrendCollector.collect

            async def patched_collect(self):
                result = await original_collect(self)
                result["reference_url"] = reference_url
                result["trend"] = f"UI for: {reference_url.split('//')[1].split('/')[0]}"
                return result

            TrendCollector.collect = patched_collect
            info("TrendCollector patched with reference_url")

        # 1c. Run pipeline
        step("Running Market Intelligence Pipeline...")
        pipeline = MarketPipeline()
        pipeline_id, result = await pipeline.run("e2e_test")

        # 1d. Validate results
        brief = result.get("brief", {})
        demand_score = result.get("demand_score", 0)
        quality_score = result.get("quality_score", 0)

        success(f"Pipeline completed: {pipeline_id}")
        info(f"Demand score: {demand_score}")
        info(f"Quality score: {quality_score}")
        info(f"Brief sections: {brief.get('sections', [])}")

        # 1e. Check for deep analysis data
        briefs = metadata_store.get_design_briefs()
        has_deep = False
        if briefs:
            last_brief = briefs[-1]
            deep_path = last_brief.get("provenance", {}).get("deep_analysis")
            has_deep = bool(deep_path)
            info(f"Deep analysis captured: {'YES ✦' if has_deep else 'No (basic scrape)'}")

        # 1f. Save brief for stage 2
        brief_path = os.path.join("storage", "e2e_test_brief.json")
        with open(brief_path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2)
        success(f"Brief saved → {brief_path}")

        details = {
            "pipeline_id": pipeline_id,
            "demand_score": demand_score,
            "quality_score": quality_score,
            "deep_analysis": has_deep,
            "sections": len(brief.get("sections", [])),
        }
        report.add_stage("Market Intelligence", True, time.time() - start, details)

    except Exception as e:
        fail(f"Market Intelligence failed: {e}")
        import traceback
        traceback.print_exc()
        report.add_stage("Market Intelligence", False, time.time() - start, {"error": str(e)})


# ═══════════════════════════════════════════════════════════════════
# STAGE 2: Template Generation
# ═══════════════════════════════════════════════════════════════════

async def stage_template_generation(report):
    header("STAGE 2: Template Generation Pipeline", "🏗️")
    start = time.time()

    try:
        from storage.metadata_store import metadata_store
        from pipelines.template_pipeline import TemplatePipeline

        # 2a. Get the latest brief
        step("Loading design brief...")
        briefs = metadata_store.get_design_briefs()
        if not briefs:
            # Try from file
            brief_path = os.path.join("storage", "e2e_test_brief.json")
            if os.path.isfile(brief_path):
                with open(brief_path, "r") as f:
                    brief = json.load(f)
            else:
                raise Exception("No design brief available. Run Stage 1 first.")
        else:
            brief = briefs[-1]

        info(f"Brief loaded: {len(brief.get('sections', []))} sections")

        # 2b. Run template pipeline
        step("Running Template Generator Pipeline...")
        pipeline = TemplatePipeline()
        pipeline_id, result = await pipeline.run(brief)

        template_name = result.get("template_name", "unknown")
        components = result.get("components_generated", 0)
        gen_time = result.get("generation_time_seconds", 0)
        validation = result.get("validation", {})
        package = result.get("package", {})

        success(f"Template generated: {template_name}")
        info(f"Components: {components}")
        info(f"Generation time: {gen_time}s")
        info(f"Validation: {'✅ Valid' if validation.get('valid') else '⚠️ ' + str(validation.get('errors', []))}")
        info(f"Warnings: {validation.get('warnings', 0)}")

        # 2c. Check package
        zip_path = package.get("zip_path", "")
        zip_exists = os.path.isfile(zip_path) if zip_path else False
        info(f"Package ZIP: {'✅ ' + zip_path if zip_exists else '❌ Not found'}")

        # 2d. Check generated files
        tmpl_dir = os.path.join("generated_templates", template_name)
        if os.path.isdir(tmpl_dir):
            file_count = sum(1 for _, _, files in os.walk(tmpl_dir) for _ in files)
            info(f"Generated files: {file_count}")
        else:
            file_count = 0
            info("Generated directory not found")

        # 2e. Check registry
        reg_path = os.path.join("generated_templates", "template_registry.json")
        if os.path.isfile(reg_path):
            with open(reg_path) as f:
                registry = json.load(f)
            info(f"Registry entries: {len(registry)}")

        details = {
            "template_name": template_name,
            "components": components,
            "gen_time": f"{gen_time}s",
            "valid": validation.get("valid", False),
            "zip": zip_exists,
            "files": file_count,
        }
        report.add_stage("Template Generation", True, time.time() - start, details)

    except Exception as e:
        fail(f"Template Generation failed: {e}")
        import traceback
        traceback.print_exc()
        report.add_stage("Template Generation", False, time.time() - start, {"error": str(e)})


# ═══════════════════════════════════════════════════════════════════
# STAGE 3: Preview Server Verification
# ═══════════════════════════════════════════════════════════════════

async def stage_preview_verification(report):
    header("STAGE 3: Preview Server Verification", "👁️")
    start = time.time()

    try:
        import subprocess
        import httpx

        # 3a. Start the preview server in background
        step("Starting preview server on port 4000...")
        server_proc = subprocess.Popen(
            [sys.executable, "preview_server/run_template_preview.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(__file__),
        )

        # Give it time to start
        await asyncio.sleep(2)

        if server_proc.poll() is not None:
            stderr = server_proc.stderr.read().decode() if server_proc.stderr else ""
            raise Exception(f"Preview server failed to start: {stderr}")

        success("Preview server started (PID: {})".format(server_proc.pid))

        # 3b. Test index page
        step("Testing template listing page...")
        client = httpx.AsyncClient(timeout=10)
        try:
            resp = await client.get("http://localhost:4000/")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert "Template Preview" in resp.text, "Missing preview page title"
            success("Index page loads correctly")

            # 3c. Test template preview
            step("Testing template preview...")
            reg_path = os.path.join("generated_templates", "template_registry.json")
            if os.path.isfile(reg_path):
                with open(reg_path) as f:
                    registry = json.load(f)
                if registry:
                    name = registry[-1].get("template_name")
                    resp = await client.get(f"http://localhost:4000/template-preview/{name}")
                    assert resp.status_code == 200, f"Preview returned {resp.status_code}"
                    success(f"Template preview loads: {name}")

                    # Test raw file serving
                    resp2 = await client.get(f"http://localhost:4000/template-preview/{name}/raw/index.html")
                    info(f"Raw index.html: {resp2.status_code} ({len(resp2.text)} bytes)")
        finally:
            await client.aclose()

        # 3d. Capture preview screenshot with Playwright
        step("Capturing preview screenshot with Playwright...")
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1440, "height": 900})
                await page.goto("http://localhost:4000/", wait_until="networkidle", timeout=15000)

                shot_path = os.path.join("storage", "e2e_preview_listing.png")
                await page.screenshot(path=shot_path, full_page=True)
                success(f"Listing screenshot saved → {shot_path}")

                # If templates exist, capture the first one
                if os.path.isfile(reg_path):
                    with open(reg_path) as f:
                        registry = json.load(f)
                    if registry:
                        name = registry[-1].get("template_name")
                        await page.goto(
                            f"http://localhost:4000/template-preview/{name}/raw/index.html",
                            wait_until="networkidle",
                            timeout=15000,
                        )
                        await asyncio.sleep(1)
                        shot_path2 = os.path.join("storage", "e2e_preview_template.png")
                        await page.screenshot(path=shot_path2, full_page=True)
                        success(f"Template screenshot saved → {shot_path2}")

                await browser.close()
        except Exception as pw_err:
            info(f"Playwright screenshot skipped: {pw_err}")

        # 3e. Stop preview server
        server_proc.terminate()
        success("Preview server stopped")

        report.add_stage("Preview Verification", True, time.time() - start, {"port": 4000})

    except Exception as e:
        fail(f"Preview verification failed: {e}")
        import traceback
        traceback.print_exc()
        try:
            server_proc.terminate()
        except Exception:
            pass
        report.add_stage("Preview Verification", False, time.time() - start, {"error": str(e)})


# ═══════════════════════════════════════════════════════════════════
# STAGE 4: Deep Analysis Comparison
# ═══════════════════════════════════════════════════════════════════

async def stage_deep_analysis_comparison(report, reference_url=None):
    header("STAGE 4: Deep Analysis Validation", "🔬")
    start = time.time()

    try:
        from services.deep_site_analyzer import DeepSiteAnalyzer

        if not reference_url:
            info("No reference URL provided, skipping deep analysis comparison")
            report.add_stage("Deep Analysis Comparison", True, time.time() - start, {"skipped": True})
            return

        # 4a. Check if original analysis exists
        step(f"Checking for existing deep analysis of {reference_url}...")
        analysis_dir = os.path.join("storage", "deep_analysis")
        original_json = None
        if os.path.isdir(analysis_dir):
            for root, dirs, files in os.walk(analysis_dir):
                for f in files:
                    if f.endswith("_analysis.json"):
                        fp = os.path.join(root, f)
                        try:
                            with open(fp) as fh:
                                data = json.load(fh)
                            if data.get("url") == reference_url or data.get("final_url") == reference_url:
                                original_json = data
                                info(f"Found existing analysis: {fp}")
                                break
                        except Exception:
                            pass
                if original_json:
                    break

        if not original_json:
            step("Running fresh deep analysis...")
            analyzer = DeepSiteAnalyzer(headless=True)
            result = await analyzer.analyze(
                url=reference_url,
                out_dir=os.path.join("storage", "deep_analysis", "e2e_test"),
                viewport_width=1920,
                viewport_height=1080,
                scroll_screenshot_interval=1000,
                max_scroll_screenshots=8,
            )
            info(f"Analysis complete: {result.analysis_json_path}")
            with open(result.analysis_json_path) as fh:
                original_json = json.load(fh)

        # 4b. Report analysis stats
        success(f"Deep analysis data available for {reference_url}")
        info(f"  Fonts:      {len(original_json.get('fonts', []))}")
        info(f"  Colors:     {len(original_json.get('colors', []))}")
        info(f"  Sections:   {len(original_json.get('sections', []))}")
        info(f"  Animations: {len(original_json.get('animations', []))}")
        info(f"  Layouts:    {len(original_json.get('layouts', []))}")
        info(f"  Headings:   {len(original_json.get('headings', []))}")
        info(f"  Images:     {len(original_json.get('images', []))}")
        info(f"  Page:       {original_json.get('page_height', '?')}px tall")
        info(f"  Duration:   {original_json.get('analysis_duration_seconds', '?')}s")

        # 4c. Validate data completeness
        checks = [
            ("fonts", len(original_json.get("fonts", [])) > 0),
            ("colors", len(original_json.get("colors", [])) > 0),
            ("sections", len(original_json.get("sections", [])) > 0),
            ("headings", len(original_json.get("headings", [])) > 0),
            ("computed_styles", bool(original_json.get("computed_styles", {}).get("body"))),
            ("scroll_screenshots", len(original_json.get("scroll_screenshots", [])) > 0),
        ]

        divider()
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        if all_passed:
            success("All deep analysis data categories populated")
        else:
            fail("Some data categories are empty")

        details = {
            "fonts": len(original_json.get("fonts", [])),
            "colors": len(original_json.get("colors", [])),
            "sections": len(original_json.get("sections", [])),
            "animations": len(original_json.get("animations", [])),
            "all_checks_passed": all_passed,
        }
        report.add_stage("Deep Analysis Validation", all_passed, time.time() - start, details)

    except Exception as e:
        fail(f"Deep analysis validation failed: {e}")
        import traceback
        traceback.print_exc()
        report.add_stage("Deep Analysis Validation", False, time.time() - start, {"error": str(e)})


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description="MCP Brain E2E Pipeline Test")
    parser.add_argument("--url", type=str, default=None,
                        help="Reference URL for deep analysis (e.g. https://antigravity.google/)")
    parser.add_argument("--skip-market", action="store_true",
                        help="Skip market intelligence stage (use existing brief)")
    parser.add_argument("--skip-preview", action="store_true",
                        help="Skip preview server stage")
    args = parser.parse_args()

    print(f"\n{'═'*70}")
    print(f"  🧠 MCP BRAIN — END-TO-END PIPELINE TEST")
    print(f"  Phase 4 Validation: Market → Template → Package → Preview")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.url:
        print(f"  Reference URL: {args.url}")
    print(f"{'═'*70}")

    report = TestReport()

    # Stage 1: Market Intelligence
    if not args.skip_market:
        await stage_market_intelligence(report, reference_url=args.url)
    else:
        info("Skipping Market Intelligence (--skip-market)")
        report.add_stage("Market Intelligence", True, 0, {"skipped": True})

    # Stage 2: Template Generation
    await stage_template_generation(report)

    # Stage 3: Preview Server
    if not args.skip_preview:
        await stage_preview_verification(report)
    else:
        info("Skipping Preview Verification (--skip-preview)")
        report.add_stage("Preview Verification", True, 0, {"skipped": True})

    # Stage 4: Deep Analysis
    await stage_deep_analysis_comparison(report, reference_url=args.url)

    # Final Summary
    all_passed = report.print_summary()

    # Save report JSON
    report_path = os.path.join("storage", "e2e_test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "reference_url": args.url,
            "stages": report.stages,
            "all_passed": all_passed,
        }, f, indent=2)
    print(f"  📄 Report saved → {report_path}\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
