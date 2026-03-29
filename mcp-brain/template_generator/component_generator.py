"""
Component Generator — Generative UI Factory
Uses Gemini AI to dynamically generate rich, fully-fledged React/Tailwind
components for every section in the layout. Falls back to static blueprints
only if Gemini is completely unavailable.
"""

import os
import json
import logging
import textwrap
import sys

logger = logging.getLogger(__name__)

# Top-level Generative UI LLM Caller — Supports OpenRouter, Groq, and Gemini
def _call_external_llm(prompt: str, max_retries: int = 3) -> str:
    """Dynamically route to OpenRouter, Groq, or Gemini based on env keys."""
    import time
    import urllib.request
    import json
    
    api_key_or = os.environ.get("OPENROUTER_API_KEY", "")
    api_key_groq = os.environ.get("GROQ_API_KEY", "")
    api_key_gemini = os.environ.get("GEMINI_API_KEY", "")

    if not api_key_gemini:
        from app.config import settings
        api_key_gemini = settings.gemini_api_key

    def parse_markdown(text: str) -> str:
        import re
        text = text.strip()
        # Find the first code block (jsx, javascript, or generic)
        match = re.search(r"```(?:jsx|javascript|tsx)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()
        # Fix common LLM import hallucinations
        text = text.replace("@lucide/react", "lucide-react")
        return text.strip()

    # ── 1. OPENROUTER PIPELINE (Highest Priority)
    if api_key_or:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("  OpenRouter call attempt %d ...", attempt)
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key_or}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": "meta-llama/llama-3.1-70b-instruct",
                        "messages": [{"role": "user", "content": prompt}]
                    }).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["choices"][0]["message"]["content"]
                    return parse_markdown(text)
            except Exception as e:
                logger.warning("  OpenRouter failed: %s", e)
                time.sleep(2)
    
    # ── 2. GROQ PIPELINE
    if api_key_groq:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("  Groq call attempt %d ...", attempt)
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key_groq}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}]
                    }).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["choices"][0]["message"]["content"]
                    return parse_markdown(text)
            except Exception as e:
                logger.warning("  Groq failed: %s", e)
                time.sleep(2)

    # ── 3. GEMINI PIPELINE
    if api_key_gemini:
        try:
            import google.generativeai as genai
            import re
            genai.configure(api_key=api_key_gemini)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info("  Gemini call attempt %d ...", attempt)
                    response = model.generate_content(prompt)
                    return parse_markdown(response.text)
                except Exception as e:
                    err_str = str(e)
                    m = re.search(r"seconds:\s*(\d+)", err_str)
                    wait = int(m.group(1)) + 2 if m else (attempt * 15)
                    wait = min(wait, 60)
                    if attempt < max_retries:
                        logger.warning("  Gemini Rate limit. Waiting %ds...", wait)
                        time.sleep(wait)
                    else:
                        logger.error("  Gemini completely failed: %s", err_str[:120])
        except Exception as e:
            logger.error("Gemini init failed: %s", e)
            
    logger.error("❌ ALL AI PROVIDERS FAILED.")
    return ""


# ── Component blueprints ────────────────────────────────────────────
# Each blueprint is a function(style_classes, animation_props) → JSX string

