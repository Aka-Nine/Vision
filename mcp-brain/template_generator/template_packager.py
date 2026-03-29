"""
Template Packager — Phase 3 Module
Prepares generated templates for distribution by creating a
zip archive and metadata file.

Version 2.0 — Added template versioning, framework tracking,
brief linkage, and auto-increment on re-generation.
"""
import os, json, zipfile, logging, time, hashlib

logger = logging.getLogger(__name__)


class TemplatePackager:
    """Package a generated template into a distributable zip with metadata."""

    async def package(self, project_dir: str, spec: dict, validation: dict) -> dict:
        template_name = os.path.basename(project_dir)
        parent_dir = os.path.dirname(project_dir)
        zip_name = f"{template_name}.zip"
        zip_path = os.path.join(parent_dir, zip_name)

        # 1. Create zip (exclude node_modules, dist, .git)
        excluded = {"node_modules", "dist", ".git", "__pycache__"}
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(project_dir):
                dirs[:] = [d for d in dirs if d not in excluded]
                for fname in files:
                    abs_path = os.path.join(root, fname)
                    arc_name = os.path.relpath(abs_path, parent_dir)
                    zf.write(abs_path, arc_name)

        zip_size = os.path.getsize(zip_path)
        logger.info("Packaged → %s  (%.1f KB)", zip_path, zip_size / 1024)

        # 2. Compute version (auto-increment if the same name exists)
        registry_path = os.path.join(parent_dir, "template_registry.json")
        registry = self._read_registry(registry_path)
        version = self._compute_version(template_name, registry)

        # 3. Generate a brief fingerprint for linkage
        brief_hash = hashlib.md5(
            json.dumps(spec, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]

        # 4. Build versioned metadata entry
        metadata = {
            "template_name": template_name,
            "version": version,
            "framework": "react",
            "framework_version": "18.x",
            "bundler": "vite",
            "css_framework": "tailwindcss",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source_brief": f"brief_{brief_hash}",
            "brief_hash": brief_hash,
            "components": validation.get("component_count", 0),
            "template_type": spec.get("template_type", ""),
            "target_market": spec.get("target_market", ""),
            "demand_score": spec.get("demand_score", 0.0),
            "sections": spec.get("sections", []),
            "style_theme": spec.get("style", {}).get("theme", "dark"),
            "validation": {
                "valid": validation.get("valid", False),
                "warnings": len(validation.get("warnings", [])),
            },
            "archive": zip_name,
            "archive_size_bytes": zip_size,
        }

        # 5. Update registry
        registry = [e for e in registry if e.get("template_name") != template_name]
        registry.append(metadata)

        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2)

        logger.info("Registry updated → %s  (%d templates, v%s)", registry_path, len(registry), version)

        return {
            "zip_path": zip_path,
            "zip_size_bytes": zip_size,
            "metadata": metadata,
            "registry_path": registry_path,
        }

    # ── Helper methods ──────────────────────────────────────────────

    def _read_registry(self, path: str) -> list:
        if os.path.isfile(path):
            with open(path) as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _compute_version(self, template_name: str, registry: list) -> str:
        """Auto-increment version when re-generating an existing template."""
        existing = [e for e in registry if e.get("template_name") == template_name]
        if not existing:
            return "1.0"
        try:
            latest = max(float(e.get("version", "1.0")) for e in existing)
            return f"{latest + 1.0:.1f}"
        except (ValueError, TypeError):
            return "1.0"

