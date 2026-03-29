# 👁️ Vision: MCP Brain Orchestrator

**MCP-Brain** is the central command center for the **Vision AI Product Factory**. It is designed to autonomously scout the internet for high-end design trends, generate sophisticated system architectures, and coordinate a swarm of code-generating agents to build production-ready, highly-animated React applications without human intervention.

## 🚀 The Ecosystem

The `Vision` project is a fully autonomous pipeline composed of deeply integrated microservices:

- **MCP Brain (Orchestrator)**: Handles internet crawling (via Playwright `DeepSiteAnalyzer`), runs the LLM agents (Gemini 2.5 Pro), parses trend data, and validates the final aesthetic output.
- **Screenshot-to-code (The Visual Engine)**: Takes reference snapshots collected by the Brain and translates pure pixels into fundamental React layouts.
- **Reference Benchmarks (`animation-showcase`, `antigravity-website`)**: The "ground truth" repositories. The pipeline rigidly holds generated templates against these benchmarks, enforcing the inclusion of **GSAP**, **Lenis Smooth Scrolling**, and **Framer Motion** before marking a template as "deployable."

---

## 🏗️ How it Works (The Pipeline)

1. **Market Intelligence**: The Brain scouts the internet matching your query. It boots headless browsers to pull computed DOM styles, fonts, color palettes, and heavy text payloads natively from live websites.
2. **Brief Generation**: Gemini analyzes the raw data payloads and generates a structured JSON Design Brief detailing the target audience, animation strategy, and UI component layout.
3. **Template Factory**: The Python orchestrator scaffolds a Vite + React + Tailwind project. It forces premium aesthetic dependencies (`gsap`, `lenis`, `canvas`) into the `package.json`.
4. **Data Alignment**: The Brain intercepts the generated UI and strictly maps the literal, real-world text headings and CTA buttons crawled from the live site directly into the React components to avoid generic LLM placeholders.
5. **Aesthetic Validation**: The final code is parsed. If the aesthetic score drops below `14` (e.g., missing particle effects or glassmorphism), the pipeline rejects the template.

---

## 📈 System Architecture & The "Control Plane" Transition

The architecture is currently migrating from a **Linear Python Pipeline** to a **Cyclic Agentic State Machine**. 

Due to the unpredictable nature of AI vision models (e.g., forgetting to inject GSAP, missing a CTA), a linear "relay race" architecture is too fragile for scale. 

**Next Phase (v2.0):** The introduction of the **Control Plane Database**. 
Instead of agents passing unstructured JSON files, every template deployment will be tracked by a robust State Database (PostgreSQL). If the `ValidatorAgent` rejects the code, the pipeline will not crash; the Database will route the code back to an `AnimationAgent` to explicitly repair the missing GSAP syntax until it passes the benchmark.

👉 **Read the full [Architectural Reassessment & Database Blueprint](./ARCHITECTURE.md) for details on the control plane upgrade.**

---

## 🛠️ Tech Stack
- **Languages**: Python (Backend), TypeScript/JSX (Frontend)
- **Frameworks**: FastAPI, Playwright (Scraper), Vite, Tailwind CSS
- **AI Models**: Gemini 2.5 Pro, Claude 3.5 Sonnet (Vision)
- **Animation Benchmarks**: GSAP, Lenis Smooth Scroll, Framer Motion