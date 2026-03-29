"""
Deep Site Analyzer — Comprehensive Website Scraping Engine
═══════════════════════════════════════════════════════════
Playwright-based module that captures EVERY aspect of a website:

  • Full CSS extraction (computed styles for key elements)
  • Complete DOM structure (semantic HTML tree)
  • Font analysis (@font-face declarations, families, weights)
  • Color palette extraction (background, text, accent colors)
  • Animation/transition detection (keyframes, transforms, scroll effects)
  • Scroll-position screenshots (captures at multiple scroll depths)
  • Section-by-section content extraction (headings, text, CTAs per section)
  • Layout analysis (grid/flex, spacing, alignment patterns)
  • Component identification (hero, nav, features, pricing, footer, etc.)
  • Asset inventory (images, SVGs, icons, canvases)

This is the "brain's eyes" — it sees a website exactly like a human designer would,
capturing every detail needed for the template generator to faithfully reproduce it.

Usage:
    from services.deep_site_analyzer import DeepSiteAnalyzer

    analyzer = DeepSiteAnalyzer()
    result = await analyzer.analyze("https://example.com", out_dir="storage/deep_analysis")
"""

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FontInfo:
    family: str
    weight: str
    style: str
    size: Optional[str] = None
    usage: Optional[str] = None  # "heading", "body", "nav", etc.


@dataclass
class ColorInfo:
    hex: str
    rgb: str
    usage: str  # "background", "text", "accent", "border"
    element: Optional[str] = None


@dataclass
class SectionInfo:
    tag: str
    id: Optional[str]
    classes: List[str]
    heading: Optional[str]
    heading_tag: Optional[str]
    description: Optional[str]
    cta_texts: List[str]
    scroll_y: float
    bounding_box: Dict[str, float]
    component_type: Optional[str]  # "hero", "features", "pricing", etc.
    child_count: int


@dataclass
class AnimationInfo:
    type: str  # "css_animation", "css_transition", "scroll_triggered", "transform"
    name: Optional[str]
    duration: Optional[str]
    properties: Optional[str]
    element_selector: Optional[str]


@dataclass
class LayoutInfo:
    display: str  # "flex", "grid", "block"
    direction: Optional[str]
    gap: Optional[str]
    columns: Optional[str]
    align: Optional[str]
    justify: Optional[str]
    element: str


@dataclass
class DeepAnalysisResult:
    url: str
    final_url: str
    title: str
    meta_description: str

    # Core extracted data
    fonts: List[Dict]
    colors: List[Dict]
    sections: List[Dict]
    animations: List[Dict]
    layouts: List[Dict]

    # Raw CSS data
    css_variables: Dict[str, str]
    computed_styles: Dict[str, Dict]

    # Content
    headings: List[Dict]
    navigation: Dict
    footer: Dict

    # Assets
    images: List[Dict]
    svgs: int
    canvases: int
    icons_library: Optional[str]

    # Screenshots
    scroll_screenshots: List[str]
    full_page_screenshot: str

    # Page metrics
    page_height: int
    viewport_width: int
    viewport_height: int

    # DOM structure
    dom_structure: Dict

    # Analysis metadata
    analysis_duration_seconds: float
    timestamp: str

    # Full JSON path for downstream use
    analysis_json_path: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# JavaScript Extraction Scripts
# ═══════════════════════════════════════════════════════════════════

JS_EXTRACT_CSS_VARIABLES = """() => {
    const rootStyles = getComputedStyle(document.documentElement);
    const vars = {};
    for (let i = 0; i < rootStyles.length; i++) {
        const k = rootStyles[i];
        if (k && k.startsWith('--')) {
            vars[k] = rootStyles.getPropertyValue(k).trim();
        }
    }
    return vars;
}"""

