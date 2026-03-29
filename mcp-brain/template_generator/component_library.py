"""
Component Reuse Library — Phase 3.5 Module
═══════════════════════════════════════════
Stores generated components by type for future template reuse.
Every time a template is generated, its components are cataloged
here. Future generations can pull from the library instead of
recreating from scratch — improving quality and consistency.

Structure:
    component_library/
        hero_sections/
        pricing_tables/
        features_sections/
        testimonials_sections/
        cta_sections/
        navbars/
        footers/
        generic/
        library_index.json
"""

import os
import json
import time
import shutil
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_DIR = os.path.join(os.path.dirname(BASE_DIR), "component_library")
INDEX_PATH = os.path.join(LIBRARY_DIR, "library_index.json")

# Section type → library subfolder mapping
SECTION_CATEGORIES = {
    "hero": "hero_sections",
    "features": "features_sections",
    "pricing": "pricing_tables",
    "testimonials": "testimonials_sections",
    "cta": "cta_sections",
    "navbar": "navbars",
    "nav": "navbars",
    "footer": "footers",
}


class ComponentLibrary:
    """
    Centralized reusable component library.
    Catalogs every generated component by type for cross-template reuse.
    """

    def __init__(self):
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create library directory structure."""
        os.makedirs(LIBRARY_DIR, exist_ok=True)
        for folder in set(SECTION_CATEGORIES.values()):
            os.makedirs(os.path.join(LIBRARY_DIR, folder), exist_ok=True)
        os.makedirs(os.path.join(LIBRARY_DIR, "generic"), exist_ok=True)

    def _load_index(self) -> list:
        if os.path.isfile(INDEX_PATH):
            try:
                with open(INDEX_PATH) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_index(self, index: list):
        with open(INDEX_PATH, "w") as f:
            json.dump(index, f, indent=2)

    def catalog_components(self, template_name: str, components: list, source_dir: str) -> dict:
        """
        After a template is generated, catalog all its components into the library.

        Parameters
        ----------
        template_name : str   — name of the source template
        components    : list  — component metadata from ComponentGenerator
        source_dir    : str   — project directory containing src/components/

        Returns
        -------
        dict with cataloged_count and details
        """
        index = self._load_index()
        cataloged = []

        for comp in components:
            section_key = comp.get("section", "generic")
            component_name = comp.get("component", "Unknown")
            relative_path = comp.get("path", "")

            # Determine category folder
            category = SECTION_CATEGORIES.get(section_key, "generic")
            dest_folder = os.path.join(LIBRARY_DIR, category)

            # Source file
            src_file = os.path.join(source_dir, relative_path)
            if not os.path.isfile(src_file):
                logger.warning("Component file not found: %s", src_file)
                continue

            # Copy to library with template prefix
            dest_filename = f"{template_name}__{component_name}.jsx"
            dest_path = os.path.join(dest_folder, dest_filename)
            shutil.copy2(src_file, dest_path)

            # Add to index
            entry = {
                "component_name": component_name,
                "section_type": section_key,
                "category": category,
                "source_template": template_name,
                "library_path": f"{category}/{dest_filename}",
                "cataloged_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            index.append(entry)
            cataloged.append(entry)
            logger.info("Cataloged %s → %s", component_name, dest_path)

        self._save_index(index)

        return {
            "cataloged_count": len(cataloged),
            "components": cataloged,
        }

    def get_components_by_type(self, section_type: str) -> list:
        """
        Retrieve all cataloged components of a given type.
        Useful for future template generation to reuse existing components.
        """
        category = SECTION_CATEGORIES.get(section_type, "generic")
        index = self._load_index()
        return [e for e in index if e.get("category") == category]

    def get_best_component(self, section_type: str) -> str | None:
        """
        Get the file path of the most recently cataloged component
        of the given type. Future: rank by quality score.
        """
        matching = self.get_components_by_type(section_type)
        if not matching:
            return None
        # Latest = last in list (newest)
        best = matching[-1]
        full_path = os.path.join(LIBRARY_DIR, best["library_path"])
        if os.path.isfile(full_path):
            return full_path
        return None

    def get_library_stats(self) -> dict:
        """Return statistics about the component library."""
        index = self._load_index()
        stats = {
            "total_components": len(index),
            "categories": {},
            "templates_contributing": len(set(e.get("source_template", "") for e in index)),
        }
        for entry in index:
            cat = entry.get("category", "generic")
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        return stats

    def list_all(self) -> list:
        """Return the full library index."""
        return self._load_index()


# Singleton
component_library = ComponentLibrary()