def _hero_jsx(cls, anim, section_cfg=None):
    if section_cfg is None: section_cfg = {}
    heading = section_cfg.get("heading") or "Build AI Products Faster"
    desc = section_cfg.get("description") or "Transform your ideas into production-ready templates powered by market intelligence."
    ctas = section_cfg.get("cta_texts", ["Get Started", "View Demo"])
    
    btn1 = ctas[0] if len(ctas) > 0 else "Get Started"
    btn2 = ctas[1] if len(ctas) > 1 else "View Demo"

    return textwrap.dedent(f"""\
        import React, {{ useEffect, useRef }} from 'react';
        {anim['import']}

        export default function HeroSection() {{
          const canvasRef = useRef(null);

          useEffect(() => {{
            const canvas = canvasRef.current;
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            let w, h, particles = [];
            const resize = () => {{ w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; }};
            window.addEventListener('resize', resize);
            resize();

            for(let i=0; i<50; i++) particles.push({{x: Math.random()*w, y: Math.random()*h, v: Math.random()*0.5}});
            
            const draw = () => {{
              ctx.clearRect(0,0,w,h);
              ctx.fillStyle = 'rgba(255,255,255,0.5)';
              particles.forEach(p => {{
                p.y -= p.v; if (p.y < 0) p.y = h;
                ctx.beginPath(); ctx.arc(p.x, p.y, 1.5, 0, Math.PI*2); ctx.fill();
              }});
              requestAnimationFrame(draw);
            }};
            draw();
            return () => window.removeEventListener('resize', resize);
          }}, []);

          return (
            <{anim['wrapper']}>
              <section className="{{cls['section']}} py-32 text-center relative overflow-hidden min-h-screen flex items-center justify-center">
                <canvas ref={{canvasRef}} className="absolute inset-0 z-0 opacity-50 pointer-events-none" />
                <div className="absolute inset-0 {{cls['bg_gradient']}} z-0"></div>
                <div className="relative z-10 max-w-5xl mx-auto px-6">
                  <h1 className="text-5xl md:text-8xl font-extrabold {{cls['heading']}} mb-6 leading-tight">
                    {heading}
                  </h1>
                  <p className="{{cls['subtext']}} text-xl md:text-2xl max-w-3xl mx-auto mb-12">
                    {desc}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-6 justify-center">
                    <button className="{{cls['btn_primary']}} px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105 shadow-xl">
                      {btn1}
                    </button>
                    <button className="{{cls['btn_secondary']}} px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105 shadow-[0_0_15px_rgba(255,255,255,0.1)] backdrop-blur-md">
                      {btn2}
                    </button>
                  </div>
                </div>
              </section>
            </{anim['wrapper_close']}>
          );
        }}
    """)


def _features_jsx(cls, anim, section_cfg=None):
    if section_cfg is None: section_cfg = {}
    heading = section_cfg.get("heading") or "Powerful Features"
    return textwrap.dedent(f"""\
        import React from 'react';
        {anim['import']}

        const features = [
          {{ title: 'Advanced Integration', description: 'Deep architecture combining native frameworks.', icon: '⚡' }},
          {{ title: 'Performant Rendering', description: 'Zero layout shift using hybrid methodologies.', icon: '🎯' }},
          {{ title: 'Data Abstraction', description: 'Robust state management spanning complex layers.', icon: '🔒' }},
        ];

        export default function FeaturesSection() {{
          return (
            <section className="{{cls['section']}} py-24 relative z-10 border-t border-white/5">
              <div className="max-w-6xl mx-auto px-6 text-center">
                <h2 className="text-4xl md:text-6xl font-bold {{cls['heading']}} mb-16">
                  {heading}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {{features.map((f, i) => (
                    <{anim['wrapper']} key={{i}}>
                      <div className="{{cls['card']}} p-10 rounded-3xl transition-all hover:scale-[1.02] hover:shadow-2xl">
                        <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-3xl mb-6 mx-auto">{{f.icon}}</div>
                        <h3 className="text-2xl font-semibold {{cls['heading']}} mb-4">{{f.title}}</h3>
                        <p className="{{cls['subtext']}} text-lg leading-relaxed">{{f.description}}</p>
                      </div>
                    </{anim['wrapper_close']}>
                  ))}}
                </div>
              </div>
            </section>
          );
        }}
    """)