JS_EXTRACT_COMPUTED_STYLES = """() => {
    const pick = (el, label) => {
        if (!el) return null;
        const cs = getComputedStyle(el);
        return {
            label,
            backgroundColor: cs.backgroundColor,
            color: cs.color,
            fontFamily: cs.fontFamily,
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
            lineHeight: cs.lineHeight,
            letterSpacing: cs.letterSpacing,
            borderRadius: cs.borderRadius,
            border: cs.border,
            boxShadow: cs.boxShadow,
            padding: cs.padding,
            margin: cs.margin,
        };
    };

    const body = pick(document.body, 'body');
    const h1 = pick(document.querySelector('h1'), 'h1');
    const h2 = pick(document.querySelector('h2'), 'h2');
    const h3 = pick(document.querySelector('h3'), 'h3');
    const p = pick(document.querySelector('p'), 'p');
    const nav = pick(document.querySelector('nav, header'), 'nav');
    const footer = pick(document.querySelector('footer'), 'footer');
    const btn = pick(document.querySelector('button, a.btn, [class*="btn"], [class*="button"]'), 'button');
    const card = pick(document.querySelector('[class*="card"], [class*="Card"]'), 'card');
    const link = pick(document.querySelector('a'), 'link');

    return { body, h1, h2, h3, p, nav, footer, button: btn, card, link };
}"""

JS_EXTRACT_FONTS = """() => {
    const fonts = [];

    // From document.fonts API
    if (document.fonts && document.fonts.size) {
        for (const f of document.fonts) {
            fonts.push({
                family: f.family,
                weight: f.weight,
                style: f.style,
                stretch: f.stretch || 'normal',
                status: f.status,
                source: 'document.fonts'
            });
        }
    }

    // From @font-face rules in stylesheets
    try {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.type === CSSRule.FONT_FACE_RULE) {
                        fonts.push({
                            family: rule.style.getPropertyValue('font-family').replace(/['"]/g, ''),
                            weight: rule.style.getPropertyValue('font-weight') || 'normal',
                            style: rule.style.getPropertyValue('font-style') || 'normal',
                            src: (rule.style.getPropertyValue('src') || '').slice(0, 200),
                            source: '@font-face'
                        });
                    }
                }
            } catch (e) { /* cross-origin */ }
        }
    } catch (e) {}

    // Deduplicate by family+weight
    const seen = new Set();
    return fonts.filter(f => {
        const key = `${f.family}|${f.weight}|${f.style}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    }).slice(0, 50);
}"""

JS_EXTRACT_COLORS = """() => {
    const colors = new Map();
    const rgbToHex = (rgb) => {
        const m = rgb.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
        if (!m) return rgb;
        return '#' + [m[1], m[2], m[3]].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
    };

    const addColor = (rgb, usage, el) => {
        if (!rgb || rgb === 'rgba(0, 0, 0, 0)' || rgb === 'transparent') return;
        const hex = rgbToHex(rgb);
        const key = `${hex}|${usage}`;
        if (!colors.has(key)) {
            colors.set(key, { hex, rgb, usage, element: el, count: 1 });
        } else {
            colors.get(key).count++;
        }
    };

    // Sample key elements
    const selectors = [
        { sel: 'body', usage: 'background' },
        { sel: 'h1', usage: 'heading' },
        { sel: 'h2', usage: 'heading' },
        { sel: 'h3', usage: 'heading' },
        { sel: 'p', usage: 'body_text' },
        { sel: 'a', usage: 'link' },
        { sel: 'nav, header', usage: 'navigation' },
        { sel: 'footer', usage: 'footer' },
        { sel: 'button, [class*="btn"]', usage: 'button' },
        { sel: '[class*="card"], [class*="Card"]', usage: 'card' },
        { sel: 'section', usage: 'section' },
    ];

    for (const { sel, usage } of selectors) {
        const els = document.querySelectorAll(sel);
        for (const el of Array.from(els).slice(0, 5)) {
            const cs = getComputedStyle(el);
            addColor(cs.backgroundColor, `${usage}_bg`, el.tagName.toLowerCase());
            addColor(cs.color, `${usage}_text`, el.tagName.toLowerCase());
            if (cs.borderColor && cs.borderColor !== 'rgb(0, 0, 0)') {
                addColor(cs.borderColor, `${usage}_border`, el.tagName.toLowerCase());
            }
        }
    }

    return Array.from(colors.values())
        .sort((a, b) => b.count - a.count)
        .slice(0, 40);
}"""

