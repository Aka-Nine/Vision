"""
UI AST Schema — Core Data Structures
═════════════════════════════════════
Defines the complete, production-grade UI AST schema.
This is the single source of truth for the Phase 2.5 → Phase 3 contract.

Golden Rules:
  ❌ LLM CANNOT: Change layout_tree, add/remove components, modify constraints
  ✅ LLM CAN ONLY: Fill content_slots, suggest minor styling (optional)
"""

from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field
from typing import Any, Optional


# ── Layout Tree Nodes ───────────────────────────────────────────────

@dataclass
class LayoutNode:
    """A node in the strict layout tree hierarchy."""
    id: str
    type: str                                 # "page", "section", "container", "group", "element"
    role: Optional[str] = None                # "navigation", "hero", "features", "cta", "footer", etc.
    layout: Optional[str] = None              # "horizontal", "vertical", "two_column", "grid", "stack"
    children: list = field(default_factory=list)  # list of LayoutNode or str (element IDs)
    props: dict = field(default_factory=dict)     # sticky, min_height, etc.

    def to_dict(self) -> dict:
        result = {"id": self.id, "type": self.type}
        if self.role:
            result["role"] = self.role
        if self.layout:
            result["layout"] = self.layout
        if self.props:
            result["props"] = self.props
        if self.children:
            result["children"] = [
                c.to_dict() if isinstance(c, LayoutNode) else c
                for c in self.children
            ]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> LayoutNode:
        children = []
        for c in data.get("children", []):
            if isinstance(c, dict):
                children.append(cls.from_dict(c))
            else:
                children.append(c)
        return cls(
            id=data["id"],
            type=data["type"],
            role=data.get("role"),
            layout=data.get("layout"),
            children=children,
            props=data.get("props", {}),
        )


# ── Design Tokens ───────────────────────────────────────────────────

@dataclass
class DesignTokens:
    """Global, unified design system — no mixing across themes."""
    theme: str = "dark"
    color_palette: dict = field(default_factory=lambda: {
        "primary": "#7C3AED",
        "secondary": "#06B6D4",
        "background": "#0F172A",
        "surface": "rgba(255,255,255,0.05)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#94A3B8",
        "accent_gradient_start": "#7C3AED",
        "accent_gradient_end": "#EC4899",
    })
    typography: dict = field(default_factory=lambda: {
        "font_family": "Inter",
        "heading_scale": ["56px", "42px", "32px", "24px"],
        "body_size": "16px",
        "font_weight_heading": "800",
        "font_weight_body": "400",
        "line_height": "1.6",
        "letter_spacing_heading": "-0.02em",
    })
    spacing: dict = field(default_factory=lambda: {
        "section_padding": "80px",
        "container_width": "1200px",
        "gap": "24px",
        "content_padding": "24px",
    })
    border_radius: str = "16px"
    shadow: str = "0 25px 50px -12px rgba(0,0,0,0.25)"
    animation: dict = field(default_factory=lambda: {
        "type": "fade-up",
        "duration": "0.6s",
        "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
        "stagger_delay": "0.1s",
    })

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "color_palette": self.color_palette,
            "typography": self.typography,
            "spacing": self.spacing,
            "border_radius": self.border_radius,
            "shadow": self.shadow,
            "animation": self.animation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DesignTokens:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ── Component Specifications ────────────────────────────────────────

@dataclass
class ComponentSpec:
    """Maps directly to React/HTML generation — real buildable units."""
    id: str
    tag: str                                  # "nav", "section", "div", "button", "footer"
    component_name: str                       # "Navbar", "HeroSection", etc.
    variant: Optional[str] = None             # "primary", "secondary", "ghost"
    size: Optional[str] = None                # "sm", "md", "lg", "xl"
    classes: str = ""                         # Tailwind classes
    props: dict = field(default_factory=dict) # sticky, min_height, grid_cols, etc.
    children: list = field(default_factory=list)  # child ComponentSpec definitions

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "tag": self.tag,
            "component_name": self.component_name,
        }
        if self.variant:
            result["variant"] = self.variant
        if self.size:
            result["size"] = self.size
        if self.classes:
            result["classes"] = self.classes
        if self.props:
            result["props"] = self.props
        if self.children:
            result["children"] = [
                c.to_dict() if isinstance(c, ComponentSpec) else c
                for c in self.children
            ]
        return result