def _pricing_jsx(cls, anim, section_cfg=None):
    if section_cfg is None: section_cfg = {}
    heading = section_cfg.get("heading") or "Simple Pricing"
    return textwrap.dedent(f"""\
        import React from 'react';
        {anim['import']}

        const plans = [
          {{ name: 'Starter', price: '$29', period: '/mo', features: ['5 Templates', 'Basic Support', 'Community Access'], highlight: false }},
          {{ name: 'Pro', price: '$79', period: '/mo', features: ['Unlimited Templates', 'Priority Support', 'API Access', 'Custom Branding'], highlight: true }},
          {{ name: 'Enterprise', price: '$199', period: '/mo', features: ['Everything in Pro', 'SSO & SAML', 'Dedicated Manager', 'SLA'], highlight: false }},
        ];

        export default function PricingSection() {{
          return (
            <section className="{{cls['section']}} py-32 relative z-10 border-t border-white/5">
              <div className="max-w-6xl mx-auto px-6">
                <h2 className="text-4xl md:text-6xl font-bold {{cls['heading']}} text-center mb-20">
                  {heading}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {{plans.map((plan, i) => (
                    <{anim['wrapper']} key={{i}}>
                      <div className={{`${{plan.highlight ? '{cls['card_highlight']}' : '{cls['card']}'}} p-10 rounded-3xl flex flex-col hover:-translate-y-2 transition-transform`}}>
                        <h3 className="text-2xl font-semibold {{cls['heading']}} mb-4">{{plan.name}}</h3>
                        <div className="flex items-end mb-8">
                          <span className="text-5xl font-bold {{cls['heading']}}">{{plan.price}}</span>
                          <span className="{{cls['subtext']}} ml-2">{{plan.period}}</span>
                        </div>
                        <ul className="flex-1 space-y-4 mb-10">
                          {{plan.features.map((feat, j) => (
                            <li key={{j}} className="{{cls['subtext']}} flex items-center gap-3">
                              <span className="text-indigo-400">✓</span> {{feat}}
                            </li>
                          ))}}
                        </ul>
                        <button className="{{plan.highlight ? '{cls['btn_primary']}' : '{cls['btn_secondary']}'}} w-full py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105">
                          Get Started
                        </button>
                      </div>
                    </{anim['wrapper_close']}>
                  ))}}
                </div>
              </div>
            </section>
          );
        }}
    """)


def _testimonials_jsx(cls, anim, section_cfg=None):
    if section_cfg is None: section_cfg = {}
    heading = section_cfg.get("heading") or "What People Say"
    return textwrap.dedent(f"""\
        import React from 'react';
        {anim['import']}

        const testimonials = [
          {{ name: 'Sarah Chen', role: 'CTO at TechFlow', text: 'This platform cut our design-to-code time by 80%. Absolutely game-changing.' }},
          {{ name: 'Marcus Rivera', role: 'Lead Designer', text: 'The AI-generated templates are surprisingly polished — our clients love them.' }},
        ];

        export default function TestimonialsSection() {{
          return (
            <section className="{{cls['section']}} py-32 relative z-10 border-t border-white/5">
              <div className="max-w-5xl mx-auto px-6">
                <h2 className="text-4xl md:text-6xl font-bold {{cls['heading']}} text-center mb-20">
                  {heading}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {{testimonials.map((t, i) => (
                    <{anim['wrapper']} key={{i}}>
                      <div className="{{cls['card']}} p-10 rounded-3xl">
                        <p className="{{cls['subtext']}} text-xl italic mb-8">"{{t.text}}"</p>
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-full bg-white/20"></div>
                          <div>
                            <p className="font-semibold {{cls['heading']}} text-lg">{{t.name}}</p>
                            <p className="{{cls['subtext']}}">{{t.role}}</p>
                          </div>
                        </div>
                      </div>
                    </{anim['wrapper_close']}>
                  ))}}
                </div>
              </div>
            </section>
          );
        }}
    """)


