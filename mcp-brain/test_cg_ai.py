import asyncio
import logging
import json
from template_generator.component_generator import ComponentGenerator

logging.basicConfig(level=logging.INFO)

async def test_ai():
    gen = ComponentGenerator()
    
    cfg = {"heading": "Global Header", "description": "test", "cta_texts": []}
    style = gen._resolve_style_classes({"theme": "dark", "glass": True})
    anim = gen._resolve_animation_props({})
    
    from core.llm_gateway import llm_gateway
    print("Testing Gateway Config...")
    
    await llm_gateway._check_ollama()
    llm_gateway._init_gemini()
    print("Gemini Available:", llm_gateway._gemini_available)
    
    # Let's peek into component generator internals...
    # import it from instance
    import sys
    from template_generator.component_generator import _generate_component_ai
    # Wait, _generate_component_ai is nested inside the generate method. 
    # Let me just run a direct llm query via llm_gateway.
    
    prompt = """You are an elite, design-obsessed React & Tailwind CSS developer.
You are tasked with generating a FULLY FINISHED, production-ready React component named GlobalHeader for the 'GLOBAL_HEADER' section..."""
    
    from core.llm_gateway import LLMProvider, LLMTaskType

    res = await llm_gateway.query(prompt, task_type=LLMTaskType.CONTENT_WRITING, provider=LLMProvider.GEMINI_CLOUD, json_mode=False)
    
    print("\nRESULT:")
    print(res)
    print("\nSTATS:")
    print(llm_gateway.get_stats())

asyncio.run(test_ai())
