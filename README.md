

# 👁️ Vision — AI Tools Monorepo

**A collection of cutting-edge AI-powered tools: screenshot-to-code generation, MCP server infrastructure, UI animation showcases, and an Antigravity IDE landing page.**

[![Python](https://img.shields.io/badge/Python-52%25-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-24%25-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-10%25-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org)
[![HTML](https://img.shields.io/badge/HTML-9%25-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org)
[![CSS](https://img.shields.io/badge/CSS-4%25-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-🚧%20Active%20Development-orange?style=for-the-badge)]()

<br/>

> **Vision** is an ongoing AI tooling monorepo experimenting with multimodal LLM capabilities — from converting screenshots directly into production-ready UI code, to building MCP servers that give AI agents real tools, to creating showcase UIs for animation techniques and the Antigravity IDE ecosystem.

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture Diagram](#-architecture-diagram)
- [Monorepo Structure](#-monorepo-structure)
- [Modules](#-modules)
  - [screenshot-to-code](#-screenshot-to-code)
  - [mcp-brain](#-mcp-brain)
  - [animation-showcase](#-animation-showcase)
  - [antigravity-website](#-antigravity-website)
  - [_write_test](#-_write_test)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)

---

## 🔍 Overview

**Vision** is a monorepo housing multiple experimental and production-bound AI tools, all built around the same core theme: **giving AI agents real superpowers** — whether that's eyes (screenshot understanding), hands (MCP tool access), or a voice (landing pages and showcases).

The project is actively developed with an emphasis on:
- **Multimodal AI** — using vision-capable LLMs to understand and reproduce UI designs
- **MCP (Model Context Protocol)** — exposing tools to AI agents via the open standard pioneered by Anthropic
- **Frontend craft** — high-quality CSS animation techniques and TypeScript-first web development
- **Antigravity IDE ecosystem** — building tools and sites for Google's agentic coding IDE

---

## 🏗 Architecture Diagram

> The SVG architecture diagram is included in this repo at `vision-architecture.svg`. Embed it in your README like so:

![vision-architecture](https://github.com/user-attachments/assets/62fe022d-aa45-4048-8697-487a6de4210f)<div align="center">

The diagram covers all 5 architectural layers:
1. **Monorepo Root** — all 5 modules branching from the `Vision/` root
2. **screenshot-to-code** — vision LLM → layout analysis → component generation pipeline
3. **mcp-brain** — MCP server, tool registry, and AI host adapter layer
4. **animation-showcase** — CSS engine + JS controller + browser render pipeline
5. **antigravity-website** — TypeScript frontend → Docker → CDN hosting chain
6. **Shared Infrastructure** — Node.js, Python, TypeScript, Docker, Vite, Git
7. **External AI Integrations** — OpenAI, Anthropic, Gemini, Antigravity IDE, Browser APIs, MCP Protocol

---

## 📁 Monorepo Structure

```
Vision/
│
├── _write_test/                # Write evaluation test harness
│   └── ...                     # Prompt / output eval suite
│
├── animation-showcase/         # CSS & JS animation techniques showcase
│   ├── index.html              # Demo entry point
│   ├── styles/                 # Keyframe, variable, and animation CSS
│   └── scripts/                # Intersection Observer, GSAP controllers
│
├── antigravity-website/        # Antigravity IDE landing page
│   ├── src/                    # TypeScript component source
│   ├── public/                 # Static assets
│   ├── Dockerfile              # Container build for deployment
│   └── package.json            # Frontend dependencies
│
├── mcp-brain/                  # MCP server infrastructure
│   ├── server.py               # MCP server entrypoint (Python)
│   ├── tools/                  # Tool definitions (web, fs, exec, api)
│   ├── transport/              # stdio / HTTP / SSE transport adapters
│   └── schema/                 # JSON schema tool specs
│
├── screenshot-to-code/         # Screenshot → UI code pipeline
│   ├── backend/                # Python FastAPI + vision LLM integration
│   │   ├── main.py             # API entrypoint
│   │   ├── vision.py           # LLM image analysis module
│   │   ├── generator.py        # HTML/CSS/React code generation
│   │   └── requirements.txt    # Python dependencies
│   └── frontend/               # TypeScript drag-drop UI
│       ├── src/                # React components
│       └── package.json        # Frontend dependencies
│
└── package-lock.json           # Root npm lockfile (lockfileVersion 3)
```

---

## 📦 Modules

### 📸 screenshot-to-code

> Convert any screenshot, mockup, or wireframe directly into clean HTML, CSS, or React code using multimodal LLMs.

**How it works:**
1. User uploads an image (PNG/JPG/WebP) via drag-and-drop frontend
2. Image sent to FastAPI backend as `multipart/form-data`
3. Vision LLM (GPT-4o or Claude) analyzes layout, colors, typography, and spacing
4. Code generator emits structured HTML/CSS or JSX output
5. Output displayed in live preview panel with copy/download option

**Pipeline stages:**
```
Image Input → Vision LLM → Layout Analysis → Style Extraction → Component Generation → Code Output
```

**Stack:** Python · FastAPI · OpenAI Vision API / Anthropic Claude · TypeScript · React · Tailwind CSS

**Status:** 🚧 Active development

---

### 🧠 mcp-brain

> A configurable MCP (Model Context Protocol) server that exposes tools to AI agents like Antigravity, Claude Code, and Cursor.

**What is MCP?** The Model Context Protocol is an open standard that lets AI agents call real tools — file system, web, APIs, databases — through a structured JSON schema interface. `mcp-brain` is a custom MCP server implementing this protocol.

**Exposed tools (planned/in-progress):**

| Tool | Description | Transport |
|---|---|---|
| `web_search` | Fetch and scrape live web data | HTTP |
| `file_read` / `file_write` | Read and write project files | stdio |
| `code_exec` | Run shell commands and scripts | stdio |
| `api_bridge` | Connect to external services | HTTP |

**Transport modes:** stdio (local agents) · HTTP + SSE (remote agents)

**Compatible with:** Antigravity IDE · Claude Code · Cursor · Gemini CLI · Any MCP-compliant host

**Stack:** Python · TypeScript · MCP Protocol · JSON Schema · FastAPI

**Status:** 🚧 Core protocol scaffolding underway

---

### 🎬 animation-showcase

> A curated showcase of advanced CSS and JavaScript animation techniques for reference and inspiration.

**Techniques demonstrated:**

| Category | Techniques |
|---|---|
| **CSS-native** | Keyframe animations, custom properties, clip-path morphing, 3D transforms |
| **Scroll-driven** | Intersection Observer triggers, scroll-linked progress |
| **Interaction** | Hover states, focus transitions, micro-interactions |
| **Advanced** | Particle systems, SVG morphing, Lottie JSON playback, Canvas API |
| **Planned** | WebGL shaders, GSAP timeline demos, physics-based spring animations |

**Stack:** HTML5 · CSS3 · Vanilla JS · GSAP · Canvas API · Lottie

**Status:** 🚧 Adding new animations progressively

---

### 🌐 antigravity-website

> A landing page for the Antigravity AI coding IDE ecosystem — Google's agentic Gemini-powered development environment.

**Page sections:**

| Section | Status |
|---|---|
| Hero / headline | 🚧 In progress |
| Feature highlights | 🚧 In progress |
| Live demo embed | 🔮 Planned |
| Pricing tiers | 🔮 Planned |
| CTA / Sign up | 🔮 Planned |
| Blog / Docs links | 🔮 Planned |
| Footer / Legal | 🔮 Planned |

**Deployment:** Containerized via `Dockerfile` — deployable to Vercel, Netlify, or any Docker-compatible host.

**Stack:** TypeScript · Vite · React · Tailwind CSS · Docker

**Status:** 🚧 Early frontend scaffolding

---

### ✏️ _write_test

> Internal test harness for evaluating AI writing and code generation output quality.

Used to benchmark prompt variations, measure output consistency, and validate that LLM responses meet quality bars for other modules in the repo.

**Status:** 🔮 Experimental / internal tooling

---

## 🧰 Tech Stack

### Backend / AI
| Technology | Version | Module | Purpose |
|---|---|---|---|
| **Python** | 3.10+ | screenshot-to-code, mcp-brain | Core runtime |
| **FastAPI** | 0.100+ | screenshot-to-code | REST API framework |
| **Uvicorn** | Latest | screenshot-to-code | ASGI server |
| **OpenAI SDK** | Latest | screenshot-to-code | GPT-4o Vision API |
| **Anthropic SDK** | Latest | mcp-brain | Claude API |
| **Pillow** | 10.x | screenshot-to-code | Image I/O |
| **OpenCV** | 4.x | screenshot-to-code | Image preprocessing |
| **python-dotenv** | Latest | All Python | Env config |

### Frontend
| Technology | Version | Module | Purpose |
|---|---|---|---|
| **TypeScript** | 5.x | antigravity-website, screenshot-to-code | Type-safe JS |
| **React** | 18+ | screenshot-to-code | UI framework |
| **Vite** | 5.x | antigravity-website | Build tool + HMR |
| **Tailwind CSS** | 3.x | All frontend | Utility CSS |
| **GSAP** | 3.x | animation-showcase | Animation library |
| **HTML5 / CSS3** | — | animation-showcase | Native animations |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker** | Container runtime for antigravity-website |
| **Node.js 18+** | JS runtime, npm workspace root |
| **npm v3 (lockfile)** | Package management |
| **Git / GitHub** | Version control, public repo |

### Protocols
| Protocol | Used In | Purpose |
|---|---|---|
| **MCP (stdio)** | mcp-brain | Local agent tool communication |
| **MCP (HTTP/SSE)** | mcp-brain | Remote agent streaming transport |
| **REST / JSON** | screenshot-to-code | Client-server API |
| **JSON Schema** | mcp-brain | Tool definition specs |

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Docker | Latest | `docker --version` |
| npm | 9+ | `npm --version` |

### 1. Clone the Repo

```bash
git clone https://github.com/Aka-Nine/Vision.git
cd Vision
```

### 2. screenshot-to-code

```bash
cd screenshot-to-code/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create .env
echo "OPENAI_API_KEY=your-key-here" > .env

uvicorn main:app --reload
```

Frontend:
```bash
cd ../frontend
npm install && npm run dev
```

### 3. mcp-brain

```bash
cd mcp-brain
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run MCP server (stdio mode for local agents)
python server.py --transport stdio
```

To connect with Antigravity IDE, add to your `mcp.json`:
```json
{
  "mcpServers": {
    "vision-brain": {
      "command": "python",
      "args": ["path/to/Vision/mcp-brain/server.py"]
    }
  }
}
```

### 4. antigravity-website

```bash
cd antigravity-website
npm install
npm run dev
```

Or with Docker:
```bash
docker build -t antigravity-site .
docker run -p 3000:3000 antigravity-site
```

### 5. animation-showcase

No build step needed — open `animation-showcase/index.html` directly in a browser, or serve it:

```bash
cd animation-showcase
npx serve .
```

---

## 🗺 Roadmap

### screenshot-to-code
- [ ] Component-level code generation (React, Vue, Svelte)
- [ ] Multi-frame / multi-page detection
- [ ] Figma export integration
- [ ] Dark/light mode variant generation
- [ ] CSS variable extraction pipeline

### mcp-brain
- [ ] Complete stdio transport implementation
- [ ] HTTP + SSE streaming transport
- [ ] Web search tool (Playwright-based)
- [ ] File system tool (sandboxed read/write)
- [ ] Shell execution tool (scoped)
- [ ] Tool authentication & rate limiting
- [ ] Tool schema auto-generation from Python functions

### animation-showcase
- [ ] WebGL particle system demo
- [ ] GSAP timeline showcase
- [ ] Spring physics animations
- [ ] Scroll-linked progress bars
- [ ] Searchable / filterable demo index

### antigravity-website
- [ ] Complete all page sections
- [ ] Responsive mobile layout
- [ ] CMS integration for blog
- [ ] SEO metadata
- [ ] Lighthouse 90+ score

### Infrastructure (all modules)
- [ ] GitHub Actions CI/CD pipeline
- [ ] Shared TypeScript types package
- [ ] ESLint + Prettier config
- [ ] Jest / Vitest test coverage
- [ ] Environment variable management (dotenv + secrets)
- [ ] Monorepo tooling (Turborepo or nx)

---

## 🤝 Contributing

This is an active personal project — contributions, issues, and ideas welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: describe change"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with curiosity, caffeine, and multimodal LLMs ☕**

*Starring: Python · TypeScript · MCP · OpenAI · Anthropic · Gemini · React · Docker*

</div>
