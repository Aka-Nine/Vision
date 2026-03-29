"""
Test the Dual-LLM Gateway — LLaMA (local) + Gemini (cloud)
"""
import asyncio
import json
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

from core.llm_gateway import llm_gateway, LLMTaskType, LLMProvider


async def main():
    print("=" * 60)
    print("  DUAL-LLM GATEWAY TEST")
    print("  LLaMA 3 (local/Ollama) + Gemini 2.5 (cloud)")
    print("=" * 60)

    # Test 1: LLaMA-only (section planning — fast local inference)
    print("\n--- Test 1: LLaMA LOCAL — Section Planning ---")
    result = await llm_gateway.query(
        prompt='Plan the sections for a "Crypto Dashboard" mobile app. Return JSON with keys: "sections" (list of section names), "layout_type" (string).',
        task_type=LLMTaskType.SECTION_PLANNING,
        json_mode=True,
    )
    print(f"Provider: {result.get('provider_used')}")
    print(f"Time: {result.get('time_seconds', 'N/A')}s")
    if isinstance(result.get('result'), dict):
        print(f"Sections: {json.dumps(result['result'], indent=2)[:300]}")
    else:
        print(f"Result: {str(result.get('result', 'None'))[:300]}")

    # Test 2: DUAL mode (brief generation — LLaMA draft → Gemini refine)
    print("\n--- Test 2: DUAL — Design Brief Generation ---")
    result2 = await llm_gateway.query(
        prompt='''Generate a design brief for an "AI Analytics Dashboard" SaaS product. 
Return JSON with: "product_type", "target_market", "style", "sections" (list), "animation_type", "demand_score".''',
        task_type=LLMTaskType.BRIEF_GENERATION,
        json_mode=True,
    )
    print(f"Provider: {result2.get('provider_used')}")
    if result2.get('llama_draft'):
        print(f"LLaMA draft: {json.dumps(result2['llama_draft'], indent=2)[:200]}...")
    if result2.get('gemini_refined'):
        print(f"Gemini refined: {json.dumps(result2['gemini_refined'], indent=2)[:200]}...")
    if not result2.get('gemini_refined') and result2.get('result'):
        print(f"Final result: {json.dumps(result2['result'], indent=2)[:300]}")

    # Test 3: Code validation (LLaMA only)
    print("\n--- Test 3: LLaMA LOCAL — Code Validation ---")
    sample_code = '''export default function HeroSection() {
  return (
    <section className="py-32 text-center bg-gray-950">
      <h1 className="text-5xl font-bold text-white">Build AI Products</h1>
    </section>
  );
}'''
    result3 = await llm_gateway.query(
        prompt=f'Review this React component for issues:\n{sample_code}\nReturn JSON: {{"valid": bool, "issues": []}}',
        task_type=LLMTaskType.VALIDATION,
        json_mode=True,
    )
    print(f"Provider: {result3.get('provider_used')}")
    print(f"Time: {result3.get('time_seconds', 'N/A')}s")
    print(f"Result: {json.dumps(result3.get('result', {}), indent=2)[:300]}")

    # Print stats
    print("\n--- Gateway Statistics ---")
    stats = llm_gateway.get_stats()
    print(json.dumps(stats, indent=2))
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
