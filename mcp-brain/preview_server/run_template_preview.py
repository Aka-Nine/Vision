"""
Template Preview Server — Phase 3.5 Module
═══════════════════════════════════════════
Serves generated templates for live preview in the browser.
Runs as a lightweight HTTP server on port 4000.

Usage:
    python preview_server/run_template_preview.py [template_name]

Endpoints:
    GET /                            → List all templates
    GET /template-preview/{name}     → Live preview of a template
    GET /template-preview/{name}/raw → Serve template raw files
"""

import os
import sys
import json
import time
import logging
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolve paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "generated_templates"
REGISTRY_PATH = TEMPLATES_DIR / "template_registry.json"


def load_registry():
    """Load the template registry."""
    if REGISTRY_PATH.is_file():
        try:
            return json.loads(REGISTRY_PATH.read_text())
        except json.JSONDecodeError:
            return []
    return []


def render_index_page(registry):
    """Generate the template listing page."""
    cards = ""
    for tmpl in registry:
        name = tmpl.get("template_name", "unknown")
        version = tmpl.get("version", "1.0")
        framework = tmpl.get("framework", "react")
        style = tmpl.get("style_theme", "dark")
        sections = tmpl.get("sections", [])
        generated_at = tmpl.get("generated_at", tmpl.get("generated_date", ""))
        source_brief = tmpl.get("source_brief", "—")
        component_count = tmpl.get("components", 0)
        valid = tmpl.get("validation", {}).get("valid", False)

        status_color = "#10b981" if valid else "#ef4444"
        status_label = "✓ Valid" if valid else "✗ Invalid"

        cards += f"""
        <a href="/template-preview/{name}" class="card">
          <div class="card-header">
            <h2>{name}</h2>
            <span class="version">v{version}</span>
          </div>
          <div class="card-tags">
            <span class="tag tag-framework">{framework}</span>
            <span class="tag tag-style">{style}</span>
            <span class="tag" style="background:{status_color}20;color:{status_color}">{status_label}</span>
          </div>
          <div class="card-meta">
            <p><strong>Sections:</strong> {', '.join(sections[:5])}</p>
            <p><strong>Components:</strong> {component_count} | <strong>Brief:</strong> {source_brief}</p>
            <p class="date">{generated_at}</p>
          </div>
        </a>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MCP Brain — Template Preview Server</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: #070c16;
      color: #f1f5f9;
      min-height: 100vh;
      padding: 2rem;
    }}
    .header {{
      text-align: center;
      margin-bottom: 3rem;
    }}
    .header h1 {{
      font-size: 2.5rem;
      font-weight: 700;
      background: linear-gradient(135deg, #60a5fa, #a78bfa, #ec4899);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }}
    .header p {{ color: #64748b; }}
    .badge {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #a78bfa;
      margin-bottom: 0.5rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
    }}
    .card {{
      background: #0f1827;
      border: 1px solid #1e2d45;
      border-radius: 1rem;
      padding: 1.5rem;
      text-decoration: none;
      color: inherit;
      transition: all 0.3s;
    }}
    .card:hover {{
      border-color: #3b82f6;
      transform: translateY(-4px);
      box-shadow: 0 16px 32px rgba(0,0,0,0.4);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }}
    .card-header h2 {{
      font-size: 1.15rem;
      font-weight: 600;
    }}
    .version {{
      font-size: 0.8rem;
      font-weight: 700;
      color: #3b82f6;
      background: rgba(59,130,246,0.15);
      padding: 0.2rem 0.6rem;
      border-radius: 100px;
    }}
    .card-tags {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}
    .tag {{
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.2rem 0.6rem;
      border-radius: 100px;
      text-transform: uppercase;
    }}
    .tag-framework {{ background: rgba(16,185,129,0.15); color: #6ee7b7; }}
    .tag-style {{ background: rgba(139,92,246,0.15); color: #c4b5fd; }}
    .card-meta {{ color: #64748b; font-size: 0.85rem; line-height: 1.8; }}
    .card-meta strong {{ color: #94a3b8; }}
    .date {{ color: #475569; font-size: 0.75rem; margin-top: 0.5rem; }}
    .empty {{
      text-align: center;
      color: #475569;
      padding: 4rem;
      font-size: 1.2rem;
    }}
  </style>
</head>
<body>
  <div class="header">
    <span class="badge">Phase 3.5 · Preview Server</span>
    <h1>Template Preview</h1>
    <p>Live preview of generated templates — localhost:4000</p>
  </div>
  <div class="grid">
    {cards if cards else '<div class="empty">No templates generated yet. Run POST /generator/build first.</div>'}
  </div>
</body>
</html>"""


