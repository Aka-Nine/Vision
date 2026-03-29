import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from playwright.async_api import async_playwright


@dataclass
class WebsiteCaptureResult:
    screenshot_path: str
    video_path: str
    final_url: str
    audit_path: Optional[str] = None
    screenshots_by_viewport: Optional[Dict[str, str]] = None
    trace_path: Optional[str] = None
    har_path: Optional[str] = None
    events_path: Optional[str] = None
    deep_analysis_path: Optional[str] = None  # Path to deep analysis JSON


async def capture_website_video(
    *,
    url: str,
    out_dir: str = "storage/visuals",
    viewport_width: int = 1440,
    viewport_height: int = 900,
    record_seconds: int = 10,
    deep_audit: bool = True,
    deterministic_interactions: bool = True,
    safe_clicks: bool = True,
    trace: bool = True,
    deep_analyze: bool = False,
) -> WebsiteCaptureResult:
    """
    Captures:
    - a full-page screenshot
    - a short interaction video (webm)

    The goal is to preserve motion/scroll animations for screenshot-to-code video mode.
    """
    os.makedirs(out_dir, exist_ok=True)
    ts = int(time.time())
    shot_path = os.path.join(out_dir, f"capture_{ts}.png")
    audit_path = os.path.join(out_dir, f"capture_{ts}_audit.json") if deep_audit else None
    spector_path = os.path.join(out_dir, f"capture_{ts}_spector.json") if deep_audit else None
    trace_path = os.path.join(out_dir, f"capture_{ts}_trace.zip") if trace else None
    har_path = os.path.join(out_dir, f"capture_{ts}.har") if trace else None
    events_path = os.path.join(out_dir, f"capture_{ts}_events.jsonl") if trace else None
    screenshots_by_viewport: Dict[str, str] = {}

    def _emit_event(evt: Dict[str, Any]) -> None:
        if not events_path:
            return
        try:
            import json
            evt = dict(evt)
            evt.setdefault("ts", time.time())
            with open(events_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        except Exception:
            pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            record_video_dir=out_dir,
            bypass_csp=True,
            record_har_path=har_path,
            record_har_content="embed",
        )

        if trace and trace_path:
            try:
                await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            except Exception:
                pass

        # Context-level instrumentation (B)
        try:
            context.on("worker", lambda w: _emit_event({"type": "worker_created", "url": getattr(w, "url", None)}))
        except Exception:
            pass

        # Pre-inject Spector so it can hook WebGL contexts created early.
        if spector_path:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get("https://unpkg.com/spectorjs/dist/spector.bundle.js")
                    if resp.status_code == 200 and resp.text:
                        await context.add_init_script(resp.text)
            except Exception:
                pass

        page = await context.new_page()

        # Page-level instrumentation (B)
        try:
            page.on("console", lambda m: _emit_event({"type": "console", "level": m.type, "text": m.text}))
            page.on("pageerror", lambda e: _emit_event({"type": "pageerror", "error": str(e)}))
            page.on("request", lambda r: _emit_event({"type": "request", "method": r.method, "url": r.url}))
            page.on("response", lambda r: _emit_event({"type": "response", "status": r.status, "url": r.url}))
            def _on_request_failed(r):
                try:
                    failure = None
                    try:
                        failure = r.failure
                    except Exception:
                        failure = None
                    if callable(failure):
                        failure = failure()
                    if isinstance(failure, dict):
                        failure = failure.get("errorText")
                    _emit_event({"type": "requestfailed", "url": r.url, "failure": failure})
                except Exception:
                    pass

            page.on("requestfailed", _on_request_failed)
        except Exception:
            pass

        await page.goto(url, wait_until="networkidle", timeout=60000)

        # Let hero animations run.
        await asyncio.sleep(2)

        # Inject Spector.js to capture WebGL/canvas frames (best-effort).
        if spector_path:
            try:
                try:
                    await page.wait_for_function("() => !!(window.SPECTOR && window.SPECTOR.Spector)", timeout=5000)
                except Exception:
                    pass
                await page.evaluate(
                    """() => {
                      window.__mcp_spector = null;
                      window.__mcp_spector_captures = [];
                      window.__mcp_spector_error = null;
                      window.__mcp_spector_ready = false;
                      if (window.SPECTOR && window.SPECTOR.Spector) {
                        const s = new window.SPECTOR.Spector();
                        // Don't show UI; just capture.
                        s.spyCanvases();
                        s.onCapture.add(function(c) { window.__mcp_spector_captures.push(c); });
                        s.onError.add(function(e) { window.__mcp_spector_error = e; });
                        window.__mcp_spector = s;
                        window.__mcp_spector_ready = true;
                      } else {
                        window.__mcp_spector_error = "SPECTOR namespace not found after injection";
                      }
                    }"""
                )
            except Exception:
                pass

        # Hover every visible interactive element (captures cursor/hover effects).
        try:
            await page.evaluate(
                """() => {
                  window.__mcp_hover_targets = Array.from(document.querySelectorAll('a,button,[role="button"],input,select,textarea,[tabindex]'))
                    .filter(el => {
                      const r = el.getBoundingClientRect();
                      const cs = getComputedStyle(el);
                      return r.width > 2 && r.height > 2 && r.bottom > 0 && r.right > 0 &&
                             r.top < (window.innerHeight * 1.2) && r.left < (window.innerWidth * 1.2) &&
                             cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0';
                    })
                    .slice(0, 80)
                    .map(el => ({ x: Math.round(el.getBoundingClientRect().left + el.getBoundingClientRect().width/2),
                                 y: Math.round(el.getBoundingClientRect().top + el.getBoundingClientRect().height/2) }));
                }"""
            )
            targets = await page.evaluate("() => window.__mcp_hover_targets || []")
            for t in targets:
                await page.mouse.move(t["x"], t["y"])
                await asyncio.sleep(0.12)
        except Exception:
            pass

        # Deterministic interaction runner (C)
        if deterministic_interactions:
            try:
                _emit_event({"type": "interaction_start"})

                # Mouse path sweeps (cursor-driven effects)
                for x in range(80, viewport_width - 80, 160):
                    await page.mouse.move(x, int(viewport_height * 0.35))
                    await asyncio.sleep(0.06)
                for x in range(viewport_width - 80, 80, -160):
                    await page.mouse.move(x, int(viewport_height * 0.55))
                    await asyncio.sleep(0.06)

                # Deep scroll to trigger reveal effects
                for _ in range(12):
                    await page.mouse.wheel(0, 900)
                    await asyncio.sleep(0.75)
                await page.mouse.wheel(0, -1600)
                await asyncio.sleep(1.0)

                # Safe clicks: only same-page anchors + visible buttons
                if safe_clicks:
                    await page.evaluate(
                        """() => {
                          const els = Array.from(document.querySelectorAll('a,button,[role=\"button\"]'));
                          const isVisible = (el) => {
                            const r = el.getBoundingClientRect();
                            const cs = getComputedStyle(el);
                            return r.width > 4 && r.height > 4 && r.bottom > 0 && r.right > 0 &&
                                   r.top < window.innerHeight && r.left < window.innerWidth &&
                                   cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0';
                          };
                          const out = [];
                          for (const el of els) {
                            if (!isVisible(el)) continue;
                            if (el.tagName.toLowerCase() === 'a') {
                              const href = el.getAttribute('href') || '';
                              if (href.startsWith('#') || href === '' || href === '/') out.push(el);
                            } else out.push(el);
                            if (out.length >= 20) break;
                          }
                          window.__mcp_safe_click_targets = out.map(el => {
                            const r = el.getBoundingClientRect();
                            return { x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2) };
                          });
                        }"""
                    )
                    click_targets = await page.evaluate("() => window.__mcp_safe_click_targets || []")
                    for t in click_targets:
                        await page.mouse.click(t["x"], t["y"])
                        await asyncio.sleep(0.25)

                _emit_event({"type": "interaction_end"})
            except Exception as e:
                _emit_event({"type": "interaction_error", "error": str(e)})
        else:
            # Legacy scroll
            for _ in range(8):
                await page.mouse.wheel(0, 900)
                await asyncio.sleep(0.8)
            await page.mouse.wheel(0, -1200)
            await asyncio.sleep(1.0)

        # Trigger WebGL capture on any canvas elements (best-effort).
        if spector_path:
            try:
                await page.evaluate(
                    """() => {
                      const s = window.__mcp_spector;
                      if (!s) return;
                      const canvases = Array.from(document.querySelectorAll('canvas')).slice(0, 8);
                      let captured = false;
                      let webglFound = 0;
                      for (const c of canvases) {
                        let ctx = null;
                        try { ctx = c.getContext('webgl2'); } catch(e) {}
                        if (!ctx) { try { ctx = c.getContext('webgl'); } catch(e) {} }
                        if (!ctx) { try { ctx = c.getContext('experimental-webgl'); } catch(e) {} }
                        if (ctx) {
                          webglFound++;
                          try {
                            // Start a short capture window; will auto-stop after commandCount or timeout.
                            s.startCapture(ctx, 300, true);
                            captured = true;
                            break;
                          } catch (e) {
                            window.__mcp_spector_error = String(e);
                          }
                        }
                      }
                      window.__mcp_spector_webglFound = webglFound;
                      window.__mcp_spector_captureRequested = captured;
                    }"""
                )
                await asyncio.sleep(8.0)
                # stopCapture returns ICapture (or undefined if not completed)
                await page.evaluate(
                    """() => {
                      const s = window.__mcp_spector;
                      if (!s) return;
                      try {
                        const c = s.stopCapture();
                        if (c) window.__mcp_spector_captures.push(c);
                      } catch (e) {
                        window.__mcp_spector_error = String(e);
                      }
                    }"""
                )

                spector_json = await page.evaluate(
                    """() => {
                      const meta = {
                        ready: !!window.__mcp_spector_ready,
                        error: window.__mcp_spector_error || null,
                        canvasCount: document.querySelectorAll('canvas').length,
                        webglFound: window.__mcp_spector_webglFound || 0,
                        captureRequested: !!window.__mcp_spector_captureRequested,
                        captureCount: (window.__mcp_spector_captures || []).length,
                      };
                      const captures = (window.__mcp_spector_captures || []).slice(0, 2);
                      const safe = { url: location.href, meta, captures };
                      const replacer = (_k, v) => (typeof v === 'bigint' ? v.toString() : v);
                      try {
                        return JSON.stringify(safe, replacer);
                      } catch (e) {
                        return JSON.stringify({ url: location.href, meta, error: String(e) });
                      }
                    }"""
                )

                with open(spector_path, "w", encoding="utf-8") as f:
                    f.write(spector_json or "")
            except Exception:
                pass

        # Capture multi-viewport screenshots to preserve sizing/alignment.
        viewports = [
            ("desktop_1440x900", 1440, 900),
            ("tablet_768x900", 768, 900),
            ("mobile_390x844", 390, 844),
        ]
        for label, w, h in viewports:
            try:
                await page.set_viewport_size({"width": w, "height": h})
                await asyncio.sleep(0.6)
                pth = os.path.join(out_dir, f"capture_{ts}_{label}.png")
                await page.screenshot(path=pth, full_page=True)
                screenshots_by_viewport[label] = pth
            except Exception:
                pass

        # Default full-page screenshot.
        await page.set_viewport_size({"width": viewport_width, "height": viewport_height})
        await asyncio.sleep(0.4)
        await page.screenshot(path=shot_path, full_page=True)

        final_url = page.url

        # Deep audit: extract computed styles, font usage, and element boxes.
        if audit_path:
            try:
                audit = await page.evaluate(
                    """() => {
                      const pick = (el) => {
                        const r = el.getBoundingClientRect();
                        const cs = getComputedStyle(el);
                        const href = el.getAttribute && el.getAttribute('href');
                        const text = (el.textContent || '').trim().slice(0, 160);
                        return {
                          tag: el.tagName.toLowerCase(),
                          id: el.id || null,
                          classes: (el.className && typeof el.className === 'string') ? el.className.split(/\\s+/).slice(0, 40) : [],
                          role: el.getAttribute && el.getAttribute('role'),
                          ariaLabel: el.getAttribute && el.getAttribute('aria-label'),
                          href: href ? href : null,
                          text,
                          box: { x: r.x, y: r.y, w: r.width, h: r.height },
                          style: {
                            fontFamily: cs.fontFamily,
                            fontSize: cs.fontSize,
                            fontWeight: cs.fontWeight,
                            lineHeight: cs.lineHeight,
                            letterSpacing: cs.letterSpacing,
                            color: cs.color,
                            backgroundColor: cs.backgroundColor,
                            borderRadius: cs.borderRadius,
                            border: cs.border,
                            boxShadow: cs.boxShadow,
                            opacity: cs.opacity,
                            transform: cs.transform,
                            transition: cs.transition,
                            animation: cs.animation,
                          },
                        };
                      };

                      const interactive = Array.from(document.querySelectorAll('a,button,[role="button"],input,select,textarea'))
                        .slice(0, 250)
                        .map(pick);

                      const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4'))
                        .slice(0, 120)
                        .map(pick);

                      const fonts = (document.fonts && document.fonts.size)
                        ? Array.from(document.fonts).slice(0, 200).map(f => ({
                            family: f.family,
                            style: f.style,
                            weight: f.weight,
                            stretch: f.stretch,
                            status: f.status
                          }))
                        : [];

                      const rootStyles = getComputedStyle(document.documentElement);
                      const cssVars = {};
                      for (let i=0; i<rootStyles.length; i++) {
                        const k = rootStyles[i];
                        if (k && k.startsWith('--')) cssVars[k] = rootStyles.getPropertyValue(k).trim();
                      }

                      return {
                        url: location.href,
                        title: document.title,
                        viewport: { w: window.innerWidth, h: window.innerHeight, dpr: window.devicePixelRatio },
                        fonts,
                        cssVars,
                        interactive,
                        headings,
                      };
                    }"""
                )
                import json
                with open(audit_path, "w", encoding="utf-8") as f:
                    json.dump(audit, f, indent=2)
            except Exception:
                pass

        if trace and trace_path:
            try:
                await context.tracing.stop(path=trace_path)
            except Exception:
                pass

        await context.close()
        await browser.close()

    # Playwright stores the video under out_dir, but the file name is generated.
    # We pick the newest webm file in out_dir.
    newest = None
    newest_mtime = -1.0
    for name in os.listdir(out_dir):
        if not name.lower().endswith(".webm"):
            continue
        pth = os.path.join(out_dir, name)
        try:
            mt = os.path.getmtime(pth)
        except OSError:
            continue
        if mt > newest_mtime:
            newest_mtime = mt
            newest = pth

    if not newest:
        raise RuntimeError("Failed to find recorded .webm video output from Playwright.")

    # ── Optional Deep Analysis ───────────────────────────────────
    deep_analysis_path = None
    if deep_analyze:
        try:
            from services.deep_site_analyzer import DeepSiteAnalyzer
            import logging as _log
            _log.getLogger(__name__).info("Running DeepSiteAnalyzer for comprehensive data extraction...")
            analyzer = DeepSiteAnalyzer(headless=True)
            deep_result = await analyzer.analyze(
                url=url,
                out_dir=os.path.join(out_dir, "deep_analysis"),
                viewport_width=viewport_width,
                viewport_height=viewport_height,
            )
            deep_analysis_path = deep_result.analysis_json_path
            _log.getLogger(__name__).info("Deep analysis saved → %s", deep_analysis_path)
        except Exception as e:
            import logging as _log
            _log.getLogger(__name__).warning("Deep analysis failed (non-fatal): %s", e)

    return WebsiteCaptureResult(
        screenshot_path=shot_path,
        video_path=newest,
        final_url=final_url,
        audit_path=audit_path if audit_path and os.path.isfile(audit_path) else None,
        screenshots_by_viewport=screenshots_by_viewport or None,
        trace_path=trace_path if trace_path and os.path.isfile(trace_path) else None,
        har_path=har_path if har_path and os.path.isfile(har_path) else None,
        events_path=events_path if events_path and os.path.isfile(events_path) else None,
        deep_analysis_path=deep_analysis_path,
    )

