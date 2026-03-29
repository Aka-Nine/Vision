"""
UI AST Validator — Fix #5
══════════════════════════
Strict validation BEFORE generation. If the AST is invalid,
Phase 3 MUST reject it — no silent fallbacks to generic output.

Validates:
  1. Layout tree exists and has proper hierarchy
  2. All children are mapped to components
  3. Component depth is correct
  4. Required sections are present
  5. Content slots reference valid sections
  6. Spatial rules are consistent
  7. Design tokens are complete
  8. Grammar rules are satisfied
"""

import logging
from typing import Optional
from ui_ast.schema import UIAST, LayoutNode
from ui_ast.grammar_engine import UIGrammarEngine

logger = logging.getLogger(__name__)


class UIASTValidator:
    """Strict validator for UI AST — rejects invalid ASTs hard."""

    def __init__(self):
        self.grammar = UIGrammarEngine()

    def validate(self, ast: UIAST) -> dict:
        """
        Full validation of a UI AST.

        Returns
        -------
        dict with:
          - valid: bool
          - errors: list[str]   (MUST fix — generation will fail)
          - warnings: list[str] (SHOULD fix — generation may be suboptimal)
          - score: float (0-1)
        """
        errors = []
        warnings = []

        # ── 1. Layout Tree ─────────────────────────────────────────
        if not ast.layout_tree:
            errors.append("CRITICAL: Missing layout_tree — AST has no page structure")
        else:
            tree_errors, tree_warnings = self._validate_layout_tree(ast.layout_tree)
            errors.extend(tree_errors)
            warnings.extend(tree_warnings)

        # ── 2. Components ──────────────────────────────────────────
        if not ast.components:
            errors.append("CRITICAL: No components defined")
        else:
            comp_errors, comp_warnings = self._validate_components(ast)
            errors.extend(comp_errors)
            warnings.extend(comp_warnings)

        # ── 3. Design Tokens ───────────────────────────────────────
        token_errors, token_warnings = self._validate_design_tokens(ast.design_tokens)
        errors.extend(token_errors)
        warnings.extend(token_warnings)

        # ── 4. Constraints ─────────────────────────────────────────
        constraint_errors = self._validate_constraints(ast)
        errors.extend(constraint_errors)

        # ── 5. Content Slots ───────────────────────────────────────
        slot_warnings = self._validate_content_slots(ast)
        warnings.extend(slot_warnings)

        # ── 6. Grammar Rules ──────────────────────────────────────
        if ast.constraints.order:
            grammar_report = self.grammar.validate_full_structure(ast.constraints.order)
            if not grammar_report["valid"]:
                errors.extend(grammar_report["violations"])
            warnings.extend(grammar_report.get("warnings", []))

        # ── 7. Compiler Flags Consistency ──────────────────────────
        if ast.compiler_flags.strict_mode:
            if ast.compiler_flags.allow_llm_layout_changes:
                errors.append("CONFLICT: strict_mode=True but allow_llm_layout_changes=True")
            min_s = ast.compiler_flags.min_sections
            max_s = ast.compiler_flags.max_sections
            actual = len(ast.components)
            if actual < min_s:
                errors.append(
                    f"Too few sections: {actual} < min_sections={min_s}"
                )
            if actual > max_s:
                warnings.append(
                    f"Many sections: {actual} > max_sections={max_s}"
                )

        # ── Calculate score ────────────────────────────────────────
        total_checks = max(
            len(errors) + len(warnings) + 10, 1  # base of 10 "passed" checks
        )
        score = max(0.0, 1.0 - (len(errors) * 0.15 + len(warnings) * 0.05))

        is_valid = len(errors) == 0

        if not is_valid:
            logger.error(
                "AST VALIDATION FAILED: %d errors, %d warnings (score=%.2f)",
                len(errors), len(warnings), score,
            )
            for e in errors:
                logger.error("  ❌ %s", e)
        else:
            logger.info(
                "AST validation passed: %d warnings (score=%.2f)",
                len(warnings), score,
            )

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "score": round(score, 3),
        }

    def _validate_layout_tree(self, tree: LayoutNode) -> tuple[list, list]:
        """Validate the layout tree structure."""
        errors = []
        warnings = []

        if tree.type != "page":
            errors.append(f"Layout tree root must be type='page', got '{tree.type}'")

        if not tree.children:
            errors.append("Layout tree has no children (empty page)")
        elif len(tree.children) < 2:
            warnings.append("Layout tree has very few children — page may be too simple")

        # Check for duplicate IDs
        all_ids = self._collect_ids(tree)
        if len(all_ids) != len(set(all_ids)):
            dups = [id for id in all_ids if all_ids.count(id) > 1]
            errors.append(f"Duplicate IDs in layout tree: {set(dups)}")

        # Check depth (shouldn't be > 5 levels deep)
        max_depth = self._max_depth(tree)
        if max_depth > 5:
            warnings.append(f"Layout tree is {max_depth} levels deep — consider flattening")

        return errors, warnings

    def _validate_components(self, ast: UIAST) -> tuple[list, list]:
        """Validate that components are properly defined."""
        errors = []
        warnings = []

        for comp_id, comp_data in ast.components.items():
            if not comp_data.get("tag"):
                errors.append(f"Component '{comp_id}' has no tag")
            if not comp_data.get("component_name"):
                errors.append(f"Component '{comp_id}' has no component_name")

        # Cross-reference: every layout tree section should have a component
        if ast.layout_tree:
            tree_ids = self._collect_section_ids(ast.layout_tree)
            for tid in tree_ids:
                if tid not in ast.components:
                    warnings.append(
                        f"Section '{tid}' in layout_tree has no component definition"
                    )

        return errors, warnings

    def _validate_design_tokens(self, tokens) -> tuple[list, list]:
        """Validate design tokens completeness."""
        errors = []
        warnings = []

        palette = tokens.color_palette
        required_colors = ["primary", "background", "text_primary"]
        for color_key in required_colors:
            if not palette.get(color_key):
                errors.append(f"Design tokens missing required color: '{color_key}'")

        if not tokens.typography.get("font_family"):
            warnings.append("No font_family specified in design tokens")

        return errors, warnings

    def _validate_constraints(self, ast: UIAST) -> list:
        """Validate that constraints are satisfiable."""
        errors = []
        required = set(ast.constraints.required_sections)
        available = set(ast.components.keys())

        missing = required - available
        if missing:
            errors.append(
                f"Required sections missing from components: {missing}"
            )

        return errors

    def _validate_content_slots(self, ast: UIAST) -> list:
        """Validate content slots reference valid sections."""
        warnings = []
        component_ids = set(ast.components.keys())

        for slot_id in ast.content_slots:
            section_id = slot_id.split(".")[0]
            if section_id not in component_ids:
                warnings.append(
                    f"Content slot '{slot_id}' references unknown section '{section_id}'"
                )

        return warnings

    def _collect_ids(self, node: LayoutNode) -> list:
        """Recursively collect all IDs from a layout tree."""
        ids = [node.id]
        for child in node.children:
            if isinstance(child, LayoutNode):
                ids.extend(self._collect_ids(child))
        return ids

    def _collect_section_ids(self, node: LayoutNode) -> list:
        """Collect IDs of section-type nodes only."""
        ids = []
        if node.type == "section":
            ids.append(node.id)
        for child in node.children:
            if isinstance(child, LayoutNode):
                ids.extend(self._collect_section_ids(child))
        return ids

    def _max_depth(self, node: LayoutNode, current: int = 0) -> int:
        """Calculate maximum depth of the layout tree."""
        if not node.children:
            return current
        return max(
            self._max_depth(c, current + 1)
            for c in node.children
            if isinstance(c, LayoutNode)
        ) if any(isinstance(c, LayoutNode) for c in node.children) else current
