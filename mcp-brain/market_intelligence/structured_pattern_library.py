"""
Structured Pattern Library — Fix #1 (Enforceable Schema)
═════════════════════════════════════════════════════════
Converts extracted patterns from descriptive strings to
enforceable schema structures.

BEFORE (descriptive, useless for generation):
  "hero": "glassmorphism style with CTA"

AFTER (enforceable, deterministic):
  "hero": {
    "layout": "two_column",
    "left": ["heading", "subtext", "cta_group"],
    "right": ["image_mockup"],
    "cta_group": {"type": "button_row", "buttons": 2},
    "spacing": {"padding_y": "80px", "gap": "32px"}
  }
"""

import os
import json
import logging
import re

logger = logging.getLogger(__name__)


# ── Section Schema Templates ───────────────────────────────────────
# These enforce STRUCTURE, not just describe appearance

SECTION_SCHEMAS = {
    "hero": {
        "layout": "two_column",
        "children": {
            "left": ["badge", "heading", "subtext", "cta_group"],
            "right": ["image_mockup"],
        },
        "cta_group": {"type": "button_row", "max_buttons": 2},
        "spacing": {"padding_y": "80px", "gap": "32px"},
        "constraints": {
            "heading_required": True,
            "cta_required": True,
            "min_height": "80vh",
        },
    },
    "features": {
        "layout": "grid",
        "children": {
            "header": ["heading", "subtext"],
            "grid": ["feature_card"],
        },
        "feature_card": {
            "structure": ["icon", "title", "description"],
            "min_count": 3,
            "max_count": 6,
        },
        "spacing": {"padding_y": "80px", "gap": "24px"},
        "constraints": {"heading_required": True},
    },
    "pricing": {
        "layout": "grid",
        "children": {
            "header": ["heading", "subtext", "toggle"],
            "grid": ["plan_card"],
        },
        "plan_card": {
            "structure": ["name", "price", "period", "features_list", "cta"],
            "min_count": 2,
            "max_count": 4,
            "highlight_one": True,
        },
        "spacing": {"padding_y": "80px", "gap": "24px"},
        "constraints": {"heading_required": True},
    },
    "testimonials": {
        "layout": "grid",
        "children": {
            "header": ["heading"],
            "grid": ["testimonial_card"],
        },
        "testimonial_card": {
            "structure": ["quote", "avatar", "name", "role"],
            "min_count": 2,
            "max_count": 6,
        },
        "spacing": {"padding_y": "80px", "gap": "24px"},
    },
    "cta": {
        "layout": "centered",
        "children": {
            "content": ["heading", "subtext", "cta_group"],
        },
        "cta_group": {"type": "button_row", "max_buttons": 2},
        "spacing": {"padding_y": "100px", "gap": "24px"},
        "constraints": {"heading_required": True, "cta_required": True},
    },
    "navbar": {
        "layout": "horizontal",
        "children": {
            "left": ["logo"],
            "center": ["nav_links"],
            "right": ["cta_button"],
        },
        "spacing": {"padding_y": "16px"},
        "constraints": {"sticky": True, "z_index": 50},
    },
    "footer": {
        "layout": "grid",
        "children": {
            "columns": ["link_group"],
            "bottom": ["copyright", "social_links"],
        },
        "link_group": {"min_count": 3, "max_count": 5},
        "spacing": {"padding_y": "60px", "gap": "32px"},
    },
    "faq": {
        "layout": "single_column",
        "children": {
            "header": ["heading", "subtext"],
            "list": ["faq_item"],
        },
        "faq_item": {
            "structure": ["question", "answer"],
            "min_count": 4,
            "max_count": 10,
            "type": "accordion",
        },
        "spacing": {"padding_y": "80px", "gap": "16px"},
    },
    "stats": {
        "layout": "grid",
        "children": {
            "grid": ["stat_item"],
        },
        "stat_item": {
            "structure": ["number", "label"],
            "count": 4,
        },
        "spacing": {"padding_y": "60px", "gap": "24px"},
    },
}


