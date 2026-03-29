"""
Generative UI Website Builder
══════════════════════════════════════════════
Runs the pipeline: Market Intelligence → Semantic Engine → AI Component Generation

This script:
  1. Loads design brief from market_data.json
  2. Generates/loads semantic brief (Context)
  3. Uses your Gemini API key to write completely custom React/Tailwind code on the fly
  4. Outputs the finished project to generated_templates/
"""

import asyncio
import json
import glob
import os
import sys
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s", datefmt="%H:%M:%S")

async def main():
    print("═" * 70)
    print("  🧠 MCP BRAIN — GENERATIVE UI ENGINE")
    print("  Using Gemini API to write custom React + Tailwind code...")
    print("═" * 70)

    # 1. Load latest brief
    with open("market_data.json", encoding="utf-8") as f:
        data = json.load(f)
        brief = [b for b in data.get("design_briefs", []) if b.get("sections")][-1]
    
    # 2. Load latest semantic context
    sem_files = sorted(glob.glob("storage/semantic_briefs/semantic_brief_*.json"))
    with open(sem_files[-1], encoding="utf-8") as f:
        semantic_brief = json.load(f)

    # 3. Trigger robust Generation Pipeline
    from pipelines.template_pipeline import TemplatePipeline
    pipeline = TemplatePipeline()
    
    print("\n  🚀 Starting AI component factory...")
    _, result = await pipeline.run(brief=brief, semantic_brief=semantic_brief)

    if result.get("status") == "success":
        print(f"\n  ✅ Website fully generated using Generative UI!")
        print(f"     Project Folder: {result.get('project_dir')}")
        print("  💡 Run 'npm install' & 'npm run dev' to see the custom AI designs!")
    else:
        print(f"\n  ❌ Generation failed: {result}")

if __name__ == "__main__":
    asyncio.run(main())
