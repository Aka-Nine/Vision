"""
Spatial Engine — Fix #2
════════════════════════
Converts bounding box data from screenshots into enforceable
spatial layout rules. This is the system's BIGGEST hidden advantage.

Input:  bounding_box [x, y, w, h] from deep analysis
Output: SpatialRule (height, alignment, padding, width_ratio, z_index)
"""

import logging
from typing import Optional
from ui_ast.schema import SpatialRule

logger = logging.getLogger(__name__)

# Viewport defaults (assumed design canvas)
DEFAULT_VIEWPORT_WIDTH = 1440
DEFAULT_VIEWPORT_HEIGHT = 900


class SpatialEngine:
    """Reconstructs layout rules from actual screenshot spatial data."""

    def __init__(self, viewport_width: int = DEFAULT_VIEWPORT_WIDTH,
                 viewport_height: int = DEFAULT_VIEWPORT_HEIGHT):
        self.vw = viewport_width
        self.vh = viewport_height

    def extract_spatial_rules(self, sections: list[dict]) -> dict[str, SpatialRule]:
        """
        Process all sections and return spatial rules keyed by section_id.

        Parameters
        ----------
        sections : list[dict]
            Sections from semantic brief, each may have:
            - _bounding_box: [x, y, w, h]
            - _scroll_y: float
            - type: str (section identifier)
        """
        rules = {}

        for section in sections:
            section_id = section.get("type", "unknown")
            bbox = section.get("_bounding_box")
            scroll_y = section.get("_scroll_y", 0)

            if bbox and len(bbox) == 4:
                rule = self._bbox_to_rule(section_id, bbox, scroll_y)
            else:
                rule = self._infer_defaults(section_id)

            rules[section_id] = rule
            logger.debug(
                "Spatial rule for '%s': height=%s, alignment=%s, width_ratio=%s",
                section_id, rule.height, rule.alignment, rule.width_ratio,
            )

        return rules

    def _bbox_to_rule(self, section_id: str, bbox: list, scroll_y: float) -> SpatialRule:
        """Convert a bounding box [x, y, w, h] to a SpatialRule."""
        def parse_val(v):
            if v is None: return 0.0
            if isinstance(v, str):
                s = ''.join(c for c in v if c.isdigit() or c == '.')
                return float(s) if s else 0.0
            return float(v)
            
        x, y, w, h = map(parse_val, bbox)
        scroll_y = parse_val(scroll_y)

        # ── Height calculation ──
        height_ratio = h / self.vh
        if height_ratio >= 0.85:
            height = "100vh"
        elif height_ratio >= 0.65:
            height = "80vh"
        elif height_ratio >= 0.45:
            height = "60vh"
        elif height_ratio >= 0.3:
            height = "40vh"
        else:
            height = "auto"

        # ── Alignment from x position ──
        center_x = x + w / 2
        vw_center = self.vw / 2
        offset_ratio = abs(center_x - vw_center) / vw_center

        if offset_ratio < 0.1:
            alignment = "center"
        elif center_x < vw_center:
            alignment = "left"
        else:
            alignment = "right"

        # ── Width ratio ──
        width_ratio = round(min(w / self.vw, 1.0), 3)

        # ── Padding from top of viewport ──
        if scroll_y == 0 and y < 20:
            padding_top = "0px"
            position = "sticky" if section_id in ("navbar", "header", "nav") else "relative"
        elif y / self.vh < 0.1:
            padding_top = f"{int(y)}px"
            position = "relative"
        else:
            # Section is further down — convert y to padding
            padding_top = f"{max(40, int((y % self.vh) * 0.8))}px"
            position = "relative"

        # ── Z-index heuristic ──
        z_index = self._compute_z_index(section_id, scroll_y, y)

        return SpatialRule(
            section_id=section_id,
            height=height,
            alignment=alignment,
            padding_top=padding_top,
            padding_bottom=self._compute_padding_bottom(h),
            width_ratio=width_ratio,
            z_index=z_index,
            position=position,
        )

    def _infer_defaults(self, section_id: str) -> SpatialRule:
        """Provide sensible default spatial rules when no bbox is available."""
        defaults = {
            "navbar": SpatialRule(
                section_id="navbar", height="auto", alignment="center",
                padding_top="0px", padding_bottom="0px", width_ratio=1.0,
                z_index=50, position="sticky",
            ),
            "hero": SpatialRule(
                section_id="hero", height="80vh", alignment="center",
                padding_top="100px", padding_bottom="80px", width_ratio=1.0,
                z_index=10, position="relative",
            ),
            "features": SpatialRule(
                section_id="features", height="auto", alignment="center",
                padding_top="80px", padding_bottom="80px", width_ratio=1.0,
                z_index=5, position="relative",
            ),
            "pricing": SpatialRule(
                section_id="pricing", height="auto", alignment="center",
                padding_top="80px", padding_bottom="80px", width_ratio=1.0,
                z_index=5, position="relative",
            ),
            "testimonials": SpatialRule(
                section_id="testimonials", height="auto", alignment="center",
                padding_top="80px", padding_bottom="80px", width_ratio=1.0,
                z_index=5, position="relative",
            ),
            "cta": SpatialRule(
                section_id="cta", height="auto", alignment="center",
                padding_top="60px", padding_bottom="60px", width_ratio=1.0,
                z_index=5, position="relative",
            ),
            "footer": SpatialRule(
                section_id="footer", height="auto", alignment="center",
                padding_top="40px", padding_bottom="40px", width_ratio=1.0,
                z_index=5, position="relative",
            ),
        }

        if section_id in defaults:
            return defaults[section_id]

        return SpatialRule(
            section_id=section_id, height="auto", alignment="center",
            padding_top="60px", padding_bottom="60px", width_ratio=1.0,
            z_index=5, position="relative",
        )

    def _compute_z_index(self, section_id: str, scroll_y: float, y: float) -> int:
        """Compute z-index based on section role and position."""
        if section_id in ("navbar", "header", "nav"):
            return 50  # Always on top
        if scroll_y == 0 and y < 100:
            return 20  # Above fold
        return 5       # Normal flow

    def _compute_padding_bottom(self, height: float) -> str:
        """Compute bottom padding from section height."""
        if height > self.vh * 0.6:
            return "80px"
        if height > self.vh * 0.3:
            return "60px"
        return "40px"

    def detect_layout_pattern(self, sections: list[dict]) -> str:
        """
        Analyze spatial arrangement to detect overall layout pattern.
        Returns: "single_column", "two_column", "sidebar_main", "grid"
        """
        if not sections:
            return "single_column"

        # Check if any section has a width_ratio < 0.5 (indicates multi-column)
        narrow_sections = []
        for section in sections:
            bbox = section.get("_bounding_box")
            if bbox and len(bbox) == 4:
                width_ratio = bbox[2] / self.vw
                if width_ratio < 0.5:
                    narrow_sections.append(section)

        if len(narrow_sections) >= 2:
            # Check if one is a sidebar (very narrow)
            for s in narrow_sections:
                w_ratio = s["_bounding_box"][2] / self.vw
                if w_ratio < 0.25:
                    return "sidebar_main"
            return "two_column"

        return "single_column"