def render_preview_page(name, tmpl_meta):
    """Generate the iframe preview page for a specific template."""
    version = tmpl_meta.get("version", "1.0") if tmpl_meta else "?"
    framework = tmpl_meta.get("framework", "react") if tmpl_meta else "?"
    sections = tmpl_meta.get("sections", []) if tmpl_meta else []
    source_brief = tmpl_meta.get("source_brief", "—") if tmpl_meta else "—"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Preview: {name}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', sans-serif; background: #070c16; color: #f1f5f9; }}
    .toolbar {{
      position: fixed; top: 0; left: 0; right: 0;
      height: 56px;
      background: #0f1827;
      border-bottom: 1px solid #1e2d45;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem;
      z-index: 1000;
    }}
    .toolbar-left {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}
    .toolbar a {{
      color: #3b82f6;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 600;
    }}
    .toolbar a:hover {{ color: #60a5fa; }}
    .toolbar h2 {{ font-size: 1rem; font-weight: 600; }}
    .toolbar-meta {{
      display: flex;
      gap: 0.75rem;
      font-size: 0.75rem;
    }}
    .toolbar-meta span {{
      background: #1e2d45;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      color: #94a3b8;
    }}
    .preview-frame {{
      position: fixed;
      top: 56px; left: 0; right: 0; bottom: 0;
      border: none;
      width: 100%;
      height: calc(100vh - 56px);
      background: white;
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <div class="toolbar-left">
      <a href="/">← Back</a>
      <h2>{name}</h2>
    </div>
    <div class="toolbar-meta">
      <span>v{version}</span>
      <span>{framework}</span>
      <span>{source_brief}</span>
      <span>{len(sections)} sections</span>
    </div>
  </div>
  <iframe class="preview-frame" src="/template-preview/{name}/raw/index.html"></iframe>
</body>
</html>"""


def render_static_html_preview(name, tmpl_dir):
    """
    Generate a self-contained static HTML preview of the template
    by reading the generated JSX and rendering as styled HTML.
    """
    spec_path = tmpl_dir / "template_spec.json"
    layout_path = tmpl_dir / "layout.json"

    spec = {}
    if spec_path.is_file():
        try:
            spec = json.loads(spec_path.read_text())
        except Exception:
            pass

    layout = {"sections": []}
    if layout_path.is_file():
        try:
            layout = json.loads(layout_path.read_text())
        except Exception:
            pass

    theme = spec.get("style", {}).get("theme", "dark")
    is_dark = theme == "dark"
    glass = spec.get("style", {}).get("glass", False)

    # Theme colors
    if is_dark:
        bg = "#030712"
        card_bg = "rgba(255,255,255,0.05)" if glass else "#111827"
        card_border = "rgba(255,255,255,0.1)" if glass else "#1f2937"
        text_primary = "#f9fafb"
        text_secondary = "#9ca3af"
        accent = "#6366f1"
        accent_light = "#818cf8"
        gradient_from = "#312e81"
        gradient_to = "#1e1b4b"
    else:
        bg = "#ffffff"
        card_bg = "#f3f4f6"
        card_border = "#e5e7eb"
        text_primary = "#111827"
        text_secondary = "#6b7280"
        accent = "#4f46e5"
        accent_light = "#6366f1"
        gradient_from = "#eef2ff"
        gradient_to = "#e0e7ff"

    sections_html = ""
    for s in layout.get("sections", []):
        key = s.get("key", "unknown")
        comp = s.get("component", key)
        title = key.replace("_", " ").title()

        if key == "hero":
            sections_html += f"""
            <section style="padding:6rem 2rem;text-align:center;position:relative;overflow:hidden;
                            background:linear-gradient(135deg, {gradient_from}40, {gradient_to}20, transparent);">
              <h1 style="font-size:3.5rem;font-weight:800;margin-bottom:1.5rem;
                         background:linear-gradient(135deg,{accent_light},{accent});
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                Build AI Products Faster
              </h1>
              <p style="color:{text_secondary};font-size:1.2rem;max-width:600px;margin:0 auto 2.5rem;">
                Transform your ideas into production-ready templates powered by market intelligence.
              </p>
              <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
                <button style="background:{accent};color:white;border:none;padding:0.9rem 2rem;border-radius:0.75rem;
                               font-size:1rem;font-weight:600;cursor:pointer;transition:transform 0.2s;">Get Started</button>
                <button style="background:transparent;color:{text_primary};border:1px solid {card_border};
                               padding:0.9rem 2rem;border-radius:0.75rem;font-size:1rem;font-weight:600;
                               cursor:pointer;backdrop-filter:blur(10px);">View Demo</button>
              </div>
            </section>"""
        elif key == "features":
            features = [
                ("📊", "Market Intelligence", "AI-powered trend analysis from multiple data sources."),
                ("⚡", "Auto Generation", "Convert briefs into production-ready UI templates instantly."),
                ("✅", "Smart Validation", "Automated code checking ensures every template works."),
            ]
            feature_cards = ""
            for icon, ftitle, fdesc in features:
                feature_cards += f"""
                <div style="background:{card_bg};border:1px solid {card_border};border-radius:1rem;padding:2rem;
                            {'backdrop-filter:blur(16px);' if glass else ''}transition:transform 0.2s;">
                  <div style="font-size:2.5rem;margin-bottom:1rem;">{icon}</div>
                  <h3 style="font-size:1.1rem;font-weight:600;color:{text_primary};margin-bottom:0.5rem;">{ftitle}</h3>
                  <p style="color:{text_secondary};font-size:0.9rem;">{fdesc}</p>
                </div>"""
            sections_html += f"""
            <section style="padding:5rem 2rem;">
              <div style="max-width:72rem;margin:0 auto;">
                <h2 style="font-size:2.5rem;font-weight:700;color:{text_primary};text-align:center;margin-bottom:3rem;">
                  Powerful Features
                </h2>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;">
                  {feature_cards}
                </div>
              </div>
            </section>"""
        elif key == "pricing":
            plans = [
                ("Starter", "$29", "/mo", ["5 Templates", "Basic Support", "Community"], False),
                ("Pro", "$79", "/mo", ["Unlimited Templates", "Priority Support", "API Access", "Custom Branding"], True),
                ("Enterprise", "$199", "/mo", ["Everything in Pro", "SSO & SAML", "Dedicated Manager", "SLA"], False),
            ]
            plan_cards = ""
            for pname, price, period, feats, highlight in plans:
                border_c = accent if highlight else card_border
                bg_c = f"{accent}15" if highlight else card_bg
                feats_html = "".join(f'<li style="color:{text_secondary};padding:0.4rem 0;">✓ {f}</li>' for f in feats)
                plan_cards += f"""
                <div style="background:{bg_c};border:{'2px' if highlight else '1px'} solid {border_c};
                            border-radius:1rem;padding:2rem;display:flex;flex-direction:column;
                            {'backdrop-filter:blur(16px);' if glass else ''}">
                  <h3 style="font-size:1.1rem;font-weight:600;color:{text_primary};margin-bottom:0.5rem;">{pname}</h3>
                  <div style="margin-bottom:1.5rem;">
                    <span style="font-size:2.5rem;font-weight:700;color:{text_primary};">{price}</span>
                    <span style="color:{text_secondary};">{period}</span>
                  </div>
                  <ul style="list-style:none;flex:1;margin-bottom:1.5rem;">{feats_html}</ul>
                  <button style="background:{accent if highlight else 'transparent'};color:{'white' if highlight else text_primary};
                                 border:1px solid {border_c};padding:0.75rem;border-radius:0.75rem;font-weight:600;
                                 cursor:pointer;width:100%;">Get Started</button>
                </div>"""
            sections_html += f"""
            <section style="padding:5rem 2rem;">
              <div style="max-width:72rem;margin:0 auto;">
                <h2 style="font-size:2.5rem;font-weight:700;color:{text_primary};text-align:center;margin-bottom:3rem;">
                  Simple Pricing
                </h2>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;">
                  {plan_cards}
                </div>
              </div>
            </section>"""
        elif key == "testimonials":
            testimonials = [
                ("Sarah Chen", "CTO at TechFlow", "This platform cut our design-to-code time by 80%. Absolutely game-changing."),
                ("Marcus Rivera", "Lead Designer", "The AI-generated templates are surprisingly polished — our clients love them."),
            ]
            test_cards = ""
            for tname, trole, ttext in testimonials:
                test_cards += f"""
                <div style="background:{card_bg};border:1px solid {card_border};border-radius:1rem;padding:2rem;
                            {'backdrop-filter:blur(16px);' if glass else ''}">
                  <p style="color:{text_secondary};font-size:1.05rem;font-style:italic;margin-bottom:1.5rem;">"{ttext}"</p>
                  <p style="font-weight:600;color:{text_primary};">{tname}</p>
                  <p style="color:{text_secondary};font-size:0.85rem;">{trole}</p>
                </div>"""
            sections_html += f"""
            <section style="padding:5rem 2rem;">
              <div style="max-width:64rem;margin:0 auto;">
                <h2 style="font-size:2.5rem;font-weight:700;color:{text_primary};text-align:center;margin-bottom:3rem;">
                  What People Say
                </h2>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem;">
                  {test_cards}
                </div>
              </div>
            </section>"""
        elif key == "cta":
            sections_html += f"""
            <section style="padding:5rem 2rem;text-align:center;
                            background:linear-gradient(135deg, {gradient_from}30, {gradient_to}20);">
              <h2 style="font-size:2.5rem;font-weight:700;color:{text_primary};margin-bottom:1rem;">
                Ready to Ship Faster?
              </h2>
              <p style="color:{text_secondary};font-size:1.1rem;margin-bottom:2rem;">
                Join thousands of teams building with AI-powered templates.
              </p>
              <button style="background:{accent};color:white;border:none;padding:0.9rem 2.5rem;border-radius:0.75rem;
                             font-size:1rem;font-weight:600;cursor:pointer;">Start Building Now</button>
            </section>"""
        elif key == "footer":
            cols = [
                ("Product", ["Features", "Pricing"]),
                ("Company", ["About", "Blog"]),
                ("Resources", ["Docs", "Support"]),
                ("Legal", ["Privacy", "Terms"]),
            ]
            col_html = ""
            for ctitle, links in cols:
                links_html = "".join(f'<li><a href="#" style="color:{text_secondary};text-decoration:none;">{l}</a></li>' for l in links)
                col_html += f"""
                <div>
                  <h4 style="font-weight:600;color:{text_primary};margin-bottom:1rem;">{ctitle}</h4>
                  <ul style="list-style:none;line-height:2;">{links_html}</ul>
                </div>"""
            sections_html += f"""
            <footer style="padding:3rem 2rem;border-top:1px solid {card_border};">
              <div style="max-width:72rem;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;">
                {col_html}
              </div>
              <div style="max-width:72rem;margin:2rem auto 0;padding-top:2rem;border-top:1px solid {card_border};
                          text-align:center;color:{text_secondary};font-size:0.85rem;">
                © 2026 MCP Brain. All rights reserved.
              </div>
            </footer>"""
        else:
            # Enhanced generic renderer for unknown sections based on keywords
            if "video" in key:
                sections_html += f"""
                <section style="padding:6rem 2rem;text-align:center;background:{card_bg};border-top:1px solid {card_border};border-bottom:1px solid {card_border};">
                  <div style="max-width:800px;margin:0 auto;">
                    <h2 style="font-size:2.2rem;font-weight:700;color:{text_primary};margin-bottom:1.5rem;">{title}</h2>
                    <div style="aspect-ratio:16/9;background:#000;border-radius:1rem;display:flex;align-items:center;justify-content:center;
                                border:1px solid {card_border};box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);">
                      <div style="width:80px;height:80px;border-radius:50%;background:{accent};display:flex;align-items:center;justify-content:center;cursor:pointer;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
                      </div>
                    </div>
                  </div>
                </section>"""
            elif "carousel" in key or "slider" in key:
                sections_html += f"""
                <section style="padding:6rem 2rem;overflow:hidden;">
                  <h2 style="font-size:2.2rem;font-weight:700;color:{text_primary};text-align:center;margin-bottom:3rem;">{title}</h2>
                  <div style="display:flex;gap:1.5rem;padding:1rem 2rem;width:200%;transform:translateX(-10%);">
                    {"".join(f'<div style="width:400px;height:250px;background:{card_bg};border:1px solid {card_border};border-radius:1rem;flex-shrink:0;"></div>' for _ in range(5))}
                  </div>
                </section>"""
            elif "cards" in key or "grid" in key or "feature" in key:
                sections_html += f"""
                <section style="padding:6rem 2rem;background:linear-gradient(to bottom, transparent, {card_bg}50);">
                  <div style="max-width:1200px;margin:0 auto;">
                    <div style="text-align:center;margin-bottom:4rem;">
                      <h2 style="font-size:2.5rem;font-weight:800;color:{text_primary};margin-bottom:1rem;">{title}</h2>
                      <p style="color:{text_secondary};max-width:600px;margin:0 auto;font-size:1.1rem;">Discover the capabilities of the {title.lower()} module built for high performance.</p>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem;">
                      {"".join(f'<div style="background:{card_bg};border:1px solid {card_border};border-radius:1rem;height:200px;padding:2rem;"></div>' for _ in range(6))}
                    </div>
                  </div>
                </section>"""
            else:
                sections_html += f"""
                <section style="padding:6rem 2rem;text-align:center;border-top:1px dotted {card_border};">
                  <div style="max-width:800px;margin:0 auto;background:{card_bg};border:1px solid {card_border};border-radius:1rem;padding:4rem 2rem;">
                    <span style="font-family:monospace;font-size:0.8rem;color:{accent};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1rem;display:block;">Component / {key}</span>
                    <h2 style="font-size:2.5rem;font-weight:800;color:{text_primary};margin-bottom:1rem;">{title}</h2>
                    <p style="color:{text_secondary};font-size:1.1rem;">Dynamic content block placeholder for the <strong>{key}</strong> layout specification.</p>
                  </div>
                </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} — Preview</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: {bg};
      color: {text_primary};
      -webkit-font-smoothing: antialiased;
    }}
    button:hover {{ transform: scale(1.03); }}
  </style>
