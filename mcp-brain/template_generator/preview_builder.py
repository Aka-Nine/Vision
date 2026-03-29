"""
Preview Builder — Phase 3 Module
Launches a headless browser via Playwright to render the generated
template and capture a screenshot preview.
"""
import os, logging, asyncio

logger = logging.getLogger(__name__)


class PreviewBuilder:
    """Build a preview screenshot of the generated template."""

    async def build(self, project_dir: str) -> dict:
        """
        Attempts to:
        1. Install npm deps
        2. Start dev server
        3. Screenshot via Playwright

        Falls back gracefully if Playwright or Node is unavailable.
        """
        preview_path = os.path.join(project_dir, "preview.png")
        dist_dir = os.path.join(project_dir, "dist")

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.warning("Playwright not installed — skipping preview generation")
            return {"preview": None, "skipped": True, "reason": "playwright not installed"}

        try:
            # Attempt npm install
            proc = await asyncio.create_subprocess_exec(
                "npm", "install", cwd=project_dir,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=120)
            if proc.returncode != 0:
                logger.warning("npm install failed — skipping preview")
                return {"preview": None, "skipped": True, "reason": "npm install failed"}

            # Build static assets for preview server compatibility
            build_proc = await asyncio.create_subprocess_exec(
                "npm", "run", "build", cwd=project_dir,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(build_proc.communicate(), timeout=180)
            if build_proc.returncode != 0 or not os.path.isdir(dist_dir):
                logger.warning("npm run build failed — falling back to dev preview")
                dist_dir = None

            # Start a local server:
            # - Prefer `vite preview` (serves dist/)
            # - Fallback to `vite` dev server
            if dist_dir:
                server = await asyncio.create_subprocess_exec(
                    "npx", "vite", "preview", "--port", "4173", cwd=project_dir,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
            else:
                server = await asyncio.create_subprocess_exec(
                    "npx", "vite", "--port", "4173", cwd=project_dir,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
            await asyncio.sleep(5)  # wait for server to boot

            # Screenshot
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1440, "height": 900})
                await page.goto("http://localhost:4173", wait_until="networkidle")
                await page.screenshot(path=preview_path, full_page=True)
                await browser.close()

            # Terminate dev server
            server.terminate()
            await server.wait()

            logger.info("Preview screenshot saved → %s", preview_path)
            return {
                "preview": preview_path,
                "skipped": False,
                "dist_dir": dist_dir if dist_dir and os.path.isdir(dist_dir) else None,
            }

        except Exception as e:
            logger.warning("Preview generation failed: %s", e)
            return {"preview": None, "skipped": True, "reason": str(e)}
