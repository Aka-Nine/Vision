"""
Phase 3 integration test — generate a template from the last design brief 
in market_data.json.
"""
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from template_generator.brief_parser import BriefParser
from template_generator.layout_builder import LayoutBuilder
from template_generator.component_generator import ComponentGenerator
from template_generator.style_generator import StyleGenerator
from template_generator.project_builder import ProjectBuilder
from template_generator.asset_manager import AssetManager
from template_generator.code_validator import CodeValidator
from template_generator.template_packager import TemplatePackager

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

OUTPUT = os.path.join(os.path.dirname(__file__), "generated_templates")

async def main():
    # Load a brief from market_data.json
    with open("market_data.json") as f:
        data = json.load(f)
    
    briefs = data.get("design_briefs", [])
    # Pick the last brief that has sections
    brief = None
    for b in reversed(briefs):
        if b.get("sections"):
            brief = b
            break
    
    if not brief:
        print("ERROR: No usable brief found in market_data.json")
        return
    
    print(f"\n{'='*60}")
    print(f"  PHASE 3 TEMPLATE GENERATOR — INTEGRATION TEST")
    print(f"{'='*60}")
    print(f"  Brief type: {brief.get('product_type', brief.get('template_type', 'N/A'))}")
    print(f"  Sections:   {brief.get('sections', [])}")
    print(f"{'='*60}\n")

    # 1. Parse
    parser = BriefParser()
    spec = await parser.parse(brief)
    print(f"✓ Brief parsed → layout={spec['layout']}, {len(spec['sections'])} sections")

    # 2. Scaffold
    builder = ProjectBuilder()
    project = await builder.build(spec, OUTPUT)
    project_dir = project["project_dir"]
    print(f"✓ Project scaffold → {project_dir}")

    # 3. Styles
    styler = StyleGenerator()
    styles = await styler.generate(spec, project_dir)
    print(f"✓ Styles generated → theme={styles['theme']}")

    # 4. Layout
    layout_builder = LayoutBuilder()
    layout = await layout_builder.build(spec, project_dir)
    print(f"✓ Layout built → {len(layout['page'])} sections")

    # 5. Components
    comp_gen = ComponentGenerator()
    components = await comp_gen.generate(layout, spec, project_dir)
    print(f"✓ Components generated → {len(components)} files")

    # 6. Assets
    asset_mgr = AssetManager()
    assets = await asset_mgr.generate(spec, project_dir)
    print(f"✓ Assets generated → {len(assets['icons'])} icons")

    # 7. Validate
    validator = CodeValidator()
    validation = await validator.validate(project_dir)
    status = "PASSED ✓" if validation["valid"] else "FAILED ✗"
    print(f"✓ Validation {status} → {validation['component_count']} components, {len(validation['warnings'])} warnings")
    if validation["errors"]:
        for e in validation["errors"]:
            print(f"  ERROR: {e}")

    # 8. Package
    packager = TemplatePackager()
    pkg = await packager.package(project_dir, spec, validation)
    print(f"✓ Packaged → {pkg['zip_path']} ({pkg['zip_size_bytes']/1024:.1f} KB)")

    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"  Template: {project['template_name']}")
    print(f"  Location: {project_dir}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