def _cta_jsx(cls, anim, section_cfg=None):
    if section_cfg is None: section_cfg = {}
    heading = section_cfg.get("heading") or "Ready to Ship Faster?"
    desc = section_cfg.get("description") or "Join thousands of teams building with AI-powered templates."
    ctas = section_cfg.get("cta_texts", ["Start Building Now"])
    btn = ctas[0] if len(ctas) > 0 else "Start Building Now"
    return textwrap.dedent(f"""\
        import React from 'react';
        {anim['import']}

        export default function CTASection() {{
          return (
            <{anim['wrapper']}>
              <section className="{{cls['section']}} py-40 text-center relative z-10">
                <div className="absolute inset-0 bg-indigo-900/10 backdrop-blur-3xl z-0"></div>
                <div className="max-w-4xl mx-auto px-6 relative z-10 bg-white/5 border border-white/10 p-20 rounded-[3rem] shadow-2xl backdrop-blur-lg">
                  <h2 className="text-4xl md:text-6xl font-extrabold {{cls['heading']}} mb-8">
                    {heading}
                  </h2>
                  <p className="{{cls['subtext']}} text-xl md:text-2xl mb-12">
                    {desc}
                  </p>
                  <button className="{{cls['btn_primary']}} px-12 py-5 rounded-2xl text-xl font-bold transition-all hover:scale-105 shadow-2xl">
                    {btn}
                  </button>
                </div>
              </section>
            </{anim['wrapper_close']}>
          );
        }}
    """)


def _footer_jsx(cls, _anim, section_cfg=None):
    return textwrap.dedent(f"""\
        import React from 'react';

        export default function Footer() {{
          return (
            <footer className="{{cls['section']}} py-20 border-t border-white/10 relative z-10">
              <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-12">
                <div>
                  <h4 className="font-bold {{cls['heading']}} mb-6 text-lg">Product</h4>
                  <ul className="space-y-4 {{cls['subtext']}}">
                    <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                    <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold {{cls['heading']}} mb-6 text-lg">Company</h4>
                  <ul className="space-y-4 {{cls['subtext']}}">
                    <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                    <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold {{cls['heading']}} mb-6 text-lg">Resources</h4>
                  <ul className="space-y-4 {{cls['subtext']}}">
                    <li><a href="#" className="hover:text-white transition-colors">Docs</a></li>
                    <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold {{cls['heading']}} mb-6 text-lg">Legal</h4>
                  <ul className="space-y-4 {{cls['subtext']}}">
                    <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                    <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                  </ul>
                </div>
              </div>
              <div className="max-w-7xl mx-auto px-6 mt-16 pt-8 border-t border-white/5 text-center {{cls['subtext']}}">
                <p>&copy; 2026 Crafted dynamically by MCP Brain AI. Extracted from Market Intelligence.</p>
              </div>
            </footer>
          );
        }}
    """)


# ── Component Registry ──────────────────────────────────────────────
COMPONENT_BLUEPRINTS = {
    "hero": ("HeroSection", _hero_jsx),
    "features": ("FeaturesSection", _features_jsx),
    "pricing": ("PricingSection", _pricing_jsx),
    "testimonials": ("TestimonialsSection", _testimonials_jsx),
    "cta": ("CTASection", _cta_jsx),
    "footer": ("Footer", _footer_jsx),
}


