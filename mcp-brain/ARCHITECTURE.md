# 🏗️ Vision Architecture: Reassessment & The Control Plane

## 1. The Current State: "The Fragile Relay Race"

The initial architecture of the **MCP Brain** Pipeline was designed as a linear sequence of Python scripts:

**`Intelligence Agent -> Generator -> Screenshot-to-code -> Validator`**

### The Core Dysfunction (Why it breaks)
Because AI agents are non-deterministic, a simple relay race drops the baton constantly. 
- The `DeepSiteAnalyzer` extracts actual text, descriptions, and CTA buttons from the live website. However, when passing the reference image to the Vision model to generate the UI layout, the vision model hallucinates placeholder text (e.g., "Build AI Products Faster") because it can't read the small text in the screenshot. 
- The Python script (`ComponentGenerator.generate()`) tries to forcefully string-replace the output arrays to inject the original headings. This hack causes sections to desync and layouts to break.
- The `CodeValidator` strictly demands a layout score of `14` (meaning it literally string-matches for libraries like GSAP and Lenis). If the `Screenshot-to-code` model perfectly replicates the layout using native Flexbox but forgets to write `gsap.to()`, the `CodeValidator` rejects it entirely. 

Because the pipeline is linear, **there is no Supervisor** watching the *context* to manually correct it. The system crashes instead of learning to fix the missing code.

---

## 2. The Solution: The Vision Control Plane (State Database)

To build a true **Agentic Swarm**, we must abandon the linear Python scripts and introduce a **Global State Manager** (e.g., PostgreSQL, Redis, or a Graph Database). This is called the **Control Plane**.

Instead of agents writing and passing `.json` files locally, they push and pull state updates directly from the Database.

### Architectural Upgrade: The Database Supervisor

#### A. Granular Status Tracking (The Watchdog)
Every template generation is tracked as a row in the database:
`Template ID: #1042` | `Status: AWAITING_ANIMATION_PASS` | `Aesthetic_Score: 8/14`

If an agent crashes (e.g., Playwright hits a Cloudflare block and times out), the Supervisor observes: 
*"Warning: Template #1042 has been stuck in `AWAITING_ANIMATION_PASS` for 5 minutes. Restarting the Animation Agent using Playwright Stealth Proxies."*

#### B. The "Fixer" Workflow (Agentic Self-Healing)
Because the state tracks *why* something failed, it dispatches specialized agents to fix it via **LangGraph Cycles**.
1. The **Vision Agent** finishes the React layout. Database updates to `Status: VALIDATING`.
2. The **Code Validator** runs and flags it: *"Failed. Score 8/14. Missing GSAP."*
3. **Old Architecture**: The pipeline dies. Error printed to terminal.
4. **New Database Architecture**: The Database changes the status to `NEEDS_ANIMATION_REVISION` and pages a specialized **AnimationAgent**. The AnimationAgent exclusively looks at the raw source code, injects GSAP timelines into the React `.jsx` files recursively (via `multi_replace_file_content` style tools), tests it, and sends it back to `VALIDATING`.

#### C. Centralized Payload Management (Semantic Injection)
Instead of hacking React JSX strings in Python:
1. The `DeepSiteAnalyzer` data (colors, fonts, headings, descriptions) is inserted directly into the database: `db.template_data.insert({ title: "Experience liftoff", ctas: ["Buy"] })`.
2. The `Screenshot-to-code` model is instructed to output explicit placeholder variables (`<h1>{db.data.hero.title}</h1>`).
3. The Vite React app pulls its layout copy naturally upon compilation, replacing the variable cleanly and securely.

---

## 3. Recommended Tech Stack for v2.0 (The Scale-Up)

To implement this Control Plane properly, the next commit phase should integrate:

1. **State Database (PostgreSQL / SQLite)**: The single source of truth for the Agent swarm to log execution times, prompt states, and error payloads.
2. **LangGraph (by LangChain)**: To construct explicit cyclic graphs for the agents. If the `CodeValidator` node fails the template, the graph automatically loops the state back to the `Coding` node with the error message attached, forcing the agent to rewrite its code until the benchmark passes.
3. **Temporal.io or Inngest**: A specialized execution wrapper. If an agent hits a rate limit or API failure, Temporal automatically pauses the workflow, saves the complete context state, and retries the exact function without abandoning the entire generation sequence.
4. **PM2 Process Manager**: Spawning `npm run dev` async across 5 different template folders leaks memory and hangs terminal ports (`[3457, 4000, 5000, 5001]`). A root-level `ecosystem.config.js` is required to clean, boot, and tear down the generated test servers dynamically.