JS_EXTRACT_SECTIONS = """() => {
    const sections = [];
    const sectionEls = document.querySelectorAll('section, [class*="section"], main > div, [role="region"]');

    const inferType = (el) => {
        const text = (el.textContent || '').toLowerCase().slice(0, 500);
        const classes = (el.className || '').toLowerCase();
        const id = (el.id || '').toLowerCase();
        const combined = `${classes} ${id} ${text}`;

        if (combined.includes('hero') || combined.includes('banner') || combined.includes('jumbotron')) return 'hero';
        if (combined.includes('feature') || combined.includes('benefit')) return 'features';
        if (combined.includes('pric') || combined.includes('plan')) return 'pricing';
        if (combined.includes('testimonial') || combined.includes('review') || combined.includes('feedback')) return 'testimonials';
        if (combined.includes('cta') || combined.includes('call-to-action') || combined.includes('download')) return 'cta';
        if (combined.includes('footer')) return 'footer';
        if (combined.includes('nav') || combined.includes('header') || combined.includes('menu')) return 'navigation';
        if (combined.includes('blog') || combined.includes('article') || combined.includes('post')) return 'blog';
        if (combined.includes('faq') || combined.includes('question')) return 'faq';
        if (combined.includes('contact') || combined.includes('form')) return 'contact';
        if (combined.includes('team') || combined.includes('about')) return 'about';
        if (combined.includes('gallery') || combined.includes('showcase') || combined.includes('portfolio')) return 'gallery';
        if (combined.includes('stat') || combined.includes('metric') || combined.includes('number')) return 'stats';
        return 'generic_section';
    };

    for (const el of sectionEls) {
        const rect = el.getBoundingClientRect();
        if (rect.height < 50) continue;  // Skip tiny sections

        const heading = el.querySelector('h1, h2, h3');
        const headingTag = heading ? heading.tagName.toLowerCase() : null;
        const headingText = heading ? heading.textContent.trim().slice(0, 200) : null;

        const desc = el.querySelector('p');
        const descText = desc ? desc.textContent.trim().slice(0, 300) : null;

        const ctaEls = el.querySelectorAll('a, button');
        const ctas = Array.from(ctaEls)
            .map(e => e.textContent.trim())
            .filter(t => t.length >= 2 && t.length <= 60)
            .slice(0, 10);

        sections.push({
            tag: el.tagName.toLowerCase(),
            id: el.id || null,
            classes: (el.className && typeof el.className === 'string') ? el.className.split(/\\s+/).slice(0, 20) : [],
            heading: headingText,
            heading_tag: headingTag,
            description: descText,
            cta_texts: ctas,
            scroll_y: rect.top + window.scrollY,
            bounding_box: { x: rect.x, y: rect.top + window.scrollY, w: rect.width, h: rect.height },
            component_type: inferType(el),
            child_count: el.children.length,
        });
    }

    return sections.slice(0, 50);
}"""

