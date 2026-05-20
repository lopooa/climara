from pathlib import Path
import subprocess
import sys
import tomllib

root = Path.cwd()

if not (root / "pyproject.toml").exists() or not (root / "src" / "climara").exists():
    raise SystemExit("请在 climara 项目根目录运行。")

print("检查版本号...")

with open(root / "pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

project_version = pyproject["project"]["version"]

from climara import __version__

if project_version != __version__:
    raise SystemExit(f"版本号不一致：pyproject={project_version}, climara={__version__}")

if project_version != "0.3.4":
    raise SystemExit(f"当前版本不是 0.3.4，而是 {project_version}")

print("版本号正常：0.3.4")

print("检查公开导入...")

from climara.plotting import (
    ncl_style,
    gsn_csm_contour_map,
    resource_groups,
    print_resource_groups,
    projection_aliases,
    print_projection_aliases,
)

print("公开导入正常")

print("检查资源分组...")

groups = resource_groups()
required_groups = ["ContourPlot", "MapPlot", "LabelBar", "TickMark", "Panel", "Titles"]

for name in required_groups:
    if name not in groups:
        raise SystemExit(f"缺少资源分组：{name}")

aliases = projection_aliases()
required_projections = [
    "CylindricalEquidistant",
    "Robinson",
    "Mollweide",
    "Orthographic",
    "NorthPolarStereo",
    "LambertConformal",
]

for name in required_projections:
    if name not in aliases:
        raise SystemExit(f"缺少投影别名：{name}")

print("资源分组正常")

print("检查关键示例文件...")

required_files = [
    "examples/demo_19_v031_panel_labelbar_tickmark.py",
    "examples/demo_20_v032_contour_advanced.py",
    "examples/demo_22_v033_mapplot_resources.py",
    "examples/demo_23_v034_projection_gallery.py",
    "docs/v0.3.1_notes.md",
    "docs/v0.3.2_notes.md",
    "docs/v0.3.3_notes.md",
    "docs/v0.3.4_notes.md",
]

for rel in required_files:
    path = root / rel
    if not path.exists():
        raise SystemExit(f"缺少文件：{rel}")

print("关键示例和文档正常")

print("运行 compileall 语法检查...")

subprocess.run(
    [sys.executable, "-m", "compileall", "src", "tests", "examples"],
    check=True,
)

print("全部检查通过。")