# ── Content Slots (LLM ZONE ONLY) ──────────────────────────────────

@dataclass
class ContentSlot:
    """The ONLY part an LLM is allowed to touch."""
    slot_id: str                              # e.g. "hero.heading"
    type: str                                 # "text", "button_text", "list", "image_url"
    value: Optional[str] = None               # Filled content
    max_length: Optional[int] = None
    tone: Optional[str] = None                # "technical", "casual", "enterprise"
    target: Optional[str] = None              # "saas_founders", "developers", etc.
    style: Optional[str] = None               # "action", "informational"
    item_structure: Optional[dict] = None     # For list-type slots: {"title": "text", "description": "text"}
    count: Optional[int] = None               # For list-type slots

    def to_dict(self) -> dict:
        result = {"slot_id": self.slot_id, "type": self.type}
        if self.value is not None:
            result["value"] = self.value
        if self.max_length:
            result["max_length"] = self.max_length
        if self.tone:
            result["tone"] = self.tone
        if self.target:
            result["target"] = self.target
        if self.style:
            result["style"] = self.style
        if self.item_structure:
            result["item_structure"] = self.item_structure
        if self.count:
            result["count"] = self.count
        return result


# ── Spatial Rules (from bounding boxes) ─────────────────────────────

@dataclass
class SpatialRule:
    """Anti-generic weapon — reconstructed from actual screenshot layout data."""
    section_id: str
    height: Optional[str] = None              # "75vh", "auto"
    alignment: Optional[str] = None           # "center", "left", "right"
    padding_top: Optional[str] = None
    padding_bottom: Optional[str] = None
    width_ratio: Optional[float] = None       # 0.0 - 1.0
    z_index: Optional[int] = None
    position: Optional[str] = None            # "relative", "sticky", "fixed"

    def to_dict(self) -> dict:
        result = {"section_id": self.section_id}
        for k in ["height", "alignment", "padding_top", "padding_bottom",
                   "width_ratio", "z_index", "position"]:
            v = getattr(self, k)
            if v is not None:
                result[k] = v
        return result


# ── Constraints ─────────────────────────────────────────────────────

@dataclass
class Constraints:
    """Strict validation rules the generator MUST obey."""
    required_sections: list = field(default_factory=lambda: ["navbar", "hero", "footer"])
    order: list = field(default_factory=list)
    rules: list = field(default_factory=lambda: [
        "hero must contain heading and cta",
        "cta must be visible above fold",
        "no empty containers",
        "max 2 primary CTAs per section",
        "navbar must exist at top",
        "footer must exist at bottom",
    ])

    def to_dict(self) -> dict:
        return {
            "required_sections": self.required_sections,
            "order": self.order,
            "rules": self.rules,
        }


# ── Variation Engine Config ─────────────────────────────────────────

@dataclass
class VariationConfig:
    """Anti-repetition engine — controlled randomness."""
    variation_seed: int = 42
    layout_variant: str = "balanced"          # "left-heavy", "centered", "split", "offset"
    cta_style: str = "single"                 # "single", "dual", "inline"
    hero_alignment: str = "center"            # "center", "left", "offset"
    feature_style: str = "cards"              # "cards", "bento", "list", "alternating"
    pricing_style: str = "columns"            # "columns", "toggle", "comparison"
    testimonial_style: str = "grid"           # "grid", "carousel", "single"
    animation_intensity: str = "medium"       # "none", "subtle", "medium", "rich"
    color_mode: str = "gradient"              # "flat", "gradient", "glassmorphic"

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


# ── Compiler Flags ──────────────────────────────────────────────────