def _generic_section_jsx(component_name, section_key, cls, anim, section_cfg=None):
    """Fallback generator for sections without a dedicated blueprint."""
    if section_cfg is None: section_cfg = {}
    
    # Use real scraped content from the Antigravity Deep Analysis if available
    raw_heading = section_cfg.get("heading")
    title = raw_heading if raw_heading else section_key.replace("_", " ").title()
    desc = section_cfg.get("description")
    desc_html = f'<p className="{{cls[\'subtext\']}} text-xl max-w-2xl mx-auto mb-10">{desc}</p>' if desc else ""
    
    ctas = section_cfg.get("cta_texts", [])
    ctas_html = ""
    if ctas and len(ctas) > 0:
        ctas_html = f'<div className="flex gap-4 justify-center mt-8">'
        for ctext in ctas[:2]: # Max 2 generic buttons
            ctas_html += f'<button className="{{cls[\'btn_primary\']}} px-8 py-3 rounded-xl font-semibold">{ctext}</button>'
        ctas_html += '</div>'
    
    # Generate high-end UI components based on section keywords, matching the static fallback UI
    if "video" in section_key.lower():
        content_jsx = f"""
                <div className="max-w-5xl mx-auto px-6">
                  <h2 className="text-3xl md:text-5xl font-bold {cls['heading']} text-center mb-10">{title}</h2>
                  {desc_html}
                  <div className="aspect-video bg-black rounded-2xl flex border {cls['border']} items-center justify-center shadow-2xl overflow-hidden relative group cursor-pointer mt-8">
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
                    <div className="w-24 h-24 rounded-full bg-indigo-600/90 flex items-center justify-center transition-transform group-hover:scale-110 z-10 backdrop-blur-md">
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
                    </div>
                  </div>
                  {ctas_html}
                </div>"""
                
    elif "carousel" in section_key.lower() or "slider" in section_key.lower():
        content_jsx = f"""
                <div className="w-full overflow-hidden">
                  <h2 className="text-3xl md:text-5xl font-bold {cls['heading']} text-center mb-6">{title}</h2>
                  <div className="text-center mb-12">{desc_html}</div>
                  <div className="flex gap-6 px-10 w-[200vw] -translate-x-[10vw]">
                    {{[1,2,3,4,5].map(i => (
                      <div key={{i}} className="w-[450px] h-[300px] {cls['card']} rounded-2xl shrink-0 p-8 flex flex-col justify-end">
                        <h3 className="{cls['heading']} text-xl font-bold">Showcase {{i}}</h3>
                      </div>
                    ))}}
                  </div>
                  {ctas_html}
                </div>"""
                
    elif "cards" in section_key.lower() or "grid" in section_key.lower() or "feature" in section_key.lower():
        content_jsx = f"""
                <div className="max-w-7xl mx-auto px-6">
                  <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold {cls['heading']} mb-4">{title}</h2>
                    {desc_html}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {{[1,2,3,4,5,6].map(i => (
                      <div key={{i}} className="{cls['card']} h-[250px] p-8 rounded-2xl transition-all hover:-translate-y-2 hover:shadow-2xl flex flex-col justify-between">
                         <div className="w-12 h-12 rounded-full bg-white/10 mb-4"></div>
                         <h3 className="{cls['heading']} text-xl font-bold">Feature {{i}}</h3>
                      </div>
                    ))}}
                  </div>
                  {ctas_html}
                </div>"""
                
    else:
        content_jsx = f"""
                <div className="max-w-4xl mx-auto px-6 text-center">
                  <div className="{cls['card']} p-16 rounded-3xl">
                    <span className="font-mono text-xs text-indigo-400 tracking-widest uppercase mb-4 block">Component / {section_key}</span>
                    <h2 className="text-4xl md:text-6xl font-extrabold {cls['heading']} mb-6">
                      {title}
                    </h2>
                    {desc_html}
                    {ctas_html}
                  </div>
                </div>"""

    return textwrap.dedent(f"""\
        import React from 'react';
        {anim['import']}

        export default function {component_name}() {{
          return (
            <{anim['wrapper']}>
              <section className="{cls['section']} py-32 border-t border-b border-white/5 relative z-10">
{content_jsx}
              </section>
            </{anim['wrapper_close']}>
          );
        }}
    """)