JS_EXTRACT_ANIMATIONS = """() => {
    const animations = [];
    const seen = new Set();

    // 1. CSS @keyframes names from stylesheets
    try {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.type === CSSRule.KEYFRAMES_RULE) {
                        const name = rule.name;
                        if (!seen.has(name)) {
                            seen.add(name);
                            animations.push({
                                type: 'css_keyframe',
                                name,
                                duration: null,
                                properties: null,
                                element_selector: null,
                            });
                        }
                    }
                }
            } catch (e) { /* cross-origin */ }
        }
    } catch (e) {}

    // 2. Elements with animation or transition properties
    const allEls = document.querySelectorAll('*');
    let checked = 0;
    for (const el of allEls) {
        if (checked > 500) break;
        checked++;
        const cs = getComputedStyle(el);

        // CSS animations
        if (cs.animationName && cs.animationName !== 'none') {
            const key = `anim|${cs.animationName}|${el.tagName}`;
            if (!seen.has(key)) {
                seen.add(key);
                animations.push({
                    type: 'css_animation',
                    name: cs.animationName,
                    duration: cs.animationDuration,
                    properties: null,
                    element_selector: el.tagName.toLowerCase() +
                        (el.id ? '#' + el.id : '') +
                        (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''),
                });
            }
        }

        // CSS transitions
        if (cs.transitionProperty && cs.transitionProperty !== 'all' && cs.transitionProperty !== 'none') {
            const key = `trans|${cs.transitionProperty}|${el.tagName}`;
            if (!seen.has(key)) {
                seen.add(key);
                animations.push({
                    type: 'css_transition',
                    name: null,
                    duration: cs.transitionDuration,
                    properties: cs.transitionProperty,
                    element_selector: el.tagName.toLowerCase() +
                        (el.id ? '#' + el.id : '') +
                        (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''),
                });
            }
        }

        // Transforms (potential animations)
        if (cs.transform && cs.transform !== 'none') {
            const key = `xform|${cs.transform.slice(0, 30)}|${el.tagName}`;
            if (!seen.has(key)) {
                seen.add(key);
                animations.push({
                    type: 'transform',
                    name: null,
                    duration: null,
                    properties: cs.transform,
                    element_selector: el.tagName.toLowerCase() +
                        (el.id ? '#' + el.id : ''),
                });
            }
        }
    }

    // 3. Detect canvas elements (potential JS animations)
    const canvases = document.querySelectorAll('canvas');
    for (const c of canvases) {
        animations.push({
            type: 'canvas_animation',
            name: 'canvas',
            duration: 'continuous',
            properties: `${c.width}x${c.height}`,
            element_selector: 'canvas' + (c.id ? '#' + c.id : ''),
        });
    }

    return animations.slice(0, 60);
}"""

JS_EXTRACT_LAYOUTS = """() => {
    const layouts = [];
    const seen = new Set();
    const els = document.querySelectorAll('section, nav, header, footer, main, [class*="container"], [class*="grid"], [class*="flex"], [class*="row"]');

    for (const el of Array.from(els).slice(0, 40)) {
        const cs = getComputedStyle(el);
        const display = cs.display;
        if (!display || display === 'inline') continue;

        const key = `${el.tagName}|${el.className || ''}|${display}`;
        if (seen.has(key)) continue;
        seen.add(key);

        layouts.push({
            display,
            direction: cs.flexDirection || cs.gridAutoFlow || null,
            gap: cs.gap || null,
            columns: cs.gridTemplateColumns || null,
            align: cs.alignItems || null,
            justify: cs.justifyContent || null,
            element: el.tagName.toLowerCase() +
                (el.id ? '#' + el.id : '') +
                (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''),
        });
    }

    return layouts;
}"""

JS_EXTRACT_NAVIGATION = """() => {
    const nav = document.querySelector('nav, header');
    if (!nav) return { links: [], logo_text: null, cta_text: null };

    const links = Array.from(nav.querySelectorAll('a'))
        .map(a => ({ text: a.textContent.trim(), href: a.getAttribute('href') || '' }))
        .filter(l => l.text.length > 0 && l.text.length < 60)
        .slice(0, 20);

    // Try to find logo text
    const logoEl = nav.querySelector('[class*="logo"], [class*="brand"], .logo, .brand, a:first-child');
    const logo_text = logoEl ? logoEl.textContent.trim().slice(0, 80) : null;

    // Try to find primary CTA
    const ctaEl = nav.querySelector('button, [class*="btn"], [class*="cta"], [class*="download"]');
    const cta_text = ctaEl ? ctaEl.textContent.trim() : null;

    return { links, logo_text, cta_text };
}"""

