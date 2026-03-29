# MCP Brain Architecture

This system acts as the central orchestrator for an automated template production platform. It functions as an **AI-driven product factory**.

## Workflow Flow
1. **API Trigger**: The API receives a request (e.g., `/pipeline/start`).
2. **Orchestrator**: The central `Orchestrator` initializes the setup and triggers the Task Queue / Pipeline Engine.
3. **Pipeline Engine**: Executes jobs logically across stages (e.g., Market Research -> Generation -> Testing -> Publishing).
4. **Agents**: The engine delegates actual cognitive and execution tasks to specific Agents (LLM coding, web scraping, rendering tests).
5. **Storage**: Agents interface with the Storage modules for saving intermediate artifacts, syncing them locally, or pushing final versions to the cloud.
6. **Monitoring & Events**: At every granular step, the Event Bus emits `status_updates` which the Monitoring system logs and analyzes for metrics functionality.

## Phase 3.5 — Screenshot-to-Code integration

MCP Brain can optionally generate a UI **directly from a screenshot** by delegating to the local `screenshot-to-code` service (repo: `D:\Vision\screenshot-to-code`).

### How it fits the system
- **Input**: a screenshot upload (PNG/JPEG/WebP)
- **Generation**: MCP Brain calls `screenshot-to-code` over WebSocket (`/generate-code`) and receives generated code variants
- **Artifact**: MCP Brain stores the generated result in `mcp-brain/generated_templates/<template_name>/index.html`
- **Preview**: the existing preview server serves a real `index.html` when present (otherwise it falls back to its synthetic preview)

### API surface
- `POST /generator/from-screenshot` — upload screenshot → generate code → save template → return preview URL
- `POST /generator/from-url` — visit URL → record video + deep analysis → generate code → save template → return preview URL

## Phase 4 — Deep Site Analyzer

The **Deep Site Analyzer** (`services/deep_site_analyzer.py`) is a comprehensive Playwright-based module that captures every visual and structural aspect of a website, producing rich JSON data packages that dramatically improve downstream template generation quality.

### What it captures (10 categories)
1. **CSS Variables** — All custom properties on `:root`
2. **Computed Styles** — Exact `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `borderRadius`, `boxShadow`, `padding`, `margin` for body, h1-h3, p, nav, footer, buttons, cards, links
3. **Font Analysis** — `@font-face` declarations + `document.fonts` API (family, weight, style, stretch)
4. **Color Palette** — Background, text, border, accent colors with hex/rgb values and usage context
5. **Sections** — Component type inference (hero, features, pricing, CTA, blog, FAQ, etc.) with bounding boxes, headings, descriptions, and CTAs
6. **Animations** — CSS `@keyframes`, `transition` properties, `transform` matrices, canvas animation detection
7. **Layouts** — `display` (flex/grid/block), `flex-direction`, `gap`, `grid-template-columns`, `align-items`, `justify-content`
8. **Navigation & Footer** — Links, logo text, CTA buttons, footer columns, copyright
9. **Images & Assets** — `<img>` inventory, SVG count, canvas count, icon library detection (Material, Font Awesome, Lucide, etc.)
10. **Scroll Screenshots** — Screenshots at regular scroll intervals to capture scroll-triggered reveal animations

### Integration points
- **`design_scraper.py`** — `scrape_live_website()` uses DeepSiteAnalyzer when a `reference_url` is provided in trend data, with automatic fallback to basic scraping
- **`website_capture.py`** — `capture_website_video()` accepts a `deep_analyze=True` flag to run DeepSiteAnalyzer alongside video recording
- **`routes_generator.py`** — `/generator/from-url` enables `deep_analyze=True` for all URL-based captures
- **`trend_analyzer.py`** — Receives the enriched data (fonts, colors, sections, animations) for more accurate Gemini analysis

