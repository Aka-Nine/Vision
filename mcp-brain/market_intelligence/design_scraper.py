import logging
from app.config import settings
from playwright.async_api import async_playwright
import urllib.parse
import asyncio
import os
import re
from utils.scraper_rate_limiter import rate_limiter
from utils.cache import cache

class DesignScraper:
    async def scrape(self, trend: dict):
        if settings.market_data_provider == "paid" and settings.apify_api_key:
            return {
                "title": f"Dribbble Pro Output for {trend.get('trend', 'SaaS')}",
                "image_urls": ["https://cdn.dribbble.com/users/premium_image.png"],
                "components": ["hero", "pricing", "features"],
                "style": "clean modern",
                "animations": ["hover", "cursor_follow"]
            }
        
        target_topic = trend.get('trend', 'SaaS')
        clean_topic = target_topic.replace("UI for: ", "").replace("Reddit Theme: ", "")

        cache_key = f"scrape_{clean_topic.replace(' ', '_')}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        reference_url = trend.get('reference_url')
        if reference_url:
            result = await self.scrape_live_website(reference_url, clean_topic)
        # If the user has supplied Pinterest Credentials, we run the Pinterest Scraper natively!
        elif settings.pinterest_email and settings.pinterest_password:
            result = await self.scrape_pinterest(clean_topic)
        else:
            result = await self.scrape_dribbble(clean_topic)
            
        cache.set(cache_key, result)
        return result

    async def scrape_pinterest(self, clean_topic: str):
        safe_query = urllib.parse.quote(clean_topic + " ui design")
        search_url = f"https://www.pinterest.com/search/pins/?q={safe_query}"
        
        scraped_data = {
            "title": f"Live Scraped Pinterest UI for {clean_topic}",
            "image_urls": [],
            "source": f"Scraped from Pinterest: {clean_topic}",
            "reference_pages": [],
            "components": ["hero_section", "features_grid", "pricing_cards"],
            "style": "modern",
            "animations": ["fade_in", "scroll_reveal"]
        }

        try:
            await rate_limiter.wait()
            logging.info("Starting Pinterest scraping flow...")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False) # Changed to False so you can see it!
                context = await browser.new_context(
                    user_agent=rate_limiter.get_user_agent(),
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                # 1. Login to Pinterest
                logging.info("Logging into Pinterest...")
                await page.goto("https://www.pinterest.com/login/")
                await page.wait_for_selector('input[id="email"]', timeout=15000)
                await page.fill('input[id="email"]', settings.pinterest_email)
                await page.fill('input[id="password"]', settings.pinterest_password)
                
                await page.keyboard.press("Enter")
                
                # Wait for login to complete and dashboard to load
                await page.wait_for_selector('div[data-test-id="pin"]', timeout=20000)
                logging.info("Pinterest Login Successful!")
                
                # 2. Search
                logging.info(f"Navigating to search: {search_url}")
                await page.goto(search_url, wait_until="domcontentloaded")
                
                # Wait for pins to load in the grid
                await page.wait_for_selector('div[data-test-id="pin"] img', timeout=15000)
                
                # 3. Extract High Resolution Images
                pin_imgs = await page.query_selector_all('div[data-test-id="pin"] img')
                valid_images = []
                pin_pages = []
                for img in pin_imgs:
                    src = await img.get_attribute('src')
                    if src and "i.pinimg.com" in src:
                        # Convert Pinterest thumbnails (236x) into crisp high-res UI references (736x)
                        large_src = src.replace("236x", "736x")
                        valid_images.append(large_src)

                        # Best-effort: extract a pin page url from the closest anchor.
                        try:
                            anchor = await img.evaluate_handle(
                                "(el) => el.closest('a')"
                            )
                            href = await anchor.get_property("href") if anchor else None
                            href_val = await href.json_value() if href else None
                            if href_val and isinstance(href_val, str) and "pinterest.com/pin/" in href_val:
                                pin_pages.append(href_val)
                        except Exception:
                            pass
                    if len(valid_images) >= 4:
                        break
                
                scraped_data['image_urls'] = valid_images

                # 4. Visit a couple pins to capture UI context (title/meta + screenshot)
                scraped_data["reference_pages"] = await self._capture_reference_pages(
                    context=context,
                    urls=pin_pages[:2],
                    source="pinterest",
                    topic=clean_topic,
                )
                await browser.close()
                logging.info(f"Successfully scraped {len(valid_images)} images from Pinterest.")
                
        except Exception as e:
            logging.error(f"Pinterest Scraping Failed: {e}")
            scraped_data['image_urls'] = ["https://placehold.co/800x600/png?text=Pinterest+Blocked+or+Timeout"]
            
        return scraped_data

    async def scrape_dribbble(self, clean_topic: str):
        safe_query = urllib.parse.quote(clean_topic + " website template")
        dribbble_url = f"https://dribbble.com/search/shots/recent?q={safe_query}"
        
        scraped_data = {
            "title": f"Live Scraped Dribbble UI for {clean_topic}",
            "image_urls": [],
            "source": f"Scraped from Dribbble: {clean_topic}",
            "reference_pages": [],
            "components": ["hero_section", "features_grid", "pricing_cards"],
            "style": "modern",
            "animations": ["fade_in", "scroll_reveal"]
        }

        try:
            await rate_limiter.wait()
            logging.info(f"Opening headless browser to scrape: {dribbble_url}")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    user_agent=rate_limiter.get_user_agent(),
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                await page.goto(dribbble_url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_selector('li.shot-thumbnail figure img', timeout=10000)
                
                shots = await page.query_selector_all('li.shot-thumbnail a.shot-thumbnail-link, li.shot-thumbnail a')
                
                valid_images = []
                shot_pages = []
                for a in shots:
                    href = await a.get_attribute("href")
                    if href and href.startswith("/shots/"):
                        shot_pages.append("https://dribbble.com" + href)
                    if len(valid_images) >= 4:
                        break

                # fallback to images if we couldn't find shot links
                if not shot_pages:
                    images = await page.query_selector_all('li.shot-thumbnail figure img')
                    for img in images:
                        src = await img.get_attribute('src')
                        if src and "cdn.dribbble.com" in src:
                            large_src = src.replace("?compress=1&resize=400x300", "?compress=1&resize=1000x750")
                            valid_images.append(large_src)
                        if len(valid_images) >= 4:
                            break
                
                scraped_data['image_urls'] = valid_images
                scraped_data["reference_pages"] = await self._capture_reference_pages(
                    context=context,
                    urls=shot_pages[:2],
                    source="dribbble",
                    topic=clean_topic,
                )
                
                await browser.close()
                logging.info(f"Successfully scraped {len(valid_images)} images from Dribbble.")
                
        except Exception as e:
            logging.error(f"Playwright Scraping Failed: {e}")
            scraped_data['image_urls'] = ["https://placehold.co/800x600/png?text=Playwright+Blocked+or+Timeout"]
            
        return scraped_data

    async def scrape_live_website(self, url: str, clean_topic: str):
        """
        Enhanced live website scraping using DeepSiteAnalyzer.

        Captures comprehensive data: CSS, fonts, colors, animations,
        sections, layouts, scroll screenshots, DOM structure, and more.
        Falls back to basic scrape if deep analysis fails.
        """
        scraped_data = {
            "title": f"Live Website: {clean_topic}",
            "image_urls": [],
            "source": f"Deep Scraped Live Website: {url}",
            "reference_pages": [],
            "components": [],
            "style": "unknown",
            "animations": [],
            # Enhanced fields from deep analysis
            "deep_analysis": None,
            "fonts": [],
            "color_palette": [],
            "layout_patterns": [],
            "dom_structure": None,
            "css_variables": {},
            "computed_styles": {},
            "navigation": {},
            "footer": {},
            "page_metrics": {},
        }

        try:
            await rate_limiter.wait()
            logging.info(f"═══ Starting DEEP analysis of live site: {url} ═══")

            # Use the comprehensive DeepSiteAnalyzer
            from services.deep_site_analyzer import DeepSiteAnalyzer

            out_dir = os.path.join("storage", "deep_analysis", re.sub(r"[^a-zA-Z0-9_-]+", "_", clean_topic)[:60])
            analyzer = DeepSiteAnalyzer(headless=True)

            result = await analyzer.analyze(
                url=url,
                out_dir=out_dir,
                viewport_width=1920,
                viewport_height=1080,
                scroll_screenshot_interval=800,
                max_scroll_screenshots=15,
            )

            # ── Map deep analysis results into scraped_data ──────
            scraped_data["title"] = result.title or f"Live Website: {clean_topic}"
            scraped_data["local_screenshot"] = result.full_page_screenshot

            # Extract component types from sections
            scraped_data["components"] = list(set(
                s.get("component_type", "generic_section")
                for s in result.sections
                if s.get("component_type")
            ))

            # Extract style theme from colors
            bg_colors = [c for c in result.colors if "bg" in c.get("usage", "")]
            text_colors = [c for c in result.colors if "text" in c.get("usage", "")]
            if bg_colors:
                primary_bg = bg_colors[0].get("hex", "#ffffff")
                # Determine light vs dark theme
                try:
                    r = int(primary_bg[1:3], 16) if len(primary_bg) >= 7 else 255
                    g = int(primary_bg[3:5], 16) if len(primary_bg) >= 7 else 255
                    b = int(primary_bg[5:7], 16) if len(primary_bg) >= 7 else 255
                    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                    scraped_data["style"] = "dark" if luminance < 0.5 else "light"
                except Exception:
                    scraped_data["style"] = "modern"

            # Extract animation types
            scraped_data["animations"] = list(set(
                a.get("type", "unknown") for a in result.animations
            ))

            # Store full deep analysis data for downstream processing
            scraped_data["fonts"] = result.fonts
            scraped_data["color_palette"] = result.colors
            scraped_data["layout_patterns"] = result.layouts
            scraped_data["dom_structure"] = result.dom_structure
            scraped_data["css_variables"] = result.css_variables
            scraped_data["computed_styles"] = result.computed_styles
            scraped_data["navigation"] = result.navigation
            scraped_data["footer"] = result.footer
            scraped_data["page_metrics"] = {
                "page_height": result.page_height,
                "viewport_width": result.viewport_width,
                "viewport_height": result.viewport_height,
                "section_count": len(result.sections),
                "heading_count": len(result.headings),
                "image_count": len(result.images),
                "svg_count": result.svgs,
                "canvas_count": result.canvases,
                "icons_library": result.icons_library,
                "animation_count": len(result.animations),
                "analysis_duration": result.analysis_duration_seconds,
            }

            # Build rich reference pages from sections
            scraped_data["reference_pages"] = [{
                "url": result.final_url,
                "source": "deep_site_analysis",
                "title": result.title,
                "meta_description": result.meta_description,
                "local_screenshot": result.full_page_screenshot,
                "scroll_screenshots": result.scroll_screenshots,
                "sections": result.sections,
                "headings": result.headings,
                "ui_text": {
                    "headings": [h.get("text", "") for h in result.headings],
                    "ctas": list(set(
                        cta for s in result.sections
                        for cta in s.get("cta_texts", [])
                    ))[:30],
                },
                "deep_analysis_json": result.analysis_json_path,
            }]

            # Store the analysis JSON path for the pipeline
            scraped_data["deep_analysis"] = result.analysis_json_path

            logging.info(f"═══ Deep analysis complete: {len(result.sections)} sections, "
                         f"{len(result.fonts)} fonts, {len(result.colors)} colors, "
                         f"{len(result.animations)} animations captured in {result.analysis_duration_seconds}s ═══")

        except Exception as e:
            logging.error(f"Deep analysis failed: {e} — falling back to basic scrape")
            # Fallback to basic scrape
            try:
                await self._basic_scrape_live(url, clean_topic, scraped_data)
            except Exception as e2:
                logging.error(f"Basic scrape also failed: {e2}")
                scraped_data['image_urls'] = ["https://placehold.co/800x600/png?text=Live+Site+Blocked"]

        return scraped_data

    async def _basic_scrape_live(self, url: str, clean_topic: str, scraped_data: dict):
        """Fallback basic scrape when deep analysis fails."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=rate_limiter.get_user_agent(),
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until="networkidle")

            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

            os.makedirs("storage/visuals", exist_ok=True)
            screenshot_path = f"storage/visuals/live_scrape_{hash(url)}.png"
            await page.screenshot(path=screenshot_path, full_page=True)

            scraped_data["local_screenshot"] = screenshot_path
            scraped_data["reference_pages"] = [
                await self._extract_page_context(page, url=url, source="live_site", screenshot_path=screenshot_path)
            ]

            await browser.close()
            logging.info(f"Basic scrape captured at {screenshot_path}")

    async def _capture_reference_pages(self, *, context, urls, source: str, topic: str):
        if not urls:
            return []

        os.makedirs("storage/visuals", exist_ok=True)
        out = []
        page = await context.new_page()
        for i, url in enumerate(urls, 1):
            try:
                await rate_limiter.wait()
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(1)

                safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", f"{source}_{topic}")[:80]
                screenshot_path = os.path.join("storage", "visuals", f"{safe}_{i}.png")
                await page.screenshot(path=screenshot_path, full_page=True)

                out.append(
                    await self._extract_page_context(page, url=url, source=source, screenshot_path=screenshot_path)
                )
            except Exception as e:
                logging.warning(f"Failed to capture reference page {url}: {e}")
        await page.close()
        return out

    async def _extract_page_context(self, page, *, url: str, source: str, screenshot_path: str):
        """
        Pull a compact "UI context" payload from a page:
        - title, meta description
        - a small set of visible headings and CTA-like button/link texts
        - a truncated html snapshot (best-effort)
        """
        title = ""
        description = ""
        try:
            title = await page.title()
        except Exception:
            pass
        try:
            description = await page.evaluate(
                """() => {
                  const m = document.querySelector('meta[name="description"]');
                  return m ? (m.getAttribute('content') || '') : '';
                }"""
            )
        except Exception:
            pass

        try:
            ui_text = await page.evaluate(
                """() => {
                  const uniq = (arr) => Array.from(new Set(arr.map(s => (s||'').trim()).filter(Boolean)));
                  const headings = uniq(Array.from(document.querySelectorAll('h1,h2,h3')).slice(0,20).map(e => e.textContent));
                  const ctas = uniq(Array.from(document.querySelectorAll('a,button')).slice(0,80)
                    .map(e => e.textContent)
                    .filter(t => t && t.trim().length >= 2 && t.trim().length <= 40)
                  ).slice(0,20);
                  return { headings, ctas };
                }"""
            )
        except Exception:
            ui_text = {"headings": [], "ctas": []}

        try:
            html = await page.content()
            html = html[:200_000]
        except Exception:
            html = ""

        return {
            "url": url,
            "source": source,
            "title": title,
            "meta_description": description,
            "ui_text": ui_text,
            "html_snippet": html,
            "local_screenshot": screenshot_path,
        }

