import json
import glob
import os
import asyncio
from agents.template_generator_agent import TemplateGeneratorAgent

async def main():
    with open('market_data.json', encoding='utf-8') as f:
        data = json.load(f)
    brief = None
    for b in reversed(data.get('design_briefs', [])):
        if b.get('sections'):
            brief = b
            break
    latest_semantic = None
    files = sorted(glob.glob('storage/semantic_briefs/semantic_brief_*.json'))
    if files:
        # Ignore the mock file "9999999999"
        valid_files = [f for f in files if "9999" not in f]
        if valid_files:
            with open(valid_files[-1], encoding='utf-8') as f:
                latest_semantic = json.load(f)
                
    if not latest_semantic:
        print('No valid semantic brief found, running SemanticContentEngine...')
        from semantic_content_engine.engine import SemanticContentEngine
        engine = SemanticContentEngine()
        latest_semantic = await engine.process(None, data, brief)
    
    if not brief:
        print('No brief found')
        return
        
    print('Starting Template Generation Pipeline with Semantic Content...')
    agent = TemplateGeneratorAgent()
    result = await agent.run({
        'brief': brief,
        'semantic_brief': latest_semantic
    })
    
    if result.get("status") == "success":
        print(f"\\nDone! SaaS Website Project created successfully!")
        print(f"Project directory: {result.get('project_dir')}")
        print(f"Template name: {result.get('template_name')}")
        print(f"Semantic Enriched: {result.get('semantic_enriched')}")
    else:
        print(f"\\nPipeline failed: {result}")

if __name__ == "__main__":
    asyncio.run(main())
