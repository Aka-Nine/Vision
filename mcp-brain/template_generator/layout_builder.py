"""
Layout Builder — Phase 3 Module (AST-Powered)
Creates the page layout structure using spatial rules from the UI AST
instead of hardcoded defaults, producing layouts that match real
screenshot compositions rather than generic templates.
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

# ── Section rendering metadata ──────────────────────────────────────
SECTION_DEFAULTS = {
    "hero": {
        "component": "HeroSection",
        "grid": "full-width",
        "padding": "py-32",
        "order": 0,
    },
    "navbar": {
        "component": "Navbar",
        "grid": "full-width",
        "padding": "py-4",
        "order": -1,
        "sticky": True,
    },
    "features": {
        "component": "FeaturesSection",
        "grid": "3-col",
        "padding": "py-24",
        "order": 1,
    },
    "pricing": {
        "component": "PricingSection",
        "grid": "3-col",
        "padding": "py-24",
        "order": 2,
    },
    "testimonials": {
        "component": "TestimonialsSection",
        "grid": "2-col",
        "padding": "py-24",
        "order": 3,
    },
    "cta": {
        "component": "CTASection",
        "grid": "full-width",
        "padding": "py-20",
        "order": 4,
    },
    "footer": {
        "component": "Footer",
        "grid": "4-col",
        "padding": "py-12",
        "order": 99,
    },
    "header": {
        "component": "Header",
        "grid": "full-width",
        "padding": "py-4",
        "order": -1,
        "sticky": True,
    },
    "dashboard": {
        "component": "DashboardSection",
        "grid": "2-col",
        "padding": "py-8",
        "order": 1,
    },
    "sidebar": {
        "component": "Sidebar",
        "grid": "sidebar",
        "padding": "py-0",
        "order": 0,
    },
    "stats": {
        "component": "StatsSection",
        "grid": "4-col",
        "padding": "py-16",
        "order": 2,
    },
    "charts": {
        "component": "ChartsSection",
        "grid": "2-col",
        "padding": "py-16",
        "order": 3,
    },
    "faq": {
        "component": "FAQSection",
        "grid": "full-width",
        "padding": "py-24",
        "order": 5,
    },
    "contact": {
        "component": "ContactSection",
        "grid": "full-width",
        "padding": "py-24",
        "order": 6,
    },
}

# ── Responsive breakpoints ──────────────────────────────────────────
BREAKPOINTS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}


class LayoutBuilder:
    """Build a page layout structure from a parsed template spec, enhanced with AST spatial rules."""

    async def build(self, spec: dict, output_dir: str) -> dict:
        """
        Parameters
        ----------
        spec : dict       — output of BriefParser.parse(), enriched with AST data
        output_dir : str  — path where layout.json will be written

        Returns
        -------
        dict — the full layout descriptor
        """
        logger.info("Building layout for %s …", spec.get("layout", "landing_page"))

        sections = spec.get("sections", [])
        layout_type = spec.get("layout", "landing_page")

        # ── AST-powered spatial rules (Fix #2) ─────────────────────
        spatial_rules = spec.get("_spatial_rules", {})
        component_specs = spec.get("_component_specs", {})
        variation = spec.get("_variation", {})
        constraints = spec.get("_constraints", {})

        ordered_sections = self._order_sections(sections, constraints)
        page_components = [entry["component"] for entry in ordered_sections]
        section_configs = self._build_section_configs(
            ordered_sections, spec, spatial_rules, component_specs, variation
        )

        layout = {
            "layout_type": layout_type,
            "page": page_components,
            "sections": section_configs,
            "responsive": {
                "breakpoints": BREAKPOINTS,
                "mobile_first": True,
                "container_max_width": "1280px",
            },
            "meta": {
                "template_type": spec.get("template_type", ""),
                "section_count": len(page_components),
                "ast_powered": bool(spatial_rules),
                "variation": variation.get("layout_variant", "balanced"),
            },
        }

        # Persist layout.json
        os.makedirs(output_dir, exist_ok=True)
        layout_path = os.path.join(output_dir, "layout.json")
        with open(layout_path, "w") as f:
            json.dump(layout, f, indent=2)

        logger.info("Layout written → %s  (%d sections, ast_powered=%s)",
                     layout_path, len(page_components), bool(spatial_rules))
        return layout

    # ── Internal helpers ────────────────────────────────────────────
    def _order_sections(self, sections: list, constraints: dict) -> list:
        """
        Sort sections by constraint-enforced order if available,
        falling back to predefined priorities.
        """
        # If AST provides an explicit order, use it (Fix #6 — grammar enforced)
        enforced_order = constraints.get("order", [])
        if enforced_order:
            entries = []
            for idx, section_key in enumerate(enforced_order):
                if section_key in [s for s in sections] or section_key in enforced_order:
                    defaults = SECTION_DEFAULTS.get(section_key, {
                        "component": self._to_component_name(section_key),
                        "grid": "full-width",
                        "padding": "py-16",
                        "order": idx,
                    })
                    entries.append({**defaults, "key": section_key, "order": idx})
            return entries

        # Legacy: sort by predefined order
        entries = []
        for idx, section_key in enumerate(sections):
            defaults = SECTION_DEFAULTS.get(section_key, {
                "component": self._to_component_name(section_key),
                "grid": "full-width",
                "padding": "py-16",
                "order": 50 + idx,
            })
            entries.append({**defaults, "key": section_key})
        entries.sort(key=lambda e: e.get("order", 99))
        return entries

    def _build_section_configs(
        self, ordered_sections: list, spec: dict,
        spatial_rules: dict, component_specs: dict, variation: dict,
    ) -> list:
        """Build per-section configuration including spatial overrides from AST."""
        style = spec.get("style", {})
        configs = []

        for entry in ordered_sections:
            section_key = entry["key"]

            # ── Base config ──
            config = {
                "key": section_key,
                "component": entry["component"],
                "grid": entry["grid"],
                "padding": entry["padding"],
                "sticky": entry.get("sticky", False),
                "style_overrides": {
                    "theme": style.get("theme", "dark"),
                    "glass": style.get("glass", False),
                },
            }

            # ── Apply AST spatial rules (Fix #2) ──
            spatial = spatial_rules.get(section_key, {})
            if spatial:
                if spatial.get("height"):
                    config["height"] = spatial["height"]
                if spatial.get("alignment"):
                    config["alignment"] = spatial["alignment"]
                if spatial.get("padding_top"):
                    config["padding_top"] = spatial["padding_top"]
                if spatial.get("padding_bottom"):
                    config["padding_bottom"] = spatial["padding_bottom"]
                if spatial.get("width_ratio"):
                    config["width_ratio"] = spatial["width_ratio"]
                if spatial.get("z_index"):
                    config["z_index"] = spatial["z_index"]
                if spatial.get("position"):
                    config["position"] = spatial["position"]
                config["_spatial_source"] = "ui_ast"

            # ── Apply AST component specs (Fix #8) ──
            comp_spec = component_specs.get(section_key, {})
            if comp_spec:
                config["component_spec"] = comp_spec
                # Override grid from component spec
                if comp_spec.get("props", {}).get("grid_cols"):
                    cols = comp_spec["props"]["grid_cols"]
                    config["grid"] = f"{cols}-col"
                if comp_spec.get("props", {}).get("layout"):
                    config["layout_mode"] = comp_spec["props"]["layout"]

            # ── Apply variation overrides (Fix #7) ──
            if variation:
                if section_key == "features":
                    config["feature_style"] = variation.get("feature_style", "cards")
                elif section_key == "pricing":
                    config["pricing_style"] = variation.get("pricing_style", "columns")
                elif section_key == "testimonials":
                    config["testimonial_style"] = variation.get("testimonial_style", "grid")
                elif section_key == "hero":
                    config["hero_alignment"] = variation.get("hero_alignment", "center")
                    config["cta_style"] = variation.get("cta_style", "dual")

            configs.append(config)

        return configs

    @staticmethod
    def _to_component_name(slug: str) -> str:
        """Convert a slug like 'quick_action_buttons_grid' → 'QuickActionButtonsGridSection'."""
        return "".join(word.capitalize() for word in slug.split("_")) + "Section"
