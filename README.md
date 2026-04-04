![vision-architecture](https://github.com/user-attachments/assets/62fe022d-aa45-4048-8697-487a6de4210f)<div align="center">

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

```md
![Vision Architecture]![Uploading vision<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1320" width="1100" height="1320" font-family="'Courier New', Courier, monospace">
  <defs>
    <!-- Background gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#060610;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#0a0a1a;stop-opacity:1"/>
    </linearGradient>

    <!-- Glow filters -->
    <filter id="glowCyan" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowPurple" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowGold" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowGreen" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="8" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <!-- Lane gradients -->
    <linearGradient id="laneBlue" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0ea5e9;stop-opacity:0.12"/>
      <stop offset="100%" style="stop-color:#0ea5e9;stop-opacity:0.03"/>
    </linearGradient>
    <linearGradient id="lanePurple" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#a855f7;stop-opacity:0.12"/>
      <stop offset="100%" style="stop-color:#a855f7;stop-opacity:0.03"/>
    </linearGradient>
    <linearGradient id="laneGold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:0.12"/>
      <stop offset="100%" style="stop-color:#f59e0b;stop-opacity:0.03"/>
    </linearGradient>
    <linearGradient id="laneGreen" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#10b981;stop-opacity:0.12"/>
      <stop offset="100%" style="stop-color:#10b981;stop-opacity:0.03"/>
    </linearGradient>
    <linearGradient id="laneRed" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.12"/>
      <stop offset="100%" style="stop-color:#ef4444;stop-opacity:0.03"/>
    </linearGradient>

    <!-- Node box gradients -->
    <linearGradient id="nodeBlue" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0ea5e9;stop-opacity:0.2"/>
      <stop offset="100%" style="stop-color:#0ea5e9;stop-opacity:0.05"/>
    </linearGradient>
    <linearGradient id="nodePurple" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#a855f7;stop-opacity:0.2"/>
      <stop offset="100%" style="stop-color:#a855f7;stop-opacity:0.05"/>
    </linearGradient>
    <linearGradient id="nodeGold" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:0.2"/>
      <stop offset="100%" style="stop-color:#f59e0b;stop-opacity:0.05"/>
    </linearGradient>
    <linearGradient id="nodeGreen" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#10b981;stop-opacity:0.2"/>
      <stop offset="100%" style="stop-color:#10b981;stop-opacity:0.05"/>
    </linearGradient>
    <linearGradient id="nodeRed" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.2"/>
      <stop offset="100%" style="stop-color:#ef4444;stop-opacity:0.05"/>
    </linearGradient>

    <!-- Arrow markers -->
    <marker id="arrowCyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#0ea5e9" opacity="0.8"/>
    </marker>
    <marker id="arrowPurple" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#a855f7" opacity="0.8"/>
    </marker>
    <marker id="arrowGold" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#f59e0b" opacity="0.8"/>
    </marker>
    <marker id="arrowGreen" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#10b981" opacity="0.8"/>
    </marker>
    <marker id="arrowWhite" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#94a3b8" opacity="0.6"/>
    </marker>

    <!-- Decorative grid pattern -->
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.4"/>
    </pattern>

    <!-- Scan line animation -->
    <linearGradient id="scanLine" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0ea5e9;stop-opacity:0"/>
      <stop offset="50%" style="stop-color:#0ea5e9;stop-opacity:0.04"/>
      <stop offset="100%" style="stop-color:#0ea5e9;stop-opacity:0"/>
    </linearGradient>
  </defs>

  <!-- Base background -->
  <rect width="1100" height="1320" fill="url(#bgGrad)"/>
  <!-- Grid overlay -->
  <rect width="1100" height="1320" fill="url(#grid)" opacity="0.5"/>

  <!-- ══════════════════════════════════════════
       TITLE SECTION
  ══════════════════════════════════════════ -->
  <!-- Title glow orb -->
  <ellipse cx="550" cy="62" rx="280" ry="30" fill="#0ea5e9" opacity="0.07" filter="url(#softGlow)"/>

  <!-- Corner brackets -->
  <path d="M30,20 L30,46 L56,46" fill="none" stroke="#0ea5e9" stroke-width="1.5" opacity="0.6"/>
  <path d="M1070,20 L1070,46 L1044,46" fill="none" stroke="#0ea5e9" stroke-width="1.5" opacity="0.6"/>

  <text x="550" y="44" text-anchor="middle" font-size="26" font-weight="bold" letter-spacing="8" fill="url(#laneBlue)" filter="url(#glowCyan)">
    <tspan fill="#0ea5e9">V</tspan><tspan fill="#38bdf8">I</tspan><tspan fill="#7dd3fc">S</tspan><tspan fill="#0ea5e9">I</tspan><tspan fill="#38bdf8">O</tspan><tspan fill="#7dd3fc">N</tspan>
  </text>
  <text x="550" y="44" text-anchor="middle" font-size="26" font-weight="bold" letter-spacing="8" fill="#0ea5e9" filter="url(#glowCyan)">VISION</text>
  <text x="550" y="62" text-anchor="middle" font-size="10" letter-spacing="4" fill="#334155">AI TOOLS MONOREPO · SYSTEM ARCHITECTURE</text>

  <!-- Divider line -->
  <line x1="30" y1="78" x2="1070" y2="78" stroke="#1e293b" stroke-width="1"/>
  <line x1="30" y1="78" x2="340" y2="78" stroke="#0ea5e9" stroke-width="1" opacity="0.5"/>
  <line x1="760" y1="78" x2="1070" y2="78" stroke="#0ea5e9" stroke-width="1" opacity="0.5"/>

  <!-- Language badges -->
  <rect x="360" y="68" width="68" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <text x="394" y="79" text-anchor="middle" font-size="8" fill="#60a5fa" letter-spacing="0.5">Python 52%</text>
  <rect x="436" y="68" width="78" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <text x="475" y="79" text-anchor="middle" font-size="8" fill="#818cf8" letter-spacing="0.5">TypeScript 24%</text>
  <rect x="522" y="68" width="60" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <text x="552" y="79" text-anchor="middle" font-size="8" fill="#fbbf24" letter-spacing="0.5">JS 10.5%</text>
  <rect x="590" y="68" width="52" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <text x="616" y="79" text-anchor="middle" font-size="8" fill="#f97316" letter-spacing="0.5">HTML 9%</text>
  <rect x="650" y="68" width="48" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <text x="674" y="79" text-anchor="middle" font-size="8" fill="#34d399" letter-spacing="0.5">CSS 4%</text>
  <rect x="706" y="68" width="50" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <text x="731" y="79" text-anchor="middle" font-size="8" fill="#94a3b8" letter-spacing="0.5">Docker 0.1%</text>

  <!-- ══════════════════════════════════════════
       LAYER 1 — MONOREPO ENTRY
  ══════════════════════════════════════════ -->
  <rect x="30" y="92" width="1040" height="106" rx="10" fill="url(#laneBlue)" stroke="#0ea5e9" stroke-width="0.8" opacity="0.9"/>
  <!-- Layer label tab -->
  <rect x="30" y="88" width="190" height="14" rx="3" fill="#0c4a6e"/>
  <text x="125" y="98" text-anchor="middle" font-size="8" letter-spacing="3" fill="#0ea5e9">LAYER 1 · MONOREPO ROOT</text>

  <!-- Root node -->
  <rect x="60" y="106" width="140" height="74" rx="8" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1.2" filter="url(#glowCyan)"/>
  <text x="130" y="128" text-anchor="middle" font-size="16">📦</text>
  <text x="130" y="146" text-anchor="middle" font-size="11" font-weight="bold" fill="#0ea5e9">Vision/</text>
  <text x="130" y="161" text-anchor="middle" font-size="8" fill="#64748b">monorepo root</text>
  <text x="130" y="173" text-anchor="middle" font-size="7.5" fill="#475569">package-lock.json</text>

  <!-- Sub-module nodes row -->
  <!-- _write_test -->
  <rect x="228" y="106" width="148" height="74" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="302" y="128" text-anchor="middle" font-size="14">✏️</text>
  <text x="302" y="146" text-anchor="middle" font-size="10" font-weight="bold" fill="#94a3b8">_write_test/</text>
  <text x="302" y="160" text-anchor="middle" font-size="7.5" fill="#475569">Test harness</text>
  <text x="302" y="172" text-anchor="middle" font-size="7" fill="#334155">write eval suite</text>

  <!-- animation-showcase -->
  <rect x="392" y="106" width="148" height="74" rx="8" fill="#0f172a" stroke="#a855f7" stroke-width="1"/>
  <text x="466" y="128" text-anchor="middle" font-size="14">🎬</text>
  <text x="466" y="146" text-anchor="middle" font-size="10" font-weight="bold" fill="#c084fc">animation-showcase/</text>
  <text x="466" y="160" text-anchor="middle" font-size="7.5" fill="#475569">UI animation demos</text>
  <text x="466" y="172" text-anchor="middle" font-size="7" fill="#334155">HTML / CSS / JS</text>

  <!-- antigravity-website -->
  <rect x="556" y="106" width="148" height="74" rx="8" fill="#0f172a" stroke="#f59e0b" stroke-width="1"/>
  <text x="630" y="128" text-anchor="middle" font-size="14">🌐</text>
  <text x="630" y="146" text-anchor="middle" font-size="10" font-weight="bold" fill="#fcd34d">antigravity-website/</text>
  <text x="630" y="160" text-anchor="middle" font-size="7.5" fill="#475569">AI IDE landing page</text>
  <text x="630" y="172" text-anchor="middle" font-size="7" fill="#334155">TypeScript + HTML</text>

  <!-- mcp-brain -->
  <rect x="720" y="106" width="148" height="74" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1.2" filter="url(#glowGreen)"/>
  <text x="794" y="128" text-anchor="middle" font-size="14">🧠</text>
  <text x="794" y="146" text-anchor="middle" font-size="10" font-weight="bold" fill="#34d399">mcp-brain/</text>
  <text x="794" y="160" text-anchor="middle" font-size="7.5" fill="#475569">MCP server core</text>
  <text x="794" y="172" text-anchor="middle" font-size="7" fill="#334155">Python · TypeScript</text>

  <!-- screenshot-to-code -->
  <rect x="884" y="106" width="158" height="74" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="1.2" filter="url(#glowPurple)"/>
  <text x="963" y="128" text-anchor="middle" font-size="14">📸</text>
  <text x="963" y="146" text-anchor="middle" font-size="10" font-weight="bold" fill="#f87171">screenshot-to-code/</text>
  <text x="963" y="160" text-anchor="middle" font-size="7.5" fill="#475569">Vision → UI pipeline</text>
  <text x="963" y="172" text-anchor="middle" font-size="7" fill="#334155">Python · TypeScript</text>

  <!-- Root arrows to each module -->
  <line x1="200" y1="143" x2="228" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2" marker-end="url(#arrowWhite)"/>
  <line x1="200" y1="143" x2="370" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2"/>
  <line x1="370" y1="143" x2="392" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2" marker-end="url(#arrowWhite)"/>
  <line x1="200" y1="143" x2="534" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2"/>
  <line x1="534" y1="143" x2="556" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2" marker-end="url(#arrowWhite)"/>
  <line x1="200" y1="143" x2="698" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2"/>
  <line x1="698" y1="143" x2="720" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2" marker-end="url(#arrowWhite)"/>
  <line x1="200" y1="143" x2="862" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2"/>
  <line x1="862" y1="143" x2="884" y2="143" stroke="#334155" stroke-width="1" stroke-dasharray="3,2" marker-end="url(#arrowWhite)"/>

  <!-- ══════════════════════════════════════════
       LAYER 2 — SCREENSHOT-TO-CODE MODULE
  ══════════════════════════════════════════ -->
  <rect x="30" y="218" width="510" height="240" rx="10" fill="url(#laneRed)" stroke="#ef4444" stroke-width="0.8" opacity="0.9"/>
  <rect x="30" y="214" width="230" height="14" rx="3" fill="#450a0a"/>
  <text x="145" y="224" text-anchor="middle" font-size="8" letter-spacing="3" fill="#ef4444">LAYER 2 · SCREENSHOT-TO-CODE</text>

  <!-- Input: Screenshot -->
  <rect x="50" y="232" width="120" height="68" rx="7" fill="url(#nodeRed)" stroke="#ef4444" stroke-width="1"/>
  <text x="110" y="252" text-anchor="middle" font-size="13">🖼️</text>
  <text x="110" y="268" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#f87171">Input</text>
  <text x="110" y="282" text-anchor="middle" font-size="7.5" fill="#64748b">Screenshot / mockup</text>
  <text x="110" y="293" text-anchor="middle" font-size="7" fill="#475569">PNG · JPG · WebP</text>

  <!-- Vision Model -->
  <rect x="196" y="232" width="126" height="68" rx="7" fill="url(#nodeRed)" stroke="#ef4444" stroke-width="1"/>
  <text x="259" y="252" text-anchor="middle" font-size="13">👁️</text>
  <text x="259" y="268" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#f87171">Vision LLM</text>
  <text x="259" y="282" text-anchor="middle" font-size="7.5" fill="#64748b">Image understanding</text>
  <text x="259" y="293" text-anchor="middle" font-size="7" fill="#475569">GPT-4o / Claude</text>

  <!-- Code Generator -->
  <rect x="348" y="232" width="170" height="68" rx="7" fill="url(#nodeRed)" stroke="#ef4444" stroke-width="1.2"/>
  <text x="433" y="252" text-anchor="middle" font-size="13">⚙️</text>
  <text x="433" y="268" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#f87171">Code Generator</text>
  <text x="433" y="282" text-anchor="middle" font-size="7.5" fill="#64748b">HTML · CSS · React</text>
  <text x="433" y="293" text-anchor="middle" font-size="7" fill="#475569">TypeScript output</text>

  <!-- Output preview -->
  <rect x="50" y="322" width="460" height="120" rx="7" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
  <text x="280" y="342" text-anchor="middle" font-size="8" letter-spacing="2" fill="#475569">OUTPUT PIPELINE</text>
  <!-- Pipeline steps -->
  <rect x="66" y="352" width="92" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="112" y="373" text-anchor="middle" font-size="9.5">🔍</text>
  <text x="112" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">Layout</text>
  <text x="112" y="400" text-anchor="middle" font-size="8" fill="#94a3b8">Analysis</text>
  <text x="112" y="413" text-anchor="middle" font-size="7" fill="#475569">parse regions</text>

  <text x="188" y="395" text-anchor="middle" font-size="14" fill="#334155">→</text>

  <rect x="202" y="352" width="92" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="248" y="373" text-anchor="middle" font-size="9.5">🎨</text>
  <text x="248" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">Style</text>
  <text x="248" y="400" text-anchor="middle" font-size="8" fill="#94a3b8">Extraction</text>
  <text x="248" y="413" text-anchor="middle" font-size="7" fill="#475569">colors / fonts</text>

  <text x="324" y="395" text-anchor="middle" font-size="14" fill="#334155">→</text>

  <rect x="338" y="352" width="92" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="384" y="373" text-anchor="middle" font-size="9.5">🧩</text>
  <text x="384" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">Component</text>
  <text x="384" y="400" text-anchor="middle" font-size="8" fill="#94a3b8">Generation</text>
  <text x="384" y="413" text-anchor="middle" font-size="7" fill="#475569">JSX / HTML</text>

  <text x="460" y="395" text-anchor="middle" font-size="14" fill="#334155">→</text>

  <rect x="474" y="352" width="28" height="74" rx="5" fill="#1e293b" stroke="#ef4444" stroke-width="0.6"/>
  <text x="488" y="393" text-anchor="middle" font-size="9.5" fill="#ef4444">✓</text>

  <!-- Arrows in screenshot module -->
  <line x1="170" y1="266" x2="196" y2="266" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arrowGreen)" opacity="0.7"/>
  <line x1="322" y1="266" x2="348" y2="266" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arrowGreen)" opacity="0.7"/>
  <line x1="259" y1="300" x2="259" y2="322" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>

  <!-- ══════════════════════════════════════════
       LAYER 2 — MCP-BRAIN MODULE
  ══════════════════════════════════════════ -->
  <rect x="558" y="218" width="512" height="240" rx="10" fill="url(#laneGreen)" stroke="#10b981" stroke-width="0.8" opacity="0.9"/>
  <rect x="558" y="214" width="185" height="14" rx="3" fill="#022c22"/>
  <text x="650" y="224" text-anchor="middle" font-size="8" letter-spacing="3" fill="#10b981">LAYER 2 · MCP-BRAIN</text>

  <!-- MCP Server -->
  <rect x="578" y="232" width="140" height="68" rx="7" fill="url(#nodeGreen)" stroke="#10b981" stroke-width="1.2" filter="url(#glowGreen)"/>
  <text x="648" y="252" text-anchor="middle" font-size="13">🔌</text>
  <text x="648" y="268" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#34d399">MCP Server</text>
  <text x="648" y="282" text-anchor="middle" font-size="7.5" fill="#64748b">Model Context Protocol</text>
  <text x="648" y="293" text-anchor="middle" font-size="7" fill="#475569">Python / TS transport</text>

  <!-- Tool Registry -->
  <rect x="740" y="232" width="130" height="68" rx="7" fill="url(#nodeGreen)" stroke="#10b981" stroke-width="1"/>
  <text x="805" y="252" text-anchor="middle" font-size="13">🗂️</text>
  <text x="805" y="268" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#34d399">Tool Registry</text>
  <text x="805" y="282" text-anchor="middle" font-size="7.5" fill="#64748b">Tool definitions</text>
  <text x="805" y="293" text-anchor="middle" font-size="7" fill="#475569">JSON schema spec</text>

  <!-- AI Host connector -->
  <rect x="892" y="232" width="148" height="68" rx="7" fill="url(#nodeGreen)" stroke="#10b981" stroke-width="1"/>
  <text x="966" y="252" text-anchor="middle" font-size="13">🤖</text>
  <text x="966" y="268" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#34d399">AI Host Client</text>
  <text x="966" y="282" text-anchor="middle" font-size="7.5" fill="#64748b">Antigravity / Claude</text>
  <text x="966" y="293" text-anchor="middle" font-size="7" fill="#475569">LLM agent caller</text>

  <!-- Tool capabilities -->
  <rect x="578" y="322" width="460" height="120" rx="7" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
  <text x="808" y="342" text-anchor="middle" font-size="8" letter-spacing="2" fill="#475569">EXPOSED MCP TOOLS</text>

  <rect x="594" y="352" width="88" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="638" y="372" text-anchor="middle" font-size="11">🌐</text>
  <text x="638" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">Web Search</text>
  <text x="638" y="401" text-anchor="middle" font-size="7" fill="#475569">fetch &amp; scrape</text>
  <text x="638" y="413" text-anchor="middle" font-size="7" fill="#475569">live data</text>

  <rect x="694" y="352" width="88" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="738" y="372" text-anchor="middle" font-size="11">📂</text>
  <text x="738" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">File System</text>
  <text x="738" y="401" text-anchor="middle" font-size="7" fill="#475569">read / write</text>
  <text x="738" y="413" text-anchor="middle" font-size="7" fill="#475569">project files</text>

  <rect x="794" y="352" width="88" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="838" y="372" text-anchor="middle" font-size="11">💻</text>
  <text x="838" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">Code Exec</text>
  <text x="838" y="401" text-anchor="middle" font-size="7" fill="#475569">run scripts</text>
  <text x="838" y="413" text-anchor="middle" font-size="7" fill="#475569">shell cmds</text>

  <rect x="894" y="352" width="88" height="74" rx="5" fill="#1e293b" stroke="#334155" stroke-width="0.6"/>
  <text x="938" y="372" text-anchor="middle" font-size="11">🔗</text>
  <text x="938" y="388" text-anchor="middle" font-size="8" fill="#94a3b8">API Bridge</text>
  <text x="938" y="401" text-anchor="middle" font-size="7" fill="#475569">ext services</text>
  <text x="938" y="413" text-anchor="middle" font-size="7" fill="#475569">integrations</text>

  <rect x="994" y="352" width="58" height="74" rx="5" fill="#022c22" stroke="#10b981" stroke-width="0.6"/>
  <text x="1023" y="380" text-anchor="middle" font-size="9.5" fill="#10b981">+</text>
  <text x="1023" y="395" text-anchor="middle" font-size="7" fill="#10b981">more</text>
  <text x="1023" y="407" text-anchor="middle" font-size="7" fill="#10b981">tools</text>

  <!-- MCP arrows -->
  <line x1="718" y1="266" x2="740" y2="266" stroke="#10b981" stroke-width="1.2" marker-end="url(#arrowGreen)" opacity="0.7"/>
  <line x1="870" y1="266" x2="892" y2="266" stroke="#10b981" stroke-width="1.2" marker-end="url(#arrowGreen)" opacity="0.7"/>
  <line x1="805" y1="300" x2="805" y2="322" stroke="#10b981" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>

  <!-- ══════════════════════════════════════════
       LAYER 3 — ANIMATION SHOWCASE
  ══════════════════════════════════════════ -->
  <rect x="30" y="478" width="510" height="200" rx="10" fill="url(#lanePurple)" stroke="#a855f7" stroke-width="0.8" opacity="0.9"/>
  <rect x="30" y="474" width="220" height="14" rx="3" fill="#2e1065"/>
  <text x="140" y="484" text-anchor="middle" font-size="8" letter-spacing="3" fill="#a855f7">LAYER 3 · ANIMATION SHOWCASE</text>

  <rect x="50" y="492" width="130" height="68" rx="7" fill="url(#nodePurple)" stroke="#a855f7" stroke-width="1.2"/>
  <text x="115" y="512" text-anchor="middle" font-size="13">🎨</text>
  <text x="115" y="528" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#c084fc">CSS Engine</text>
  <text x="115" y="542" text-anchor="middle" font-size="7.5" fill="#64748b">Keyframes / vars</text>
  <text x="115" y="553" text-anchor="middle" font-size="7" fill="#475569">Custom properties</text>

  <rect x="202" y="492" width="130" height="68" rx="7" fill="url(#nodePurple)" stroke="#a855f7" stroke-width="1"/>
  <text x="267" y="512" text-anchor="middle" font-size="13">⚡</text>
  <text x="267" y="528" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#c084fc">JS Controller</text>
  <text x="267" y="542" text-anchor="middle" font-size="7.5" fill="#64748b">Intersection Observer</text>
  <text x="267" y="553" text-anchor="middle" font-size="7" fill="#475569">GSAP / Vanilla JS</text>

  <rect x="354" y="492" width="164" height="68" rx="7" fill="url(#nodePurple)" stroke="#a855f7" stroke-width="1"/>
  <text x="436" y="512" text-anchor="middle" font-size="13">🖥️</text>
  <text x="436" y="528" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#c084fc">Browser Render</text>
  <text x="436" y="542" text-anchor="middle" font-size="7.5" fill="#64748b">HTML5 · WebGL</text>
  <text x="436" y="553" text-anchor="middle" font-size="7" fill="#475569">Canvas API</text>

  <!-- animation types -->
  <rect x="50" y="574" width="468" height="88" rx="6" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
  <text x="284" y="592" text-anchor="middle" font-size="8" letter-spacing="2" fill="#475569">ANIMATION TYPES IN SHOWCASE</text>
  <!-- type pills -->
  <rect x="66" y="602" width="80" height="22" rx="4" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="106" y="616" text-anchor="middle" font-size="8" fill="#c084fc">Scroll Triggers</text>
  <rect x="156" y="602" width="80" height="22" rx="4" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="196" y="616" text-anchor="middle" font-size="8" fill="#c084fc">Hover States</text>
  <rect x="246" y="602" width="80" height="22" rx="4" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="286" y="616" text-anchor="middle" font-size="8" fill="#c084fc">Page Transitions</text>
  <rect x="336" y="602" width="80" height="22" rx="4" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="376" y="616" text-anchor="middle" font-size="8" fill="#c084fc">Particle FX</text>
  <rect x="426" y="602" width="80" height="22" rx="4" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="466" y="616" text-anchor="middle" font-size="8" fill="#c084fc">SVG Morph</text>
  <rect x="66" y="632" width="80" height="22" rx="4" fill="#1e293b" stroke="#7c3aed" stroke-width="0.5"/>
  <text x="106" y="646" text-anchor="middle" font-size="8" fill="#a78bfa">Lottie JSON</text>
  <rect x="156" y="632" width="80" height="22" rx="4" fill="#1e293b" stroke="#7c3aed" stroke-width="0.5"/>
  <text x="196" y="646" text-anchor="middle" font-size="8" fill="#a78bfa">3D CSS</text>
  <rect x="246" y="632" width="80" height="22" rx="4" fill="#1e293b" stroke="#7c3aed" stroke-width="0.5"/>
  <text x="286" y="646" text-anchor="middle" font-size="8" fill="#a78bfa">Clip-path Anim</text>
  <rect x="336" y="632" width="168" height="22" rx="4" fill="#2e1065" stroke="#a855f7" stroke-width="0.6"/>
  <text x="420" y="646" text-anchor="middle" font-size="8" fill="#a855f7">🚧 More in progress...</text>

  <!-- anim arrows -->
  <line x1="180" y1="526" x2="202" y2="526" stroke="#a855f7" stroke-width="1.2" marker-end="url(#arrowPurple)" opacity="0.7"/>
  <line x1="332" y1="526" x2="354" y2="526" stroke="#a855f7" stroke-width="1.2" marker-end="url(#arrowPurple)" opacity="0.7"/>

  <!-- ══════════════════════════════════════════
       LAYER 3 — ANTIGRAVITY WEBSITE
  ══════════════════════════════════════════ -->
  <rect x="558" y="478" width="512" height="200" rx="10" fill="url(#laneGold)" stroke="#f59e0b" stroke-width="0.8" opacity="0.9"/>
  <rect x="558" y="474" width="220" height="14" rx="3" fill="#451a03"/>
  <text x="668" y="484" text-anchor="middle" font-size="8" letter-spacing="3" fill="#f59e0b">LAYER 3 · ANTIGRAVITY WEBSITE</text>

  <rect x="578" y="492" width="140" height="68" rx="7" fill="url(#nodeGold)" stroke="#f59e0b" stroke-width="1.2"/>
  <text x="648" y="512" text-anchor="middle" font-size="13">🏗️</text>
  <text x="648" y="528" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#fcd34d">Frontend</text>
  <text x="648" y="542" text-anchor="middle" font-size="7.5" fill="#64748b">TypeScript + Vite</text>
  <text x="648" y="553" text-anchor="middle" font-size="7" fill="#475569">Component-driven</text>

  <rect x="740" y="492" width="140" height="68" rx="7" fill="url(#nodeGold)" stroke="#f59e0b" stroke-width="1"/>
  <text x="810" y="512" text-anchor="middle" font-size="13">🐳</text>
  <text x="810" y="528" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#fcd34d">Docker</text>
  <text x="810" y="542" text-anchor="middle" font-size="7.5" fill="#64748b">Containerized deploy</text>
  <text x="810" y="553" text-anchor="middle" font-size="7" fill="#475569">Dockerfile present</text>

  <rect x="902" y="492" width="138" height="68" rx="7" fill="url(#nodeGold)" stroke="#f59e0b" stroke-width="1"/>
  <text x="971" y="512" text-anchor="middle" font-size="13">☁️</text>
  <text x="971" y="528" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#fcd34d">Hosting</text>
  <text x="971" y="542" text-anchor="middle" font-size="7.5" fill="#64748b">CDN / Static host</text>
  <text x="971" y="553" text-anchor="middle" font-size="7" fill="#475569">Vercel / Netlify</text>

  <!-- page sections -->
  <rect x="578" y="574" width="460" height="88" rx="6" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
  <text x="808" y="592" text-anchor="middle" font-size="8" letter-spacing="2" fill="#475569">LANDING PAGE SECTIONS</text>
  <rect x="594" y="602" width="72" height="22" rx="4" fill="#1e293b" stroke="#f59e0b" stroke-width="0.5"/>
  <text x="630" y="616" text-anchor="middle" font-size="8" fill="#fcd34d">Hero</text>
  <rect x="674" y="602" width="72" height="22" rx="4" fill="#1e293b" stroke="#f59e0b" stroke-width="0.5"/>
  <text x="710" y="616" text-anchor="middle" font-size="8" fill="#fcd34d">Features</text>
  <rect x="754" y="602" width="72" height="22" rx="4" fill="#1e293b" stroke="#f59e0b" stroke-width="0.5"/>
  <text x="790" y="616" text-anchor="middle" font-size="8" fill="#fcd34d">Demo</text>
  <rect x="834" y="602" width="72" height="22" rx="4" fill="#1e293b" stroke="#f59e0b" stroke-width="0.5"/>
  <text x="870" y="616" text-anchor="middle" font-size="8" fill="#fcd34d">Pricing</text>
  <rect x="914" y="602" width="108" height="22" rx="4" fill="#451a03" stroke="#f59e0b" stroke-width="0.6"/>
  <text x="968" y="616" text-anchor="middle" font-size="8" fill="#f59e0b">🚧 In Progress</text>
  <rect x="594" y="632" width="72" height="22" rx="4" fill="#1e293b" stroke="#b45309" stroke-width="0.5"/>
  <text x="630" y="646" text-anchor="middle" font-size="8" fill="#d97706">CTA / Signup</text>
  <rect x="674" y="632" width="72" height="22" rx="4" fill="#1e293b" stroke="#b45309" stroke-width="0.5"/>
  <text x="710" y="646" text-anchor="middle" font-size="8" fill="#d97706">Blog</text>
  <rect x="754" y="632" width="72" height="22" rx="4" fill="#1e293b" stroke="#b45309" stroke-width="0.5"/>
  <text x="790" y="646" text-anchor="middle" font-size="8" fill="#d97706">Docs Link</text>
  <rect x="834" y="632" width="188" height="22" rx="4" fill="#451a03" stroke="#f59e0b" stroke-width="0.6"/>
  <text x="928" y="646" text-anchor="middle" font-size="8" fill="#f59e0b">🚧 Footer / Legal TBD</text>

  <!-- website arrows -->
  <line x1="718" y1="526" x2="740" y2="526" stroke="#f59e0b" stroke-width="1.2" marker-end="url(#arrowGold)" opacity="0.7"/>
  <line x1="880" y1="526" x2="902" y2="526" stroke="#f59e0b" stroke-width="1.2" marker-end="url(#arrowGold)" opacity="0.7"/>

  <!-- ══════════════════════════════════════════
       LAYER 4 — SHARED INFRASTRUCTURE
  ══════════════════════════════════════════ -->
  <rect x="30" y="698" width="1040" height="170" rx="10" fill="url(#laneBlue)" stroke="#0ea5e9" stroke-width="0.8" opacity="0.9"/>
  <rect x="30" y="694" width="240" height="14" rx="3" fill="#0c4a6e"/>
  <text x="150" y="704" text-anchor="middle" font-size="8" letter-spacing="3" fill="#0ea5e9">LAYER 4 · SHARED INFRASTRUCTURE</text>

  <!-- Node.js/npm -->
  <rect x="50" y="714" width="140" height="74" rx="7" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1.2"/>
  <text x="120" y="736" text-anchor="middle" font-size="13">📦</text>
  <text x="120" y="752" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#38bdf8">Node.js / npm</text>
  <text x="120" y="766" text-anchor="middle" font-size="7.5" fill="#64748b">Workspace root</text>
  <text x="120" y="777" text-anchor="middle" font-size="7" fill="#475569">package-lock.json v3</text>

  <!-- Python env -->
  <rect x="218" y="714" width="140" height="74" rx="7" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1"/>
  <text x="288" y="736" text-anchor="middle" font-size="13">🐍</text>
  <text x="288" y="752" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#38bdf8">Python 3.10+</text>
  <text x="288" y="766" text-anchor="middle" font-size="7.5" fill="#64748b">Backend runtime</text>
  <text x="288" y="777" text-anchor="middle" font-size="7" fill="#475569">venv / pip</text>

  <!-- TypeScript -->
  <rect x="386" y="714" width="140" height="74" rx="7" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1"/>
  <text x="456" y="736" text-anchor="middle" font-size="13">🔷</text>
  <text x="456" y="752" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#38bdf8">TypeScript</text>
  <text x="456" y="766" text-anchor="middle" font-size="7.5" fill="#64748b">Static type safety</text>
  <text x="456" y="777" text-anchor="middle" font-size="7" fill="#475569">tsconfig per module</text>

  <!-- Docker -->
  <rect x="554" y="714" width="140" height="74" rx="7" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1"/>
  <text x="624" y="736" text-anchor="middle" font-size="13">🐳</text>
  <text x="624" y="752" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#38bdf8">Docker</text>
  <text x="624" y="766" text-anchor="middle" font-size="7.5" fill="#64748b">Container runtime</text>
  <text x="624" y="777" text-anchor="middle" font-size="7" fill="#475569">antigravity-website</text>

  <!-- Vite -->
  <rect x="722" y="714" width="140" height="74" rx="7" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1"/>
  <text x="792" y="736" text-anchor="middle" font-size="13">⚡</text>
  <text x="792" y="752" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#38bdf8">Vite</text>
  <text x="792" y="766" text-anchor="middle" font-size="7.5" fill="#64748b">Build tooling</text>
  <text x="792" y="777" text-anchor="middle" font-size="7" fill="#475569">HMR · fast builds</text>

  <!-- Git -->
  <rect x="890" y="714" width="152" height="74" rx="7" fill="url(#nodeBlue)" stroke="#0ea5e9" stroke-width="1"/>
  <text x="966" y="736" text-anchor="middle" font-size="13">🌿</text>
  <text x="966" y="752" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#38bdf8">Git / GitHub</text>
  <text x="966" y="766" text-anchor="middle" font-size="7.5" fill="#64748b">Version control</text>
  <text x="966" y="777" text-anchor="middle" font-size="7" fill="#475569">main branch · public</text>

  <!-- WIP bar -->
  <rect x="50" y="800" width="990" height="52" rx="6" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
  <text x="545" y="818" text-anchor="middle" font-size="8" letter-spacing="2" fill="#475569">PLANNED INFRASTRUCTURE (IN PROGRESS)</text>
  <rect x="66" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="120" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 CI/CD Pipeline</text>
  <rect x="186" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="240" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 Shared Types Pkg</text>
  <rect x="306" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="360" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 Test Coverage</text>
  <rect x="426" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="480" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 Lint / ESLint</text>
  <rect x="546" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="600" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 Env Management</text>
  <rect x="666" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="720" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 Monorepo Tooling</text>
  <rect x="786" y="826" width="108" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="840" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 API Docs</text>
  <rect x="906" y="826" width="124" height="20" rx="3" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="968" y="840" text-anchor="middle" font-size="7.5" fill="#38bdf8">🚧 Deployment Scripts</text>

  <!-- ══════════════════════════════════════════
       LAYER 5 — EXTERNAL AI INTEGRATIONS
  ══════════════════════════════════════════ -->
  <rect x="30" y="888" width="1040" height="140" rx="10" fill="rgba(168,85,247,0.05)" stroke="#7c3aed" stroke-width="0.8" opacity="0.9"/>
  <rect x="30" y="884" width="250" height="14" rx="3" fill="#1e1b4b"/>
  <text x="155" y="894" text-anchor="middle" font-size="8" letter-spacing="3" fill="#a855f7">LAYER 5 · EXTERNAL AI INTEGRATIONS</text>

  <rect x="50" y="904" width="148" height="108" rx="7" fill="url(#nodePurple)" stroke="#a855f7" stroke-width="1.2"/>
  <text x="124" y="930" text-anchor="middle" font-size="14">🤖</text>
  <text x="124" y="950" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#c084fc">OpenAI API</text>
  <text x="124" y="965" text-anchor="middle" font-size="7.5" fill="#64748b">GPT-4o Vision</text>
  <text x="124" y="978" text-anchor="middle" font-size="7" fill="#475569">screenshot parsing</text>
  <text x="124" y="991" text-anchor="middle" font-size="7" fill="#475569">code generation</text>
  <text x="124" y="1004" text-anchor="middle" font-size="7" fill="#334155">🚧 configurable</text>

  <rect x="222" y="904" width="148" height="108" rx="7" fill="url(#nodePurple)" stroke="#a855f7" stroke-width="1"/>
  <text x="296" y="930" text-anchor="middle" font-size="14">🧠</text>
  <text x="296" y="950" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#c084fc">Anthropic API</text>
  <text x="296" y="965" text-anchor="middle" font-size="7.5" fill="#64748b">Claude Sonnet/Opus</text>
  <text x="296" y="978" text-anchor="middle" font-size="7" fill="#475569">MCP tool calling</text>
  <text x="296" y="991" text-anchor="middle" font-size="7" fill="#475569">agentic reasoning</text>
  <text x="296" y="1004" text-anchor="middle" font-size="7" fill="#334155">🚧 planned</text>

  <rect x="394" y="904" width="148" height="108" rx="7" fill="url(#nodePurple)" stroke="#a855f7" stroke-width="1"/>
  <text x="468" y="930" text-anchor="middle" font-size="14">💎</text>
  <text x="468" y="950" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#c084fc">Gemini API</text>
  <text x="468" y="965" text-anchor="middle" font-size="7.5" fill="#64748b">Gemini 3 Pro</text>
  <text x="468" y="978" text-anchor="middle" font-size="7" fill="#475569">Antigravity host</text>
  <text x="468" y="991" text-anchor="middle" font-size="7" fill="#475569">1M context window</text>
  <text x="468" y="1004" text-anchor="middle" font-size="7" fill="#334155">🚧 primary target</text>

  <rect x="566" y="904" width="148" height="108" rx="7" fill="url(#nodePurple)" stroke="#7c3aed" stroke-width="1"/>
  <text x="640" y="930" text-anchor="middle" font-size="14">🌐</text>
  <text x="640" y="950" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#a78bfa">Browser APIs</text>
  <text x="640" y="965" text-anchor="middle" font-size="7.5" fill="#64748b">Puppeteer / CDP</text>
  <text x="640" y="978" text-anchor="middle" font-size="7" fill="#475569">screenshot capture</text>
  <text x="640" y="991" text-anchor="middle" font-size="7" fill="#475569">DOM interaction</text>
  <text x="640" y="1004" text-anchor="middle" font-size="7" fill="#334155">🚧 mcp-brain</text>

  <rect x="738" y="904" width="148" height="108" rx="7" fill="url(#nodePurple)" stroke="#7c3aed" stroke-width="1"/>
  <text x="812" y="930" text-anchor="middle" font-size="14">🔧</text>
  <text x="812" y="950" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#a78bfa">MCP Protocol</text>
  <text x="812" y="965" text-anchor="middle" font-size="7.5" fill="#64748b">Std transport layer</text>
  <text x="812" y="978" text-anchor="middle" font-size="7" fill="#475569">stdio / HTTP / SSE</text>
  <text x="812" y="991" text-anchor="middle" font-size="7" fill="#475569">tool schema JSON</text>
  <text x="812" y="1004" text-anchor="middle" font-size="7" fill="#334155">🚧 core protocol</text>

  <rect x="910" y="904" width="148" height="108" rx="7" fill="url(#nodePurple)" stroke="#7c3aed" stroke-width="1"/>
  <text x="984" y="930" text-anchor="middle" font-size="14">🎯</text>
  <text x="984" y="950" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#a78bfa">Antigravity IDE</text>
  <text x="984" y="965" text-anchor="middle" font-size="7.5" fill="#64748b">Primary AI host</text>
  <text x="984" y="978" text-anchor="middle" font-size="7" fill="#475569">agent task executor</text>
  <text x="984" y="991" text-anchor="middle" font-size="7" fill="#475569">built-in browser</text>
  <text x="984" y="1004" text-anchor="middle" font-size="7" fill="#334155">🚧 target env</text>

  <!-- ══════════════════════════════════════════
       DATA FLOW CONNECTIONS (between layers)
  ══════════════════════════════════════════ -->
  <!-- Layer 1 to layer 2 -->
  <line x1="963" y1="180" x2="963" y2="218" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrowGreen)" opacity="0.6"/>
  <line x1="794" y1="180" x2="794" y2="218" stroke="#10b981" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrowGreen)" opacity="0.6"/>
  <line x1="466" y1="180" x2="284" y2="478" stroke="#a855f7" stroke-width="1" stroke-dasharray="4,3" opacity="0.4"/>
  <line x1="630" y1="180" x2="750" y2="478" stroke="#f59e0b" stroke-width="1" stroke-dasharray="4,3" opacity="0.4"/>

  <!-- modules to infra -->
  <line x1="284" y1="678" x2="284" y2="698" stroke="#0ea5e9" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>
  <line x1="630" y1="678" x2="630" y2="698" stroke="#0ea5e9" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>
  <line x1="808" y1="678" x2="808" y2="698" stroke="#0ea5e9" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>
  <line x1="963" y1="678" x2="963" y2="698" stroke="#0ea5e9" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>

  <!-- infra to AI integrations -->
  <line x1="550" y1="868" x2="550" y2="888" stroke="#a855f7" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>

  <!-- ══════════════════════════════════════════
       TECH STACK LEGEND
  ══════════════════════════════════════════ -->
  <rect x="30" y="1050" width="1040" height="180" rx="10" fill="#080810" stroke="#1e293b" stroke-width="0.8"/>
  <text x="550" y="1074" text-anchor="middle" font-size="9" letter-spacing="4" fill="#334155">COMPLETE TECH STACK</text>

  <!-- Backend -->
  <text x="50" y="1096" font-size="8" letter-spacing="2" fill="#ef4444">BACKEND / AI</text>
  <rect x="50" y="1104" width="55" height="18" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="0.5"/>
  <text x="77" y="1116" text-anchor="middle" font-size="7.5" fill="#f87171">Python 3.10</text>
  <rect x="113" y="1104" width="55" height="18" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="0.5"/>
  <text x="140" y="1116" text-anchor="middle" font-size="7.5" fill="#f87171">FastAPI</text>
  <rect x="176" y="1104" width="55" height="18" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="0.5"/>
  <text x="203" y="1116" text-anchor="middle" font-size="7.5" fill="#f87171">OpenAI SDK</text>
  <rect x="239" y="1104" width="55" height="18" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="0.5"/>
  <text x="266" y="1116" text-anchor="middle" font-size="7.5" fill="#f87171">Anthropic</text>
  <rect x="302" y="1104" width="55" height="18" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="0.5"/>
  <text x="329" y="1116" text-anchor="middle" font-size="7.5" fill="#f87171">Pillow / CV2</text>

  <!-- Frontend -->
  <text x="50" y="1142" font-size="8" letter-spacing="2" fill="#a855f7">FRONTEND</text>
  <rect x="50" y="1150" width="55" height="18" rx="3" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="77" y="1162" text-anchor="middle" font-size="7.5" fill="#c084fc">TypeScript</text>
  <rect x="113" y="1150" width="55" height="18" rx="3" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="140" y="1162" text-anchor="middle" font-size="7.5" fill="#c084fc">React 18</text>
  <rect x="176" y="1150" width="55" height="18" rx="3" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="203" y="1162" text-anchor="middle" font-size="7.5" fill="#c084fc">Vite</text>
  <rect x="239" y="1150" width="55" height="18" rx="3" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="266" y="1162" text-anchor="middle" font-size="7.5" fill="#c084fc">Tailwind CSS</text>
  <rect x="302" y="1150" width="55" height="18" rx="3" fill="#1e293b" stroke="#a855f7" stroke-width="0.5"/>
  <text x="329" y="1162" text-anchor="middle" font-size="7.5" fill="#c084fc">GSAP</text>

  <!-- Infra -->
  <text x="50" y="1188" font-size="8" letter-spacing="2" fill="#0ea5e9">INFRA / DEVOPS</text>
  <rect x="50" y="1196" width="55" height="18" rx="3" fill="#1e293b" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="77" y="1208" text-anchor="middle" font-size="7.5" fill="#38bdf8">Docker</text>
  <rect x="113" y="1196" width="55" height="18" rx="3" fill="#1e293b" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="140" y="1208" text-anchor="middle" font-size="7.5" fill="#38bdf8">Node.js</text>
  <rect x="176" y="1196" width="55" height="18" rx="3" fill="#1e293b" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="203" y="1208" text-anchor="middle" font-size="7.5" fill="#38bdf8">npm v3</text>
  <rect x="239" y="1196" width="55" height="18" rx="3" fill="#1e293b" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="266" y="1208" text-anchor="middle" font-size="7.5" fill="#38bdf8">GitHub</text>
  <rect x="302" y="1196" width="55" height="18" rx="3" fill="#1e293b" stroke="#0ea5e9" stroke-width="0.5"/>
  <text x="329" y="1208" text-anchor="middle" font-size="7.5" fill="#38bdf8">Uvicorn</text>

  <!-- Protocol -->
  <text x="420" y="1096" font-size="8" letter-spacing="2" fill="#10b981">PROTOCOLS</text>
  <rect x="420" y="1104" width="68" height="18" rx="3" fill="#1e293b" stroke="#10b981" stroke-width="0.5"/>
  <text x="454" y="1116" text-anchor="middle" font-size="7.5" fill="#34d399">MCP (stdio)</text>
  <rect x="496" y="1104" width="68" height="18" rx="3" fill="#1e293b" stroke="#10b981" stroke-width="0.5"/>
  <text x="530" y="1116" text-anchor="middle" font-size="7.5" fill="#34d399">MCP (HTTP/SSE)</text>
  <rect x="572" y="1104" width="68" height="18" rx="3" fill="#1e293b" stroke="#10b981" stroke-width="0.5"/>
  <text x="606" y="1116" text-anchor="middle" font-size="7.5" fill="#34d399">JSON Schema</text>
  <rect x="648" y="1104" width="68" height="18" rx="3" fill="#1e293b" stroke="#10b981" stroke-width="0.5"/>
  <text x="682" y="1116" text-anchor="middle" font-size="7.5" fill="#34d399">REST / OpenAPI</text>

  <!-- Status legend -->
  <text x="420" y="1142" font-size="8" letter-spacing="2" fill="#f59e0b">STATUS</text>
  <rect x="420" y="1150" width="90" height="18" rx="3" fill="#052e16" stroke="#10b981" stroke-width="0.8"/>
  <text x="465" y="1162" text-anchor="middle" font-size="7.5" fill="#34d399">✅ Implemented</text>
  <rect x="520" y="1150" width="90" height="18" rx="3" fill="#451a03" stroke="#f59e0b" stroke-width="0.8"/>
  <text x="565" y="1162" text-anchor="middle" font-size="7.5" fill="#fcd34d">🚧 In Progress</text>
  <rect x="620" y="1150" width="90" height="18" rx="3" fill="#1e1b4b" stroke="#a855f7" stroke-width="0.8"/>
  <text x="665" y="1162" text-anchor="middle" font-size="7.5" fill="#c084fc">🔮 Planned</text>

  <!-- WIP indicator -->
  <text x="420" y="1188" font-size="8" letter-spacing="2" fill="#334155">PROJECT STATUS</text>
  <rect x="420" y="1196" width="640" height="18" rx="3" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
  <!-- progress bar fill -->
  <rect x="421" y="1197" width="270" height="16" rx="2" fill="linear-gradient(90deg, #0ea5e9, #10b981)"/>
  <rect x="421" y="1197" width="270" height="16" rx="2">
    <animate attributeName="width" from="0" to="270" dur="2s" fill="freeze"/>
  </rect>
  <rect x="421" y="1197" width="270" height="16" rx="2" fill="#0ea5e9" opacity="0.6"/>
  <text x="556" y="1209" text-anchor="middle" font-size="7.5" fill="#fff" font-weight="bold">~42% Complete — Active Development</text>
  <text x="910" y="1209" text-anchor="middle" font-size="7" fill="#475569">5 modules · 1 commit · ongoing</text>

  <!-- Bottom corner brackets -->
  <path d="M30,1300 L30,1290 L56,1290" fill="none" stroke="#0ea5e9" stroke-width="1.5" opacity="0.4"/>
  <path d="M1070,1300 L1070,1290 L1044,1290" fill="none" stroke="#0ea5e9" stroke-width="1.5" opacity="0.4"/>
  <text x="550" y="1298" text-anchor="middle" font-size="8" letter-spacing="2" fill="#1e293b">github.com/Aka-Nine/Vision · 2026</text>
</svg>
-architecture.svg…]()

```

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
