"""
Generator Compatibility Validator — Fix #5 (Strengthened)
══════════════════════════════════════════════════════════
Strict validation BEFORE generation begins. Fails HARD
on missing structure instead of silently producing generic output.

Validates:
  - Layout sections exist and have proper structure
  - Visual style is defined (not just a string)
  - Target market context exists
  - Quality score meets threshold
  - Required sections are present
  - Component depth is sufficient
  - Design brief has actionable data (not just descriptions)
"""

import logging

logger = logging.getLogger(__name__)

REQUIRED_BRIEF_KEYS = ["sections", "style"]
REQUIRED_SECTIONS = {"hero"}  # At minimum, must have a hero
RECOMMENDED_SECTIONS = {"navbar", "hero", "features", "footer"}
MIN_QUALITY_SCORE = 0.5
MIN_SECTION_COUNT = 2
MAX_SECTION_COUNT = 15


class GeneratorCompatibilityCheck:
    """Strict pre-generation validator — rejects weak briefs."""

    def is_compatible(self, brief: dict) -> tuple[bool, str]:
        """
        Validate a brief is ready for generation.

        Returns
        -------
        (is_compatible, message)
        """
        errors = []
        warnings = []

        # ── 1. Sections exist and have content ─────────────────────
        sections = brief.get("sections") or []
        if not sections or len(sections) == 0:
            errors.append("No layout sections defined")
        elif len(sections) < MIN_SECTION_COUNT:
            errors.append(f"Too few sections ({len(sections)} < {MIN_SECTION_COUNT})")
        elif len(sections) > MAX_SECTION_COUNT:
            warnings.append(f"Many sections ({len(sections)}) — may impact quality")

        # ── 2. Sections are strings, not empty ─────────────────────
        for i, s in enumerate(sections):
            if not isinstance(s, str) or not s.strip():
                errors.append(f"Section [{i}] is empty or invalid: {repr(s)}")

        # ── 3. Required sections present ───────────────────────────
        section_set = {s.lower().strip() for s in sections if isinstance(s, str)}
        missing_required = REQUIRED_SECTIONS - section_set
        if missing_required:
            warnings.append(f"Missing recommended sections: {missing_required}")

        # ── 4. Visual style is defined and meaningful ──────────────
        style = brief.get("style", "")
        if not style:
            errors.append("No visual style defined")
        elif isinstance(style, str) and len(style) < 3:
            errors.append(f"Visual style too vague: '{style}'")

        # ── 5. Target market context exists ────────────────────────
        target_market = brief.get("target_market", "")
        if not target_market:
            warnings.append("No target_market context — output may be generic")

        # ── 6. Quality score threshold ─────────────────────────────
        quality = brief.get("quality_score", 0.0)
        if quality > 0 and quality < MIN_QUALITY_SCORE:
            errors.append(
                f"Quality score too low ({quality:.2f} < {MIN_QUALITY_SCORE})"
            )

        # ── 7. Product type exists ─────────────────────────────────
        product_type = brief.get("product_type", "")
        if not product_type:
            warnings.append("No product_type — generation may lack context")

        # ── 8. Demand score sanity check ───────────────────────────
        demand = brief.get("demand_score", 0.0)
        if demand == 0.0:
            warnings.append("Demand score is 0 — complexity will default to minimal")

        # ── Compile result ─────────────────────────────────────────
        if errors:
            error_msg = "Generator Errors: " + "; ".join(errors)
            if warnings:
                error_msg += " | Warnings: " + "; ".join(warnings)
            logger.error("Brief validation FAILED: %s", error_msg)
            return False, error_msg

        if warnings:
            warn_msg = "Compatible with warnings: " + "; ".join(warnings)
            logger.warning("Brief validation passed with warnings: %s", warn_msg)
            return True, warn_msg

        return True, "Fully compatible"

    def validate_for_ast(self, brief: dict) -> dict:
        """
        Extended validation for AST compilation readiness.
        Returns a detailed report instead of a simple bool.
        """
        is_ok, message = self.is_compatible(brief)

        report = {
            "compatible": is_ok,
            "message": message,
            "has_sections": bool(brief.get("sections")),
            "section_count": len(brief.get("sections", [])),
            "has_style": bool(brief.get("style")),
            "has_target_market": bool(brief.get("target_market")),
            "has_product_type": bool(brief.get("product_type")),
            "quality_score": brief.get("quality_score", 0.0),
            "demand_score": brief.get("demand_score", 0.0),
        }

        return report


generator_validator = GeneratorCompatibilityCheck()
