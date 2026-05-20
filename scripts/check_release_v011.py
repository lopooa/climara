from pathlib import Path
import subprocess
import sys
import tomllib

root = Path.cwd()

if not (root / "pyproject.toml").exists() or not (root / "src" / "climara").exists():
    raise SystemExit("请在 climara 项目根目录运行。")

print("检查版本号...")

with open(root / "pyproject.toml", "rb") as f:
    data = tomllib.load(f)

project_version = data["project"]["version"]

import climara

if project_version != "0.1.1":
    raise SystemExit(f"pyproject.toml 版本不是 0.1.1，而是 {project_version}")

if climara.__version__ != "0.1.1":
    raise SystemExit(f"climara.__version__ 不是 0.1.1，而是 {climara.__version__}")

print("版本号正常：0.1.1")

print("检查 README...")

readme = root / "README.md"
if not readme.exists():
    raise SystemExit("缺少 README.md")

text = readme.read_text(encoding="utf-8")

if "Current version: `v0.1.1`" not in text:
    raise SystemExit("README.md 中没有 Current version: `v0.1.1`")

required_images = [
    "docs/assets/panel_labelbar_tickmark.png",
    "docs/assets/contour_line_labels.png",
    "docs/assets/projection_robinson.png",
    "docs/assets/projection_orthographic.png",
]

for rel in required_images:
    if rel in text and not (root / rel).exists():
        raise SystemExit(f"README 引用了图片，但文件不存在：{rel}")

print("README 正常")

print("检查公开导入...")

from climara.plotting import (
    ncl_style,
    gsn_csm_contour_map,
    resource_groups,
    print_resource_groups,
    projection_aliases,
    print_projection_aliases,
)

groups = resource_groups()
aliases = projection_aliases()

for key in ["ContourPlot", "MapPlot", "LabelBar", "TickMark", "Panel", "Titles"]:
    if key not in groups:
        raise SystemExit(f"缺少资源分组：{key}")

for key in ["Robinson", "Mollweide", "Orthographic", "LambertConformal"]:
    if key not in aliases:
        raise SystemExit(f"缺少投影别名：{key}")

print("公开导入正常")

print("检查关键文件...")

required_files = [
    "examples/demo_19_v031_panel_labelbar_tickmark.py",
    "examples/demo_20_v032_contour_advanced.py",
    "examples/demo_22_v033_mapplot_resources.py",
    "examples/demo_23_v034_projection_gallery.py",
    "docs/gallery/index.md",
    "docs/v0.4.0_notes.md",
]

for rel in required_files:
    if not (root / rel).exists():
        raise SystemExit(f"缺少文件：{rel}")

print("关键文件正常")

print("运行语法检查...")

subprocess.run(
    [sys.executable, "-m", "compileall", "src", "tests", "examples", "scripts"],
    check=True,
)

print("全部检查通过。")
