"""
UI Grammar Engine — Fix #6
════════════════════════════
Defines strict rules about what UI elements can exist where,
what depends on what, and the valid ordering of sections.

Without this, the generator doesn't know:
  - What comes first
  - What is optional
  - What depends on what
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Grammar Rules Database ──────────────────────────────────────────

# Section ordering constraints (lower = earlier in page)
SECTION_ORDER_PRIORITY = {
    "navbar": 0,
    "header": 0,
    "nav": 0,
    "hero": 10,
    "features": 20,
    "stats": 25,
    "pricing": 30,
    "testimonials": 35,
    "faq": 40,
    "cta": 45,
    "contact": 50,
    "footer": 99,
}

# Required children per section type
REQUIRED_CHILDREN = {
    "hero": ["heading", "cta_group"],
    "navbar": ["logo", "nav_links"],
    "features": ["heading"],
    "pricing": ["heading"],
    "cta": ["heading", "cta_group"],
    "footer": [],
}

# Optional but recommended children
RECOMMENDED_CHILDREN = {
    "hero": ["subtext", "image_mockup", "badge"],
    "navbar": ["cta_button"],
    "features": ["subtext", "feature_items"],
    "pricing": ["subtext", "plan_cards"],
    "testimonials": ["heading", "testimonial_cards"],
    "cta": ["subtext"],
    "footer": ["link_columns", "copyright"],
}

# Section dependencies (A depends on B existing)
DEPENDENCIES = {
    # No section depends on another to exist, but some need context
}

# Mutual exclusions
EXCLUSIONS = {
    ("navbar", "header"),  # Can't have both
}

# Section containment rules
CONTAINMENT_RULES = {
    "cta_group": {"max_buttons": 2, "button_variants": ["primary", "secondary"]},
    "feature_items": {"min_count": 2, "max_count": 6},
    "plan_cards": {"min_count": 2, "max_count": 4},
    "testimonial_cards": {"min_count": 2, "max_count": 6},
    "nav_links": {"min_count": 3, "max_count": 7},
}


class UIGrammarEngine:
    """Enforces structural rules on the UI AST layout tree."""

    def validate_section_order(self, section_ids: list[str]) -> tuple[bool, list[str]]:
        """
        Validate that sections follow the grammar ordering rules.
        Returns (is_valid, list_of_violations).
        """
        violations = []

        for i, sid in enumerate(section_ids):
            priority = SECTION_ORDER_PRIORITY.get(sid, 50)

            # Check: navbar/header must be first
            if sid in ("navbar", "header", "nav") and i != 0:
                violations.append(f"'{sid}' must be the first section (found at position {i})")

            # Check: footer must be last
            if sid == "footer" and i != len(section_ids) - 1:
                violations.append(f"'footer' must be the last section (found at position {i})")

            # Check: hero should be right after navbar
            if sid == "hero":
                if i > 0 and section_ids[i - 1] not in ("navbar", "header", "nav"):
                    violations.append(
                        f"'hero' should follow navbar/header, but follows '{section_ids[i - 1]}'"
                    )

            # Check ordering relative to neighbors
            if i > 0:
                prev_priority = SECTION_ORDER_PRIORITY.get(section_ids[i - 1], 50)
                if priority < prev_priority and sid not in ("navbar", "header", "nav"):
                    violations.append(
                        f"'{sid}' (priority={priority}) appears after "
                        f"'{section_ids[i-1]}' (priority={prev_priority})"
                    )

        return len(violations) == 0, violations

    def enforce_order(self, section_ids: list[str]) -> list[str]:
        """
        Re-order sections to comply with grammar rules.
        Preserves relative order of same-priority sections.
        """
        return sorted(
            section_ids,
            key=lambda sid: SECTION_ORDER_PRIORITY.get(sid, 50),
        )

    def validate_children(self, section_type: str, children_ids: list[str]) -> tuple[bool, list[str]]:
        """Check if a section has all required children."""
        required = REQUIRED_CHILDREN.get(section_type, [])
        missing = [c for c in required if c not in children_ids]

        if missing:
            return False, [f"Section '{section_type}' missing required children: {missing}"]
        return True, []

    def get_recommended_children(self, section_type: str) -> list[str]:
        """Get recommended (but optional) children for a section type."""
        return RECOMMENDED_CHILDREN.get(section_type, [])

    def validate_exclusions(self, section_ids: list[str]) -> tuple[bool, list[str]]:
        """Check for mutually exclusive sections."""
        violations = []
        section_set = set(section_ids)

        for a, b in EXCLUSIONS:
            if a in section_set and b in section_set:
                violations.append(
                    f"Sections '{a}' and '{b}' are mutually exclusive — keep only one"
                )

        return len(violations) == 0, violations

    def validate_containment(self, element_type: str, count: int) -> tuple[bool, list[str]]:
        """Validate containment rules (e.g., max buttons per CTA group)."""
        rules = CONTAINMENT_RULES.get(element_type)
        if not rules:
            return True, []

        violations = []
        min_count = rules.get("min_count", 0)
        max_count = rules.get("max_count", float("inf"))

        if count < min_count:
            violations.append(f"'{element_type}' needs at least {min_count} items (got {count})")
        if count > max_count:
            violations.append(f"'{element_type}' allows at most {max_count} items (got {count})")

        return len(violations) == 0, violations

    def validate_full_structure(self, section_ids: list[str]) -> dict:
        """
        Run ALL grammar validations on a section list.
        Returns a comprehensive validation report.
        """
        report = {"valid": True, "violations": [], "warnings": []}

        # 1. Order validation
        ok, viols = self.validate_section_order(section_ids)
        if not ok:
            report["violations"].extend(viols)
            report["valid"] = False

        # 2. Exclusion validation
        ok, viols = self.validate_exclusions(section_ids)
        if not ok:
            report["violations"].extend(viols)
            report["valid"] = False

        # 3. Required sections check
        section_set = set(section_ids)
        if "hero" not in section_set:
            report["warnings"].append("No 'hero' section found — strongly recommended")
        if "footer" not in section_set:
            report["warnings"].append("No 'footer' section found — recommended for completeness")
        if not section_set.intersection({"navbar", "header", "nav"}):
            report["warnings"].append("No navigation section found — recommended")

        # 4. Size check
        if len(section_ids) < 3:
            report["warnings"].append(f"Only {len(section_ids)} sections — may appear too minimal")
        if len(section_ids) > 12:
            report["warnings"].append(f"{len(section_ids)} sections — page may be too long")

        return report

    def auto_fix_structure(self, section_ids: list[str]) -> list[str]:
        """
        Automatically fix structural issues:
        - Add missing required sections
        - Remove exclusions (keep the first one)
        - Enforce ordering
        """
        fixed = list(section_ids)

        # Add navbar if missing
        if not any(s in fixed for s in ("navbar", "header", "nav")):
            fixed.insert(0, "navbar")

        # Add hero if missing
        if "hero" not in fixed:
            nav_idx = next(
                (i for i, s in enumerate(fixed) if s in ("navbar", "header", "nav")),
                -1,
            )
            fixed.insert(nav_idx + 1, "hero")

        # Add footer if missing
        if "footer" not in fixed:
            fixed.append("footer")

        # Handle exclusions
        for a, b in EXCLUSIONS:
            if a in fixed and b in fixed:
                fixed.remove(b)
                logger.info("Auto-fix: removed '%s' (exclusive with '%s')", b, a)

        # Enforce ordering
        fixed = self.enforce_order(fixed)

        return fixed
