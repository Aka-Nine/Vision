"""
Template Generator Agent — Phase 3 (UI AST Powered)
Orchestrates the full template generation workflow:
  compile UI AST → build project → generate components → validate → store.

Now consumes the strict UI AST from Phase 2.5 compiler instead of
loose design briefs. This ensures deterministic, non-generic output.
"""
import os, json, logging, glob
from agents.base_agent import BaseAgent
from template_generator.brief_parser import BriefParser
from template_generator.layout_builder import LayoutBuilder
from template_generator.component_generator import ComponentGenerator
from template_generator.style_generator import StyleGenerator
from template_generator.project_builder import ProjectBuilder
from template_generator.asset_manager import AssetManager
from template_generator.code_validator import CodeValidator
from template_generator.preview_builder import PreviewBuilder
from template_generator.template_packager import TemplatePackager
from ui_ast.compiler import UIASTCompiler
from ui_ast.validator import UIASTValidator
from ui_ast.feedback_loop import feedback_loop, FeedbackRecord
from monitoring.metrics import metrics
import time

logger = logging.getLogger(__name__)

OUTPUT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_templates")


class TemplateGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("TemplateGeneratorAgent", "Converts design briefs into working UI templates via UI AST")
        self.brief_parser = BriefParser()
        self.layout_builder = LayoutBuilder()
        self.component_generator = ComponentGenerator()
        self.style_generator = StyleGenerator()
        self.project_builder = ProjectBuilder()
        self.asset_manager = AssetManager()
        self.code_validator = CodeValidator()
        self.preview_builder = PreviewBuilder()
        self.template_packager = TemplatePackager()

        # NEW: UI AST compiler and validator
        self.ast_compiler = UIASTCompiler()
        self.ast_validator = UIASTValidator()

    async def process(self, task_input: dict) -> dict:
        brief = task_input.get("brief", {})
        semantic_brief = task_input.get("semantic_brief")
        if not brief:
            raise ValueError("No design brief provided")

        start = time.time()

        # ══════════════════════════════════════════════════════════════
        # PHASE 2.5: Compile UI AST (NEW — replaces ad-hoc enrichment)
        # ══════════════════════════════════════════════════════════════
        await self.log_activity("ast_compilation_started", {"info": "Compiling UI AST from market intelligence"})

        # Load extracted patterns from storage
        patterns = self._load_patterns()

        ui_ast = await self.ast_compiler.compile(
            semantic_brief=semantic_brief,
            design_brief=brief,
            patterns=patterns,
            market_data=self._extract_market_data(brief),
        )

        # Validate the compiled AST
        ast_validation = self.ast_validator.validate(ui_ast)
        await self.log_activity("ast_compiled", {
            "valid": ast_validation["valid"],
            "score": ast_validation["score"],
            "sections": len(ui_ast.components),
            "pattern": ui_ast.provenance.dominant_pattern,
            "tier": ui_ast.meta.get("complexity_tier"),
            "warnings": len(ast_validation.get("warnings", [])),
        })

        if not ast_validation["valid"] and not ui_ast.compiler_flags.regenerate_on_failure:
            raise ValueError(f"UI AST validation failed: {ast_validation['errors']}")

        # ══════════════════════════════════════════════════════════════
        # PHASE 3: Generate from AST (existing pipeline, now AST-powered)
        # ══════════════════════════════════════════════════════════════

        # 1. Parse the design brief (still needed for backward compat)
        await self.log_activity("brief_parsing_started", {"info": "Parsing design brief"})
        spec = await self.brief_parser.parse(brief)

        # 1.5. Enrich spec with UI AST data (UPGRADED from raw semantic injection)
        spec = self._enrich_spec_from_ast(spec, ui_ast)

        if semantic_brief and not semantic_brief.get("_is_fallback"):
            spec = self._enrich_spec_with_semantic_brief(spec, semantic_brief)
            await self.log_activity("semantic_enrichment_applied", {
                "sections_enriched": len(semantic_brief.get("sections", [])),
                "avg_confidence": semantic_brief.get("_stats", {}).get("avg_confidence", 0),
            })

        # 2. Build project scaffold
        await self.log_activity("project_building_started", {"info": "Scaffolding project"})
        project_info = await self.project_builder.build(spec, OUTPUT_ROOT)
        project_dir = project_info["project_dir"]

        # 3. Generate styles (now informed by AST design tokens)
        await self.log_activity("style_generation_started", {"info": "Generating styles"})
        style_result = await self.style_generator.generate(spec, project_dir)

        # 4. Build layout (now informed by AST spatial rules)
        await self.log_activity("layout_building_started", {"info": "Building layout"})
        layout = await self.layout_builder.build(spec, project_dir)

        # 5. Generate components (now constrained by AST)
        await self.log_activity("component_generation_started", {"info": "Generating components"})
        components = await self.component_generator.generate(layout, spec, project_dir)

        # 6. Generate assets
        await self.log_activity("asset_generation_started", {"info": "Generating assets"})
        assets = await self.asset_manager.generate(spec, project_dir)

        # 7. Validate
        await self.log_activity("code_validation_started", {"info": "Validating code"})
        validation = await self.code_validator.validate(project_dir)

        build_errors = len(validation.get("errors", []))
        if not validation["valid"]:
            await self.log_activity("code_validation_failed", {"errors": validation["errors"]})
            # Don't raise immediately — record feedback first
            if not ui_ast.compiler_flags.regenerate_on_failure:
                self._record_feedback(ui_ast, ast_validation, False, build_errors, time.time() - start)
                raise Exception(f"Template validation failed: {validation['errors']}")

        # 8. Preview (best-effort)
        await self.log_activity("preview_generation_started", {"info": "Generating preview"})
        preview = await self.preview_builder.build(project_dir)

        # 9. Package
        await self.log_activity("packaging_started", {"info": "Packaging template"})
        package = await self.template_packager.package(project_dir, spec, validation)

        # Save the UI AST alongside the generated project
        ast_path = os.path.join(project_dir, "ui_ast.json")
        with open(ast_path, "w", encoding="utf-8") as f:
            json.dump(ui_ast.to_dict(), f, indent=2, default=str)

        elapsed = time.time() - start
        metrics.pipeline_success.inc()

        # ── Record feedback (Fix #10) ──────────────────────────────
        generation_success = validation.get("valid", False)
        self._record_feedback(ui_ast, ast_validation, generation_success, build_errors, elapsed)

        result = {
            "status": "success",
            "template_name": project_info["template_name"],
            "project_dir": project_dir,
            "components_generated": len(components),
            "validation": validation,
            "preview": preview,
            "package": package,
            "generation_time_seconds": round(elapsed, 2),
            "semantic_enriched": semantic_brief is not None and not semantic_brief.get("_is_fallback"),
            # NEW: AST metadata
            "ast_info": {
                "template_id": ui_ast.meta.get("template_id"),
                "dominant_pattern": ui_ast.provenance.dominant_pattern,
                "complexity_tier": ui_ast.meta.get("complexity_tier"),
                "variation_seed": ui_ast.variation.variation_seed,
                "ast_validation_score": ast_validation["score"],
                "design_system": ui_ast.meta.get("design_system"),
            },
        }

        await self.log_activity("template_generation_completed", result)
        return result

    def _enrich_spec_from_ast(self, spec: dict, ui_ast) -> dict:
        """
        Inject UI AST constraints into the template spec.
        This provides structured, enforceable design constraints
        instead of loose descriptive patterns.
        """
        # Inject design tokens
        tokens = ui_ast.design_tokens
        spec["style"]["accent_color"] = tokens.color_palette.get("primary", spec["style"].get("accent_color"))
        spec["style"]["surface_color"] = tokens.color_palette.get("background", spec["style"].get("surface_color"))

        # Inject variation config
        spec["_variation"] = ui_ast.variation.to_dict()

        # Inject spatial rules
        spec["_spatial_rules"] = ui_ast.spatial_rules

        # Inject component specs with strong mapping
        spec["_component_specs"] = ui_ast.components

        # Inject content slots
        spec["_content_slots"] = ui_ast.content_slots

        # Inject constraints
        spec["_constraints"] = ui_ast.constraints.to_dict()

        # Inject complexity info
        spec["_complexity_tier"] = ui_ast.meta.get("complexity_tier", "standard")

        # Inject provenance for debugging
        spec["_provenance"] = ui_ast.provenance.to_dict()

        logger.info(
            "Spec enriched from AST: %d spatial rules, %d component specs, %d content slots",
            len(ui_ast.spatial_rules),
            len(ui_ast.components),
            len(ui_ast.content_slots),
        )

        return spec

    def _enrich_spec_with_semantic_brief(self, spec: dict, semantic_brief: dict) -> dict:
        """
        Inject Phase 2.5 semantic content into the template spec.
        This provides real, ranked content to the component generator
        instead of relying on generic fallbacks.
        """
        semantic_sections = semantic_brief.get("sections", [])
        if not semantic_sections:
            return spec

        # Build a content map: section_type -> content
        content_map = {}
        for section in semantic_sections:
            sec_type = section.get("type", "")
            content = section.get("content", {})
            if sec_type and content:
                content_map[sec_type] = {
                    "heading": content.get("heading"),
                    "description": content.get("subtext"),
                    "cta_texts": content.get("cta_texts", []),
                    "intent": section.get("intent"),
                    "confidence": section.get("meta", {}).get("confidence", 0),
                }

        # Attach semantic content map to spec for component generator consumption
        spec["_semantic_content"] = content_map

        # Also attach design tokens from the semantic brief
        design_tokens = semantic_brief.get("design_tokens", {})
        if design_tokens:
            spec["_design_tokens"] = design_tokens

        # Attach market context
        market_context = semantic_brief.get("market_context", {})
        if market_context:
            spec["_market_context"] = market_context

        logger.info(
            "Enriched spec with %d semantic sections (keys: %s)",
            len(content_map),
            list(content_map.keys()),
        )

        return spec

    def _load_patterns(self) -> list[dict]:
        """Load extracted patterns from storage."""
        patterns = []
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patterns")
        if os.path.exists(patterns_dir):
            for f in glob.glob(os.path.join(patterns_dir, "*_patterns.json")):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        if isinstance(data, list):
                            patterns.extend(data)
                        else:
                            patterns.append(data)
                except Exception:
                    pass
        return patterns

    def _extract_market_data(self, brief: dict) -> dict:
        """Extract market-relevant data from a brief for the compiler."""
        return {
            "demand_score": brief.get("demand_score", 0.5),
            "competition_score": brief.get("competition_score", 0.5),
            "trends": brief.get("trends", []),
        }

    def _record_feedback(self, ui_ast, ast_validation, generation_success, build_errors, elapsed):
        """Record generation outcome into the feedback loop."""
        try:
            # Calculate content fill rate
            total_slots = len(ui_ast.content_slots)
            filled_slots = sum(
                1 for s in ui_ast.content_slots.values()
                if s.get("value") is not None
            )
            fill_rate = filled_slots / max(total_slots, 1)

            record = FeedbackRecord(
                template_id=ui_ast.meta.get("template_id", "unknown"),
                ast_validation_score=ast_validation.get("score", 0),
                generation_success=generation_success,
                dominant_pattern=ui_ast.provenance.dominant_pattern or "",
                variation_seed=ui_ast.variation.variation_seed,
                section_count=len(ui_ast.components),
                content_fill_rate=fill_rate,
                build_errors=build_errors,
                generation_time_seconds=elapsed,
                demand_score=ui_ast.provenance.demand_score,
                complexity_tier=ui_ast.meta.get("complexity_tier", ""),
            )
            feedback_loop.record(record)
        except Exception as e:
            logger.warning("Failed to record feedback: %s", e)
