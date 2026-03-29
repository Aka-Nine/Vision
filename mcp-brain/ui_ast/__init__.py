"""
UI AST — Phase 2.5 Compiler Output
════════════════════════════════════
Production-grade UI Abstract Syntax Tree that serves as
the ONLY contract between Phase 2 (Market Intelligence)
and Phase 3 (Template Generator Engine).

The compiler produces a strict, deterministic JSON AST
that Phase 3 consumes without modification.
"""

from ui_ast.schema import UIAST, LayoutNode, DesignTokens, ComponentSpec, ContentSlot
from ui_ast.compiler import UIASTCompiler
from ui_ast.validator import UIASTValidator

__all__ = [
    "UIAST",
    "LayoutNode",
    "DesignTokens",
    "ComponentSpec",
    "ContentSlot",
    "UIASTCompiler",
    "UIASTValidator",
]