@dataclass 
class CompilerFlags:
    """Control compilation behavior."""
    strict_mode: bool = True
    allow_llm_layout_changes: bool = False
    regenerate_on_failure: bool = True
    enforce_spatial_rules: bool = True
    demand_driven_complexity: bool = True
    max_sections: int = 12
    min_sections: int = 3

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


# ── Provenance (Traceability) ───────────────────────────────────────

@dataclass
class Provenance:
    """Tracks lineage of design decisions back to data sources."""
    sources: list = field(default_factory=list)       # [{"type": "reddit", "id": "abc"}, ...]
    screenshots: list = field(default_factory=list)    # [{"path": "...", "bbox_used": True}, ...]
    dominant_pattern: Optional[str] = None
    discarded_patterns: list = field(default_factory=list)
    demand_score: float = 0.0
    trend_velocity: float = 0.0

    def to_dict(self) -> dict:
        return {
            "sources": self.sources,
            "screenshots": self.screenshots,
            "dominant_pattern": self.dominant_pattern,
            "discarded_patterns": self.discarded_patterns,
            "demand_score": self.demand_score,
            "trend_velocity": self.trend_velocity,
        }


# ── TOP-LEVEL AST ──────────────────────────────────────────────────

@dataclass
class UIAST:
    """
    The complete UI Abstract Syntax Tree.
    This is the ONLY output of Phase 2.5 and the ONLY input to Phase 3.
    """
    version: str = "1.0"
    meta: dict = field(default_factory=lambda: {
        "template_id": str(uuid.uuid4()),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "market_intelligence",
        "design_system": "dark_glassmorphism_saas",
        "variation_seed": 42,
    })

    layout_tree: Optional[LayoutNode] = None
    design_tokens: DesignTokens = field(default_factory=DesignTokens)
    components: dict = field(default_factory=dict)          # id -> ComponentSpec.to_dict()
    content_slots: dict = field(default_factory=dict)       # slot_id -> ContentSlot.to_dict()
    spatial_rules: dict = field(default_factory=dict)       # section_id -> SpatialRule.to_dict()
    constraints: Constraints = field(default_factory=Constraints)
    variation: VariationConfig = field(default_factory=VariationConfig)
    provenance: Provenance = field(default_factory=Provenance)
    compiler_flags: CompilerFlags = field(default_factory=CompilerFlags)

    def to_dict(self) -> dict:
        """Serialize entire AST to JSON-compatible dict."""
        return {
            "version": self.version,
            "meta": self.meta,
            "layout_tree": self.layout_tree.to_dict() if self.layout_tree else {},
            "design_tokens": self.design_tokens.to_dict(),
            "components": self.components,
            "content_slots": self.content_slots,
            "spatial_rules": self.spatial_rules,
            "constraints": self.constraints.to_dict(),
            "variation": self.variation.to_dict(),
            "provenance": self.provenance.to_dict(),
            "compiler_flags": self.compiler_flags.to_dict(),
        }

    def get_ordered_section_ids(self) -> list[str]:
        """Return section IDs in constraint-enforced order."""
        if self.constraints.order:
            return self.constraints.order
        # Fall back to layout tree traversal
        if self.layout_tree:
            return [
                c.id if isinstance(c, LayoutNode) else c
                for c in self.layout_tree.children
            ]
        return []

    def get_component(self, section_id: str) -> Optional[dict]:
        """Get component spec for a section."""
        return self.components.get(section_id)

    def get_content_for_section(self, section_id: str) -> dict:
        """Get all content slots for a section, organized by field."""
        result = {}
        prefix = f"{section_id}."
        for slot_id, slot_data in self.content_slots.items():
            if slot_id.startswith(prefix):
                field_name = slot_id[len(prefix):]
                result[field_name] = slot_data
        return result

    def get_spatial_rule(self, section_id: str) -> Optional[dict]:
        """Get spatial layout rule for a section."""
        return self.spatial_rules.get(section_id)
