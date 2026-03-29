"""
Code Validator — Phase 3 Module
Ensures generated code is syntactically correct and structurally sound.
Rejects broken templates before they leave the pipeline.
"""
import os, re, json, logging

logger = logging.getLogger(__name__)

REQUIRED_DIRS = ["src/components", "src/pages", "src/styles"]
REQUIRED_ROOT_FILES = ["package.json", "index.html", "vite.config.js"]
REQUIRED_SRC_FILES = ["src/main.jsx", "src/App.jsx"]

# Basic React JSX patterns that must appear in every component
JSX_EXPORT_PATTERN = re.compile(r"export\s+default\s+function\s+\w+")
JSX_IMPORT_REACT = re.compile(r"import\s+React")

# Tailwind class pattern (at least some tw classes should exist)
TAILWIND_CLASS_PATTERN = re.compile(r'className="[^"]*(?:flex|grid|py-|px-|text-|bg-|rounded|border)[^"]*"')


class CodeValidator:
    """Validate generated project structure and code quality."""

    async def validate(self, project_dir: str) -> dict:
        errors = []
        warnings = []

        # 1. Folder structure
        for d in REQUIRED_DIRS:
            full = os.path.join(project_dir, d)
            if not os.path.isdir(full):
                errors.append(f"Missing directory: {d}")

        # 2. Root files
        for f in REQUIRED_ROOT_FILES:
            full = os.path.join(project_dir, f)
            if not os.path.isfile(full):
                errors.append(f"Missing root file: {f}")

        # 3. package.json integrity
        pkg_path = os.path.join(project_dir, "package.json")
        if os.path.isfile(pkg_path):
            try:
                with open(pkg_path) as f:
                    pkg = json.load(f)
                for dep in ["react", "react-dom"]:
                    if dep not in pkg.get("dependencies", {}):
                        errors.append(f"package.json missing dependency: {dep}")
                for dep in ["tailwindcss", "vite"]:
                    if dep not in pkg.get("devDependencies", {}):
                        warnings.append(f"package.json missing devDependency: {dep}")
            except json.JSONDecodeError:
                errors.append("package.json is not valid JSON")

        # 4. Source files
        for f in REQUIRED_SRC_FILES:
            full = os.path.join(project_dir, f)
            if not os.path.isfile(full):
                errors.append(f"Missing source file: {f}")

        # 5. Component files — check each JSX file
        comp_dir = os.path.join(project_dir, "src", "components")
        component_count: int = 0
        if os.path.isdir(comp_dir):
            for fname in os.listdir(comp_dir):
                if fname.endswith(".jsx"):
                    component_count += 1
                    fpath = os.path.join(comp_dir, fname)
                    with open(fpath, "r") as cf:
                        content = cf.read()
                    if not JSX_EXPORT_PATTERN.search(content):
                        errors.append(f"{fname}: missing default export function")
                    if not JSX_IMPORT_REACT.search(content):
                        warnings.append(f"{fname}: missing React import")
                    if not TAILWIND_CLASS_PATTERN.search(content):
                        warnings.append(f"{fname}: no Tailwind classes detected")

        # 6. Tailwind CSS file
        css_path = os.path.join(project_dir, "src", "styles", "tailwind.css")
        if os.path.isfile(css_path):
            with open(css_path) as f:
                css = f.read()
            if "@tailwind base" not in css:
                errors.append("tailwind.css missing @tailwind base directive")
        else:
            errors.append("Missing src/styles/tailwind.css")

        # 7. Apply strict Antigravity Aesthetic Benchmark
        self._enforce_aesthetic_benchmark(project_dir, errors, warnings)

        is_valid = len(errors) == 0
        result = {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "component_count": component_count,
            "checks_passed": (len(REQUIRED_DIRS) + len(REQUIRED_ROOT_FILES)
                              + len(REQUIRED_SRC_FILES) + component_count + 1 - len(errors)),
        }

        if is_valid:
            logger.info("Validation PASSED — %d components, %d warnings", component_count, len(warnings))
        else:
            logger.error("Validation FAILED — %d errors: %s", len(errors), errors)

        return result

    def _enforce_aesthetic_benchmark(self, project_dir: str, errors: list, warnings: list):
        """
        Enforce the Antigravity Aesthetic Benchmark.
        If the template does not utilize high-end animation libraries and styling techniques
        commensurate with the Antigravity/Animation Showcase benchmark, discard it.
        """
        has_gsap = False
        has_lenis = False
        has_framer = False
        has_glassmorphism = False
        has_complex_gradients = False
        has_particles_or_canvas = False
        
        # Check package.json for libraries
        pkg_path = os.path.join(project_dir, "package.json")
        if os.path.isfile(pkg_path):
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    pkg = json.load(f)
                    deps = str(pkg.get("dependencies", {})) + str(pkg.get("devDependencies", {}))
                    if "gsap" in deps: has_gsap = True
                    if "lenis" in deps or "@studio-freight/lenis" in deps: has_lenis = True
                    if "framer-motion" in deps: has_framer = True
            except:
                pass

        # Scan all source code files for aesthetic signatures
        src_dir = os.path.join(project_dir, "src")
        if os.path.isdir(src_dir):
            for root, dirs, files in os.walk(src_dir):
                for f in files:
                    if f.endswith((".jsx", ".tsx", ".js", ".ts", ".css", ".html")):
                        fpath = os.path.join(root, f)
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as cf:
                            content = cf.read()
                            if "gsap" in content or "ScrollTrigger" in content: has_gsap = True
                            if "lenis" in content.lower(): has_lenis = True
                            if "backdrop-blur" in content or "backdrop-filter" in content: has_glassmorphism = True
                            if "bg-gradient-to" in content or "linear-gradient" in content: has_complex_gradients = True
                            if "<canvas" in content or "requestAnimationFrame" in content: has_particles_or_canvas = True
                            if "framer-motion" in content: has_framer = True
                            
        # The Benchmark Check (Strict Mode for Antigravity Level)
        aesthetic_score = 0
        if has_gsap: aesthetic_score += 4
        if has_lenis: aesthetic_score += 3
        if has_framer: aesthetic_score += 2
        if has_glassmorphism: aesthetic_score += 2
        if has_complex_gradients: aesthetic_score += 2
        if has_particles_or_canvas: aesthetic_score += 3
        
        # Benchmark threshold: Must hit 14 points
        # Meaning it MUST include GSAP(4) + Lenis(3) + Glass(2) + Gradients(2) + Particles(3) = 14
        # The current basic generation pipeline only makes 6 points (Framer+Gradients+Glass).
        if aesthetic_score < 14:
            benchmark_err = (
                f"AESTHETIC BENCHMARK FAILED (Score {aesthetic_score}/4): "
                f"The generated UI is below the Antigravity/Animation Showcase quality standard. "
                f"Required techniques missing. Detected: "
                f"GSAP/Framer: {has_gsap or has_framer}, Lenis: {has_lenis}, "
                f"Glassmorphism: {has_glassmorphism}, Gradients: {has_complex_gradients}. "
                f"Discarding template."
            )
            errors.append(benchmark_err)
            logger.error(benchmark_err)
        else:
            logger.info(f"✨ Aesthetic Benchmark PASSED (Score {aesthetic_score}): Quality meets Antigravity standards.")
