"""
Asset Manager — Phase 3 Module
Downloads or generates placeholder assets (icons, images, fonts)
for the generated template project.
"""
import os, logging, json

logger = logging.getLogger(__name__)

# Heroicon SVGs (inline) for common UI actions
HEROICONS = {
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>',
    "star": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/></svg>',
    "bolt": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z"/></svg>',
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"/></svg>',
}

PLACEHOLDER_IMAGES = {
    "hero-bg.jpg": "https://placehold.co/1920x1080/1e1b4b/7c3aed?text=Hero+Background",
    "feature-1.jpg": "https://placehold.co/600x400/1e1b4b/7c3aed?text=Feature+1",
    "feature-2.jpg": "https://placehold.co/600x400/1e1b4b/7c3aed?text=Feature+2",
    "feature-3.jpg": "https://placehold.co/600x400/1e1b4b/7c3aed?text=Feature+3",
    "avatar-1.jpg": "https://placehold.co/100x100/1e1b4b/7c3aed?text=SC",
    "avatar-2.jpg": "https://placehold.co/100x100/1e1b4b/7c3aed?text=MR",
}


class AssetManager:
    """Manage icon and image assets for a generated template."""

    async def generate(self, spec: dict, project_dir: str) -> dict:
        assets_dir = os.path.join(project_dir, "src", "assets")
        icons_dir = os.path.join(assets_dir, "icons")
        images_dir = os.path.join(assets_dir, "images")
        os.makedirs(icons_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)

        # Write inline SVG icons
        icon_files = []
        for name, svg in HEROICONS.items():
            path = os.path.join(icons_dir, f"{name}.svg")
            with open(path, "w") as f:
                f.write(svg)
            icon_files.append(f"src/assets/icons/{name}.svg")

        # Write a manifest of placeholder image URLs
        manifest_path = os.path.join(images_dir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(PLACEHOLDER_IMAGES, f, indent=2)
        logger.info("Asset manifest → %s  (%d icons, %d images)", manifest_path, len(icon_files), len(PLACEHOLDER_IMAGES))

        return {
            "icons": icon_files,
            "image_manifest": manifest_path,
            "placeholder_count": len(PLACEHOLDER_IMAGES),
        }