JS_EXTRACT_FOOTER = """() => {
    const footer = document.querySelector('footer');
    if (!footer) return { links: [], copyright: null, columns: 0 };

    const links = Array.from(footer.querySelectorAll('a'))
        .map(a => ({ text: a.textContent.trim(), href: a.getAttribute('href') || '' }))
        .filter(l => l.text.length > 0 && l.text.length < 80)
        .slice(0, 40);

    const allText = footer.textContent || '';
    const copyrightMatch = allText.match(/©.*?\\d{4}[^\\n]*/);
    const copyright = copyrightMatch ? copyrightMatch[0].trim() : null;

    // Count footer columns
    const cols = footer.querySelectorAll('[class*="col"], [class*="column"], footer > div > div');

    return { links, copyright, columns: cols.length };
}"""

JS_EXTRACT_IMAGES = """() => {
    const images = [];
    const imgEls = document.querySelectorAll('img');

    for (const img of Array.from(imgEls).slice(0, 30)) {
        const rect = img.getBoundingClientRect();
        if (rect.width < 10 || rect.height < 10) continue;

        images.push({
            src: (img.getAttribute('src') || '').slice(0, 300),
            alt: (img.getAttribute('alt') || '').slice(0, 200),
            width: Math.round(rect.width),
            height: Math.round(rect.height),
            loading: img.getAttribute('loading') || 'eager',
        });
    }

    const svgs = document.querySelectorAll('svg').length;
    const canvases = document.querySelectorAll('canvas').length;

    // Detect icon library
    let icons_library = null;
    if (document.querySelector('link[href*="material-symbols"], link[href*="material-icons"]')) icons_library = 'material-symbols';
    else if (document.querySelector('link[href*="font-awesome"]')) icons_library = 'font-awesome';
    else if (document.querySelector('[class*="lucide"]')) icons_library = 'lucide';
    else if (document.querySelector('link[href*="heroicons"]')) icons_library = 'heroicons';
    else if (document.querySelector('[class*="feather"]')) icons_library = 'feather';

    return { images, svgs, canvases, icons_library };
}"""

JS_EXTRACT_HEADINGS = """() => {
    return Array.from(document.querySelectorAll('h1, h2, h3, h4'))
        .slice(0, 50)
        .map(el => {
            const cs = getComputedStyle(el);
            return {
                tag: el.tagName.toLowerCase(),
                text: el.textContent.trim().slice(0, 200),
                fontSize: cs.fontSize,
                fontWeight: cs.fontWeight,
                fontFamily: cs.fontFamily.split(',')[0].trim().replace(/['"]/g, ''),
                color: cs.color,
                letterSpacing: cs.letterSpacing,
                lineHeight: cs.lineHeight,
                textAlign: cs.textAlign,
            };
        });
}"""

JS_EXTRACT_DOM_STRUCTURE = """() => {
    const buildTree = (el, depth = 0) => {
        if (depth > 4) return null;
        if (!el || el.nodeType !== 1) return null;

        const tag = el.tagName.toLowerCase();
        // Skip script, style, svg internals, noscript
        if (['script', 'style', 'noscript', 'link', 'meta'].includes(tag)) return null;

        const node = {
            tag,
            id: el.id || null,
            classes: (el.className && typeof el.className === 'string')
                ? el.className.split(/\\s+/).filter(c => c.length > 0).slice(0, 10)
                : [],
            children: [],
        };

        // Only has text leaf content if no child elements
        if (el.children.length === 0 && el.textContent && el.textContent.trim().length > 0) {
            node.text = el.textContent.trim().slice(0, 120);
        }

        for (const child of el.children) {
            const childNode = buildTree(child, depth + 1);
            if (childNode) node.children.push(childNode);
        }

        return node;
    };

    return buildTree(document.body);
}"""

JS_GET_PAGE_HEIGHT = """() => Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight
)"""


# ═══════════════════════════════════════════════════════════════════
# Main Analyzer Class
# ═══════════════════════════════════════════════════════════════════