class ComponentGenerator:
    """Generate JSX component files for each section in the layout."""

    async def generate(self, layout: dict, spec: dict, output_dir: str) -> list:
        """
        Parameters
        ----------
        layout : dict     — output of LayoutBuilder.build()
        spec   : dict     — parsed template specification
        output_dir : str  — project root to write into

        Returns
        -------
        list[dict] — metadata for every generated component
        """
        components_dir = os.path.join(output_dir, "src", "components")
        os.makedirs(components_dir, exist_ok=True)

        style_classes = self._resolve_style_classes(spec.get("style", {}))
        anim_props = self._resolve_animation_props(spec.get("animations", {}))

        # AST Data
        spatial_rules = spec.get("_spatial_rules", {})
        component_specs = spec.get("_component_specs", {})
        content_slots = spec.get("_content_slots", {})
        variation = spec.get("_variation", {})

        # Phase 2.5: Inject semantic content from the enriched spec
        semantic_content = spec.get("_semantic_content", {})
        if semantic_content:
            logger.info("Phase 2.5: Injecting semantic content for %d section types", len(semantic_content))
            for section_cfg in layout.get("sections", []):
                section_key = section_cfg.get("key", "")
                if section_key in semantic_content:
                    sem = semantic_content[section_key]
                    if sem.get("heading"):
                        section_cfg["heading"] = sem["heading"]
                    if sem.get("description"):
                        section_cfg["description"] = sem["description"]
                    if sem.get("cta_texts"):
                        section_cfg["cta_texts"] = sem["cta_texts"]
                    logger.debug("  → Injected semantic content for section: %s", section_key)
        else:
            # Legacy fallback: Best-effort deep analysis injection from files
            import glob as _glob
            latest_analysis = None
            for analysis_file in sorted(_glob.glob("storage/deep_analysis/**/*_analysis.json", recursive=True)):
                try:
                    with open(analysis_file, "r", encoding="utf-8") as file:
                        data = json.load(file)
                    if "sections" in data and len(data["sections"]) > 0:
                        latest_analysis = data
                except Exception as e:
                    logger.warning(f"Error reading {analysis_file}: {e}")

            if latest_analysis:
                logger.info(f"Legacy: Injecting scraped data from deep analysis: {latest_analysis.get('url')}")
                deep_sections = latest_analysis["sections"]
                for i, section_cfg in enumerate(layout.get("sections", [])):
                    if i < len(deep_sections):
                        deep_sec = deep_sections[i]
                        if deep_sec.get("heading"):
                            section_cfg["heading"] = deep_sec.get("heading")
                        if deep_sec.get("description"):
                            section_cfg["description"] = deep_sec.get("description")
                        if deep_sec.get("cta_texts"):
                            section_cfg["cta_texts"] = deep_sec.get("cta_texts", [])

        # ── AI Generative component creation ──────────────────────────
        import asyncio

        async def _generate_component_ai(section_cfg, comp_name, s_key, style_cls, anim):
            # Extract basic content
            heading = section_cfg.get("heading", s_key.replace("_", " ").title())
            desc = section_cfg.get("description", "")
            ctas = section_cfg.get("cta_texts", [])

            # ── Inject UI AST Constraints ──
            spatial = spatial_rules.get(s_key, {})
            c_spec = component_specs.get(s_key, {})
            
            # Extract content slots tailored for this section
            section_slots = {k: v for k, v in content_slots.items() if k.startswith(f"{s_key}.")}
            slot_descriptions = "\\n".join(
                f"- {k}: {v.get('value')} (Type: {v.get('type')}, Tone: {v.get('tone')})"
                for k, v in section_slots.items()
            ) if section_slots else "None"

            # Dynamic style instructions based on AST Variation Engine
            color_mode = variation.get("color_mode", "standard")
            layout_variant = variation.get("layout_variant", "standard")
            anim_richness = variation.get("animation_intensity", "standard")

            style_guide = "Clean, modern SaaS default."
            if color_mode == "neon":
                style_guide = "Neon accents. Use rich gradients, intense shadows (`shadow-[0_0_40px_rgba(...,0.3)]`), and vibrant tech styling."
            elif color_mode == "flat":
                style_guide = "Flat minimalist design. Hard borders, solid colors, sharp spacing. ZERO gradients. Neo-brutalist influence."

            spatial_guide = ""
            if spatial:
                spatial_guide = f"\\n# SPATIAL & LAYOUT CONSTRAINTS (MANDATORY)\\n"
                spatial_guide += f"- Height: {spatial.get('height')}\\n"
                spatial_guide += f"- Padding Top: {spatial.get('padding_top')}, Padding Bottom: {spatial.get('padding_bottom')}\\n"
                spatial_guide += f"- Alignment/Flow: {spatial.get('alignment')}\\n"
                if spatial.get("position") == "sticky":
                    spatial_guide += "- Position: THIS IS A STICKY NAV. Use `fixed top-0 w-full z-50 backdrop-blur-md`\\n"

            # Component structural spec
            comp_structure = ""
            if c_spec:
                comp_structure = f"\\n# COMPONENT STRUCTURE TREE (MANDATORY)\\nYou must build the component using exactly these sub-elements:\\n"
                for child in c_spec.get("children", []):
                    comp_structure += f"- <{child.get('tag', 'div')}> id={child.get('id')} ({child.get('component_name')})\\n"
            
            prompt = f"""You are an elite, design-obsessed React & Tailwind CSS developer.
You are tasked with generating a FULLY FINISHED, production-ready React component named {comp_name} for the '{s_key}' section of a premium SaaS website.
THIS IS NOT A WIREFRAME. You must output the final, complex, functional, and visually stunning code.

# CORE CONTENT TO EXPAND UPON
Core Heading: "{heading}"
Core Description: "{desc}"
CTAs: {', '.join(ctas)}

# STRUCTURED CONTENT SLOTS (If provided, inject these directly into the UI):
{slot_descriptions}

*(CRITICAL: Expand upon the provided content! Write rich, persuasive marketing copywriting, bullet points, sub-captions, and details to flesh out a massive, highly detailed component section.)*

# STRICT DESIGN LANGUAGE & VARIATION ENFORCEMENT
{style_guide}
Layout Variant: {layout_variant}. Build structure respecting this variant style.
Animation Tier: {anim_richness}. If rich, use Framer Motion extensively.
{spatial_guide}
{comp_structure}

# 🚀 YOUR CAPABILITIES (MANDATORY TO USE):
1. **REAL IMAGES:** If the section needs imagery, YOU MUST ADD <img> tags with real placeholders! (e.g. `https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop`).
2. **RICH INTERACTIONS:** Implement actual React state (`useState`) to build interactive elements (tabs, accordions, toggles) if the section allows it.
3. **ADVANCED ANIMATIONS:** Use `framer-motion` heavily. Use `initial`, `whileInView`, and `viewport={{{{ once: true }}}}` to fade up elements. Use `whileHover` for interactive scale effects.
4. **SPACING & LAYOUT:** Do not build flat, boring rows. Use CSS Grids, overlapping absolute position elements, background blur (`backdrop-blur-xl`), and floating elements.

# INSTRUCTIONS
1. Output ONLY RAW JSX CODE. Completely self-contained. No markdown wrappers (` ```jsx `). 
2. Write perfectly formatted, massive, highly-detailed Tailwind classes.
3. Import React, `useState`, and `import {{ motion }} from 'framer-motion'`. DO NOT import any icon libraries like 'lucide-react' or 'react-icons' because they will crash the build. Use raw inline <svg> code for all icons instead!
4. Export the component as `export default function {comp_name}() {{ ... }}`
"""
            logger.info("🤖 Generating Fully-Fledged AI Component: %s ...", comp_name)

            # Use direct external LLM call in a thread pool (blocking API → async)
            loop = asyncio.get_event_loop()
            jsx = await loop.run_in_executor(None, _call_external_llm, prompt)

            if not jsx or len(jsx.strip()) < 80:
                logger.error(
                    "❌ AI returned empty/short JSX for %s (got %d chars). "
                    "Check GEMINI_API_KEY. Falling back to static blueprint.",
                    comp_name, len(jsx) if jsx else 0
                )
                if s_key in COMPONENT_BLUEPRINTS:
                    _, blueprint_fn = COMPONENT_BLUEPRINTS[s_key]
                    return blueprint_fn(style_cls, anim, section_cfg)
                return _generic_section_jsx(comp_name, s_key, style_cls, anim, section_cfg)

            logger.info("✅ AI generated %d chars for %s", len(jsx), comp_name)
            return jsx.strip()

        # Generate components SEQUENTIALLY to respect free-tier rate limits
        generated = []
        sections = layout.get("sections", [])
        for idx, section_cfg in enumerate(sections):
            section_key = section_cfg["key"]
            component_name = section_cfg["component"]

            logger.info("[%d/%d] Generating: %s", idx + 1, len(sections), component_name)
            jsx = await _generate_component_ai(section_cfg, component_name, section_key, style_classes, anim_props)

            file_path = os.path.join(components_dir, f"{component_name}.jsx")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(jsx)

            generated.append({
                "component": component_name,
                "section": section_key,
                "path": f"src/components/{component_name}.jsx",
            })
            logger.info("  ✅ Written → %s", file_path)

            # Rate-limit guard: wait 3s between API calls (free tier = ~2 RPM)
            if idx < len(sections) - 1:
                await asyncio.sleep(3)

        # Also generate the landing page that imports all components
        await self._generate_page(layout, components_dir, output_dir, style_classes)

        return generated

    # ── Style resolution ────────────────────────────────────────────
    def _resolve_style_classes(self, style: dict) -> dict:
        theme = style.get("theme", "dark")
        glass = style.get("glass", False)

        if theme == "dark":
            bg = "bg-gray-950"
            heading = "text-white"
            subtext = "text-gray-400"
            border = "border-white/10"
            card = "bg-white/5 border border-white/10 backdrop-blur-lg" if glass else "bg-gray-900 border border-gray-800"
            card_highlight = "bg-indigo-500/20 border border-indigo-400/30 backdrop-blur-lg" if glass else "bg-indigo-900 border border-indigo-700"
            btn_primary = "bg-indigo-600 hover:bg-indigo-500 text-white"
            btn_secondary = "bg-white/10 hover:bg-white/20 text-white border border-white/10"
            bg_gradient = "bg-gradient-to-br from-indigo-900/40 via-purple-900/20 to-transparent"
        else:
            bg = "bg-white"
            heading = "text-gray-900"
            subtext = "text-gray-600"
            border = "border-gray-200"
            card = "bg-gray-50 border border-gray-200"
            card_highlight = "bg-blue-50 border border-blue-200"
            btn_primary = "bg-blue-600 hover:bg-blue-500 text-white"
            btn_secondary = "bg-gray-100 hover:bg-gray-200 text-gray-900 border border-gray-300"
            bg_gradient = "bg-gradient-to-br from-blue-50 via-indigo-50 to-transparent"

        return {
            "section": bg,
            "heading": heading,
            "subtext": subtext,
            "border": border,
            "card": card,
            "card_highlight": card_highlight,
            "btn_primary": btn_primary,
            "btn_secondary": btn_secondary,
            "bg_gradient": bg_gradient,
        }

    def _resolve_animation_props(self, animations: dict) -> dict:
        anim_type = animations.get("type", "scroll_reveal")
        library = animations.get("library", "framer-motion")

        if library == "framer-motion":
            return {
                "import": "import { motion } from 'framer-motion';",
                "wrapper": 'motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}',
                "wrapper_close": "motion.div",
            }
        return {
            "import": "",
            "wrapper": "div",
            "wrapper_close": "div",
        }

    async def _generate_page(self, layout, components_dir, output_dir, cls):
        """Generate the main LandingPage.jsx that wires all components."""
        pages_dir = os.path.join(output_dir, "src", "pages")
        os.makedirs(pages_dir, exist_ok=True)

        imports = []
        usages = []
        for section_cfg in layout.get("sections", []):
            comp = section_cfg["component"]
            imports.append(f"import {comp} from '../components/{comp}';")
            usages.append(f"        <{comp} />")

        page_jsx = textwrap.dedent("""\
            import React, {{ useEffect }} from 'react';
            import Lenis from 'lenis';
            import gsap from 'gsap';
            {imports}

            export default function LandingPage() {{
              useEffect(() => {{
                // Initialize high-end smooth scrolling and GSAP context
                const lenis = new Lenis({{ duration: 1.2, smoothWheel: true }});
                function raf(time) {{ lenis.raf(time); requestAnimationFrame(raf); }}
                requestAnimationFrame(raf);
                
                // Expose gsap globally for nested components if needed
                window.gsap = gsap;
                
                return () => lenis.destroy();
              }}, []);

              return (
                <main className="min-h-screen {bg}">
            {usages}
                </main>
              );
            }}
        """).format(
            imports="\n".join(imports),
            usages="\n".join(usages),
            bg=cls["section"],
        )

        page_path = os.path.join(pages_dir, "LandingPage.jsx")
        with open(page_path, "w") as f:
            f.write(page_jsx)
        logger.info("Generated page → %s", page_path)
