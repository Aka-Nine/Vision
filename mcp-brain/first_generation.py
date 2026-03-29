"""
═══════════════════════════════════════════════════════════════════════
  MCP Brain — First Generation: Fresh Data Collection Pipeline
═══════════════════════════════════════════════════════════════════════
  This script performs the very first clean data collection run:
    1. Resets market_data.json to a clean state
    2. Clears all caches and deduplication hashes
    3. Runs the full Market Intelligence Pipeline
    4. Outputs a detailed report of what was collected
═══════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import os
import sys
import time
import logging
from datetime import datetime

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def reset_data_store():
    """Reset market_data.json to a fresh, empty state."""
    db_path = "market_data.json"
    fresh_db = {
        "schema_version": "1.0",
        "generation_metadata": {
            "generation_number": 1,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        },
        "trends": [],
        "design_references": [],
        "ui_patterns": [],
        "demand_scores": [],
        "design_briefs": []
    }

    # Backup old data if it exists
    if os.path.exists(db_path):
        backup_name = f"market_data_backup_{int(time.time())}.json"
        os.rename(db_path, backup_name)
        logger.info(f"📦 Backed up old data → {backup_name}")

    with open(db_path, "w") as f:
        json.dump(fresh_db, f, indent=4)
    logger.info("🧹 Reset market_data.json to clean state")


def reset_pipeline_states():
    """Reset pipeline states tracker."""
    states_path = "pipeline_states.json"
    if os.path.exists(states_path):
        with open(states_path, "w") as f:
            json.dump({}, f)
        logger.info("🧹 Reset pipeline_states.json")


async def run_first_generation():
    """Execute the complete data collection pipeline."""
    
    print("\n")
    print("═" * 70)
    print("  🧠 MCP BRAIN — FIRST GENERATION: DATA COLLECTION")
    print("═" * 70)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
    print()
    
    # ── Step 1: Clean slate ──────────────────────────────────────────
    logger.info("━━━ STEP 1: Preparing clean data store ━━━")
    reset_data_store()
    reset_pipeline_states()

    # Clear runtime caches
    from utils.cache import cache
    cache.clear()
    logger.info("🧹 Cleared runtime cache")

    from market_intelligence.deduplication_engine import deduplication_engine
    deduplication_engine.reset()
    logger.info("🧹 Cleared deduplication hashes")
    print()

    # ── Step 2: Run pipeline ─────────────────────────────────────────
    logger.info("━━━ STEP 2: Running Market Intelligence Pipeline ━━━")
    
    from pipelines.market_pipeline import MarketPipeline
    pipeline = MarketPipeline()
    
    start_time = time.time()
    
    try:
        pipeline_id, result = await pipeline.run("First Generation — Full Data Collection")
        elapsed = time.time() - start_time
        
        print()
        logger.info("━━━ STEP 3: Pipeline Results ━━━")
        print()
        
        # ── Step 3: Report ───────────────────────────────────────────
        brief = result.get("brief", {})
        
        print("╔" + "═" * 68 + "╗")
        print("║  ✅ FIRST GENERATION COMPLETED SUCCESSFULLY" + " " * 24 + "║")
        print("╠" + "═" * 68 + "╣")
        print(f"║  Pipeline ID : {pipeline_id[:36]}...  ║")
        print(f"║  Duration    : {elapsed:.2f} seconds" + " " * (52 - len(f"{elapsed:.2f} seconds")) + "║")
        print(f"║  Status      : {result.get('status', 'unknown')}" + " " * (52 - len(result.get('status', 'unknown'))) + "║")
        print("╠" + "═" * 68 + "╣")
        
        # Brief details
        print(f"║  Product Type  : {brief.get('product_type', 'N/A')[:48]}" + " " * max(0, 50 - len(brief.get('product_type', 'N/A')[:48])) + "║")
        print(f"║  Target Market : {brief.get('target_market', 'N/A')[:48]}" + " " * max(0, 50 - len(brief.get('target_market', 'N/A')[:48])) + "║")
        print(f"║  Style         : {brief.get('style', 'N/A')[:48]}" + " " * max(0, 50 - len(brief.get('style', 'N/A')[:48])) + "║")
        print(f"║  Animation     : {brief.get('animation_type', 'N/A')[:48]}" + " " * max(0, 50 - len(brief.get('animation_type', 'N/A')[:48])) + "║")
        print(f"║  Demand Score  : {result.get('demand_score', 'N/A')}" + " " * max(0, 50 - len(str(result.get('demand_score', 'N/A')))) + "║")
        print(f"║  Quality Score : {result.get('quality_score', 'N/A')}" + " " * max(0, 50 - len(str(result.get('quality_score', 'N/A')))) + "║")
        print("╠" + "═" * 68 + "╣")
        
        sections = brief.get("sections", [])
        print(f"║  Sections ({len(sections)}):" + " " * (54 - len(f"Sections ({len(sections)}):")) + "║")
        for i, section in enumerate(sections, 1):
            sec_text = f"    {i}. {section}"[:66]
            print(f"║  {sec_text}" + " " * max(0, 66 - len(sec_text)) + "║")
        
        # Provenance
        provenance = brief.get("provenance", {})
        if provenance:
            print("╠" + "═" * 68 + "╣")
            print("║  Data Provenance:" + " " * 50 + "║")
            print(f"║    Trend Source : {provenance.get('trend_source', 'N/A')[:46]}" + " " * max(0, 48 - len(provenance.get('trend_source', 'N/A')[:46])) + "║")
            print(f"║    Design Ref   : {provenance.get('design_reference', 'N/A')[:46]}" + " " * max(0, 48 - len(provenance.get('design_reference', 'N/A')[:46])) + "║")
            print(f"║    AI Model     : {provenance.get('analysis_model', 'N/A')[:46]}" + " " * max(0, 48 - len(provenance.get('analysis_model', 'N/A')[:46])) + "║")
            print(f"║    Reputation   : {provenance.get('source_reputation', 'N/A')}" + " " * max(0, 48 - len(str(provenance.get('source_reputation', 'N/A')))) + "║")
            
            image_urls = provenance.get('image_urls', [])
            if image_urls:
                print(f"║    Images ({len(image_urls)}):" + " " * max(0, 52 - len(f"Images ({len(image_urls)}):")) + "║")
                for url in image_urls[:3]:
                    url_short = url[:60]
                    print(f"║      {url_short}..." + " " * max(0, 62 - len(url_short) - 3) + "║")
        
        # LLM Provider Info
        llm_provider = brief.get("_llm_provider", "unknown")
        print("╠" + "═" * 68 + "╣")
        print(f"║  LLM Provider: {llm_provider[:51]}" + " " * max(0, 52 - len(llm_provider[:51])) + "║")
        print("╚" + "═" * 68 + "╝")
        
        # ── Step 4: Verify stored data ───────────────────────────────
        print()
        logger.info("━━━ STEP 4: Verifying stored data ━━━")
        
        with open("market_data.json", "r") as f:
            stored = json.load(f)
        
        print(f"  📊 Trends stored       : {len(stored.get('trends', []))}")
        print(f"  🎨 Design references   : {len(stored.get('design_references', []))}")
        print(f"  🧩 UI patterns         : {len(stored.get('ui_patterns', []))}")
        print(f"  📈 Demand scores       : {len(stored.get('demand_scores', []))}")
        print(f"  📋 Design briefs       : {len(stored.get('design_briefs', []))}")
        
        # Update generation metadata
        stored["generation_metadata"] = {
            "generation_number": 1,
            "started_at": stored.get("generation_metadata", {}).get("started_at"),
            "completed_at": datetime.now().isoformat(),
            "status": "completed",
            "duration_seconds": round(elapsed, 2),
            "pipeline_id": pipeline_id
        }
        with open("market_data.json", "w") as f:
            json.dump(stored, f, indent=4)
        
        # ── Step 5: Save full brief to separate file ─────────────────
        brief_output_path = "storage/generation_1_brief.json"
        os.makedirs("storage", exist_ok=True)
        with open(brief_output_path, "w") as f:
            json.dump({
                "generation": 1,
                "timestamp": datetime.now().isoformat(),
                "pipeline_id": pipeline_id,
                "duration_seconds": round(elapsed, 2),
                "result": result
            }, f, indent=2)
        logger.info(f"📄 Full brief saved → {brief_output_path}")
        
        # ── Step 6: LLM Gateway Stats ───────────────────────────────
        from core.llm_gateway import llm_gateway
        stats = llm_gateway.get_stats()
        print()
        logger.info("━━━ STEP 5: LLM Gateway Statistics ━━━")
        print(f"  🦙 LLaMA calls   : {stats.get('llama_calls', 0)} (avg {stats.get('avg_llama_time', 0)}s)")
        print(f"  ✨ Gemini calls   : {stats.get('gemini_calls', 0)} (avg {stats.get('avg_gemini_time', 0)}s)")
        print(f"  🔄 Dual calls    : {stats.get('dual_calls', 0)}")
        print(f"  ❌ LLaMA fails   : {stats.get('llama_failures', 0)}")
        print(f"  ❌ Gemini fails   : {stats.get('gemini_failures', 0)}")

        print()
        print("═" * 70)
        print("  🎉 FIRST GENERATION COMPLETE — Data collection successful!")
        print("  📁 Data stored in: market_data.json")
        print(f"  📄 Full brief at: {brief_output_path}")
        print("═" * 70)
        print()
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print()
        print("╔" + "═" * 68 + "╗")
        print("║  ❌ FIRST GENERATION FAILED" + " " * 41 + "║")
        print("╠" + "═" * 68 + "╣")
        err_str = str(e)[:60]
        print(f"║  Error: {err_str}" + " " * max(0, 59 - len(err_str)) + "║")
        print(f"║  Duration: {elapsed:.2f}s" + " " * max(0, 55 - len(f"{elapsed:.2f}s")) + "║")
        print("╚" + "═" * 68 + "╝")
        
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(run_first_generation())
    sys.exit(0 if success else 1)
