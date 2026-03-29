import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from template_generator.preview_builder import PreviewBuilder


async def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/build_preview.py <project_dir>")
        return 2

    project_dir = sys.argv[1]
    pb = PreviewBuilder()
    res = await pb.build(project_dir)
    print(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