class StructuredPatternLibrary:
    """
    Stores and retrieves UI patterns as enforceable schemas,
    not descriptive strings.
    """

    def __init__(self, patterns_dir: str = "patterns"):
        self.patterns_dir = patterns_dir
        os.makedirs(self.patterns_dir, exist_ok=True)

    def save_pattern(self, category: str, pattern_data: dict):
        """Save a raw extracted pattern, converting to schema if possible."""
        # Auto-enrich with schema constraints
        enriched = self._enrich_pattern(pattern_data)

        file_path = os.path.join(self.patterns_dir, f"{category}_patterns.json")

        patterns = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    patterns = json.load(f)
                except Exception:
                    patterns = []

        patterns.append(enriched)

        with open(file_path, "w") as f:
            json.dump(patterns, f, indent=4)

    def get_patterns(self, category: str) -> list:
        """Get all patterns for a category."""
        file_path = os.path.join(self.patterns_dir, f"{category}_patterns.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []

    def get_section_schema(self, section_type: str) -> dict:
        """
        Get the enforceable schema for a section type.
        This is what Phase 3 MUST follow — not descriptions.
        """
        return SECTION_SCHEMAS.get(section_type, {
            "layout": "single_column",
            "children": {"content": ["heading", "body"]},
            "spacing": {"padding_y": "60px", "gap": "24px"},
        })

    def get_all_schemas(self) -> dict:
        """Get all section schemas."""
        return SECTION_SCHEMAS.copy()

    def convert_pattern_to_schema(self, pattern: dict) -> dict:
        """
        Convert a raw descriptive pattern to an enforceable schema.

        Input:  {"layout_type": "SaaS Landing", "structure": ["Hero Section", "Features"]}
        Output: Structured schema with children, spacing, constraints
        """
        structure = pattern.get("structure", [])
        result = {
            "layout_type": pattern.get("layout_type", "landing_page"),
            "sections": [],
        }

        for section_name in structure:
            # Normalize section name
            normalized = self._normalize_section_name(section_name)
            schema = self.get_section_schema(normalized)

            result["sections"].append({
                "id": normalized,
                "original_name": section_name,
                "schema": schema,
            })

        return result

    def _enrich_pattern(self, pattern_data: dict) -> dict:
        """Enrich a raw pattern with schema constraints."""
        enriched = pattern_data.copy()

        # Add schema references for known sections
        structure = enriched.get("structure", [])
        enriched["_schemas"] = {}
        for s in structure:
            normalized = self._normalize_section_name(s)
            if normalized in SECTION_SCHEMAS:
                enriched["_schemas"][normalized] = SECTION_SCHEMAS[normalized]

        enriched["_enriched"] = True
        return enriched

    def _normalize_section_name(self, name: str) -> str:
        """Normalize a messy section name to a canonical ID."""
        # Remove parenthetical descriptions
        name = re.sub(r"\([^)]*\)", "", name).strip()
        # Convert to lowercase slug
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

        # Map common aliases
        aliases = {
            "hero_section": "hero",
            "header": "navbar",
            "header_navigation": "navbar",
            "top_navigation": "navbar",
            "top_navigation_bar": "navbar",
            "navigation": "navbar",
            "nav": "navbar",
            "global_header": "navbar",
            "feature_grid": "features",
            "features_overview": "features",
            "pricing_card": "pricing",
            "solutions_pricing": "pricing",
            "testimonial_card": "testimonials",
            "cta_button": "cta",
            "call_to_action": "cta",
            "download_call_to_action": "cta",
            "final_download_call_to_action": "cta",
            "footer_navigation": "footer",
            "global_footer": "footer",
            "bottom_navigation_bar": "footer",
            "faq_section": "faq",
            "contact_section": "contact",
        }

        return aliases.get(slug, slug)


pattern_library = StructuredPatternLibrary()