class DeepSiteAnalyzer:
    """
    Comprehensive Playwright-based website analyzer.

    Captures every visual and structural aspect of a website, producing
    a rich JSON data package consumed by the template generation pipeline.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def analyze(
        self,
        url: str,
        out_dir: str = "storage/deep_analysis",
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        scroll_screenshot_interval: int = 800,
        max_scroll_screenshots: int = 20,
    ) -> DeepAnalysisResult:
        """
        Perform deep analysis on a URL.

        Parameters
        ----------
        url : str
            The website URL to analyze.
        out_dir : str
            Directory to save screenshots and analysis JSON.
        viewport_width, viewport_height : int
            Browser viewport dimensions.
        scroll_screenshot_interval : int
            Pixels between each scroll-position screenshot.
        max_scroll_screenshots : int
            Maximum number of scroll-position screenshots to take.

        Returns
        -------
        DeepAnalysisResult with all extracted data.
        """
        os.makedirs(out_dir, exist_ok=True)
        ts = int(time.time())
        start_time = time.time()

        logger.info("═══ Deep Site Analyzer: Starting analysis of %s ═══", url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                bypass_csp=True,
            )
            page = await context.new_page()

            # ── Navigate ──────────────────────────────────────────
            logger.info("Step 1/10: Navigating to %s", url)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)  # Let hero animations run

            final_url = page.url
            title = await page.title()

            # ── Meta description ──────────────────────────────────
            meta_desc = await page.evaluate("""() => {
                const m = document.querySelector('meta[name="description"]');
                return m ? (m.getAttribute('content') || '') : '';
            }""")

            # ── Page height ──────────────────────────────────────
            page_height = await page.evaluate(JS_GET_PAGE_HEIGHT)
            logger.info("Page height: %dpx", page_height)

            # ── Step 2: Extract CSS Variables ────────────────────
            logger.info("Step 2/10: Extracting CSS variables")
            css_variables = await page.evaluate(JS_EXTRACT_CSS_VARIABLES) or {}

            # ── Step 3: Extract Computed Styles ──────────────────
            logger.info("Step 3/10: Extracting computed styles")
            computed_styles = await page.evaluate(JS_EXTRACT_COMPUTED_STYLES) or {}

            # ── Step 4: Extract Fonts ────────────────────────────
            logger.info("Step 4/10: Extracting font information")
            fonts = await page.evaluate(JS_EXTRACT_FONTS) or []

            # ── Step 5: Extract Colors ───────────────────────────
            logger.info("Step 5/10: Extracting color palette")
            colors = await page.evaluate(JS_EXTRACT_COLORS) or []

            # ── Step 6: Extract Sections ─────────────────────────
            logger.info("Step 6/10: Extracting page sections")
            sections = await page.evaluate(JS_EXTRACT_SECTIONS) or []

            # ── Step 7: Extract Animations ───────────────────────
            logger.info("Step 7/10: Detecting animations & transitions")
            animations = await page.evaluate(JS_EXTRACT_ANIMATIONS) or []

            # ── Step 8: Extract Layouts ──────────────────────────
            logger.info("Step 8/10: Analyzing layout patterns")
            layouts = await page.evaluate(JS_EXTRACT_LAYOUTS) or []

            # ── Step 9: Extract Navigation, Footer, Headings ────
            logger.info("Step 9/10: Extracting navigation, footer, headings, images")
            navigation = await page.evaluate(JS_EXTRACT_NAVIGATION) or {}
            footer = await page.evaluate(JS_EXTRACT_FOOTER) or {}
            headings = await page.evaluate(JS_EXTRACT_HEADINGS) or []
            image_data = await page.evaluate(JS_EXTRACT_IMAGES) or {}
            dom_structure = await page.evaluate(JS_EXTRACT_DOM_STRUCTURE) or {}

            # ── Step 10: Scroll-Position Screenshots ─────────────
            logger.info("Step 10/10: Capturing scroll-position screenshots")
            scroll_screenshots = []

            # Full-page screenshot first
            full_page_path = os.path.join(out_dir, f"deep_{ts}_fullpage.png")
            await page.screenshot(path=full_page_path, full_page=True)

            # Scroll-position screenshots at regular intervals
            num_screenshots = min(
                max_scroll_screenshots,
                max(1, page_height // scroll_screenshot_interval)
            )

            for i in range(num_screenshots):
                scroll_y = i * scroll_screenshot_interval
                await page.evaluate(f"window.scrollTo(0, {scroll_y})")
                await asyncio.sleep(0.5)  # Wait for scroll animations to trigger

                shot_path = os.path.join(out_dir, f"deep_{ts}_scroll_{scroll_y}.png")
                await page.screenshot(path=shot_path)
                scroll_screenshots.append(shot_path)
                logger.info("  Screenshot at scroll=%dpx → %s", scroll_y, shot_path)

            # ── Scroll down to trigger all lazy/scroll elements ──
            # Then re-extract sections (they may have new content loaded)
            logger.info("Triggering all scroll-reveal elements...")
            for scroll_pos in range(0, page_height, 600):
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                await asyncio.sleep(0.3)
            await asyncio.sleep(1)

            # Re-capture sections after full scroll (may have new revealed content)
            sections_post_scroll = await page.evaluate(JS_EXTRACT_SECTIONS) or []
            if len(sections_post_scroll) > len(sections):
                logger.info("Found %d additional sections after scroll reveal", len(sections_post_scroll) - len(sections))
                sections = sections_post_scroll

            await browser.close()

        elapsed = time.time() - start_time
        logger.info("═══ Deep Site Analyzer: Completed in %.1fs ═══", elapsed)

        # ── Build result ────────────────────────────────────────
        result = DeepAnalysisResult(
            url=url,
            final_url=final_url,
            title=title,
            meta_description=meta_desc,
            fonts=fonts,
            colors=colors,
            sections=sections,
            animations=animations,
            layouts=layouts,
            css_variables=css_variables,
            computed_styles=computed_styles,
            headings=headings,
            navigation=navigation,
            footer=footer,
            images=image_data.get("images", []),
            svgs=image_data.get("svgs", 0),
            canvases=image_data.get("canvases", 0),
            icons_library=image_data.get("icons_library"),
            scroll_screenshots=scroll_screenshots,
            full_page_screenshot=full_page_path,
            page_height=page_height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            dom_structure=dom_structure,
            analysis_duration_seconds=round(elapsed, 2),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

        # ── Save JSON ──────────────────────────────────────────
        json_path = os.path.join(out_dir, f"deep_{ts}_analysis.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self._serialize(result), f, indent=2, ensure_ascii=False)
        result.analysis_json_path = json_path

        logger.info("Analysis JSON saved → %s", json_path)
        logger.info("  Fonts: %d | Colors: %d | Sections: %d | Animations: %d | Layouts: %d",
                     len(fonts), len(colors), len(sections), len(animations), len(layouts))
        logger.info("  Headings: %d | Images: %d | SVGs: %d | Canvases: %d",
                     len(headings), len(image_data.get("images", [])),
                     image_data.get("svgs", 0), image_data.get("canvases", 0))
        logger.info("  Screenshots: %d scroll positions + 1 full page", len(scroll_screenshots))

        return result

    def _serialize(self, result: DeepAnalysisResult) -> dict:
        """Convert result to JSON-serializable dict."""
        return {
            "url": result.url,
            "final_url": result.final_url,
            "title": result.title,
            "meta_description": result.meta_description,
            "fonts": result.fonts,
            "colors": result.colors,
            "sections": result.sections,
            "animations": result.animations,
            "layouts": result.layouts,
            "css_variables": result.css_variables,
            "computed_styles": result.computed_styles,
            "headings": result.headings,
            "navigation": result.navigation,
            "footer": result.footer,
            "images": result.images,
            "svgs": result.svgs,
            "canvases": result.canvases,
            "icons_library": result.icons_library,
            "scroll_screenshots": result.scroll_screenshots,
            "full_page_screenshot": result.full_page_screenshot,
            "page_height": result.page_height,
            "viewport_width": result.viewport_width,
            "viewport_height": result.viewport_height,
            "dom_structure": result.dom_structure,
            "analysis_duration_seconds": result.analysis_duration_seconds,
            "timestamp": result.timestamp,
        }