</head>
<body>
  {sections_html}
</body>
</html>"""


class TemplatePreviewHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for the preview server."""

    def do_GET(self):
        registry = load_registry()

        if self.path == "/" or self.path == "":
            self._send_html(render_index_page(registry))

        elif self.path.startswith("/template-preview/"):
            parts = self.path.split("/")
            # /template-preview/{name}
            if len(parts) == 3:
                name = parts[2]
                tmpl_meta = next((t for t in registry if t.get("template_name") == name), None)
                self._send_html(render_preview_page(name, tmpl_meta))

            # /template-preview/{name}/raw/{filepath}
            elif len(parts) >= 5 and parts[3] == "raw":
                name = parts[2]
                tmpl_dir = TEMPLATES_DIR / name
                file_subpath = "/".join(parts[4:])

                # Prefer dist/ if present (real Vite build output)
                dist_dir = tmpl_dir / "dist"
                if dist_dir.is_dir():
                    # Map /raw/index.html -> dist/index.html and /raw/assets/... -> dist/assets/...
                    target = dist_dir / file_subpath
                    if target.is_file():
                        content_type, _ = mimetypes.guess_type(str(target))
                        self.send_response(200)
                        self.send_header("Content-Type", content_type or "application/octet-stream")
                        self.end_headers()
                        self.wfile.write(target.read_bytes())
                    else:
                        self.send_error(404, f"File not found in dist/: {file_subpath}")
                    return

                if file_subpath == "index.html":
                    # If a real index.html exists (e.g. static HTML output), serve it.
                    # However, if it's a Vite React app without a dist dir, we must serve 
                    # the static HTML preview because the raw index.html relies on Vite.
                    real_index = tmpl_dir / "index.html"
                    is_vite_react = (tmpl_dir / "src" / "main.jsx").is_file() or (tmpl_dir / "src" / "main.tsx").is_file()
                    
                    if real_index.is_file() and not is_vite_react:
                        content_type, _ = mimetypes.guess_type(str(real_index))
                        self.send_response(200)
                        self.send_header("Content-Type", content_type or "text/html; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(real_index.read_bytes())
                    else:
                        # Otherwise, serve our synthetic static HTML preview.
                        self._send_html(render_static_html_preview(name, tmpl_dir))
                else:
                    # Serve actual file
                    file_path = tmpl_dir / file_subpath
                    if file_path.is_file():
                        content_type, _ = mimetypes.guess_type(str(file_path))
                        self.send_response(200)
                        self.send_header("Content-Type", content_type or "application/octet-stream")
                        self.end_headers()
                        self.wfile.write(file_path.read_bytes())
                    else:
                        self.send_error(404, f"File not found: {file_subpath}")
            else:
                self.send_error(404, "Not found")
        else:
            self.send_error(404, "Not found")

    def _send_html(self, html: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[Preview] {args[0]}")


def main():
    port = 4000
    server = HTTPServer(("0.0.0.0", port), TemplatePreviewHandler)
    print(f"\n{'='*60}")
    print(f"  MCP Brain — Template Preview Server")
    print(f"  http://localhost:{port}")
    print(f"  Templates: {TEMPLATES_DIR}")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPreview server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
