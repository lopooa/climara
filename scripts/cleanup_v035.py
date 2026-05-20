from pathlib import Path
import re
import subprocess
import sys

root = Path.cwd()

if not (root / "pyproject.toml").exists() or not (root / "src" / "climara").exists():
    raise SystemExit("请在 climara 项目根目录运行。")

print("开始 v0.3.5 cleanup...")

patterns = [
    "*.bak_v031",
    "*.bak_v032",
    "*.bak_v033",
    "*.bak_v034",
    "*.bak_inner_edge_tick",
    "*.bak_panel_tick_values",
    "*.bak_fix_panel_lon_grid_only",
    "*.bak_lon_values",
    "*.bak_v033_frame_gridlabel",
    "*.bak_v033_plain_axis_ticks",
    "*.bak_v033_cleanup_after_plot",
    "*.bak_geoaxis_plain_ticks",
    "*.bak_gridliner_labels_off",
]

removed = []

for pattern in patterns:
    for path in root.rglob(pattern):
        if ".git" in path.parts:
            continue
        path.unlink()
        removed.append(path)

for name in [
    "apply_climara_v031.sh",
    "apply_climara_v034.sh",
    "apply_climara_v034.py",
]:
    path = root / name
    if path.exists():
        path.unlink()
        removed.append(path)

print(f"已清理临时文件数量：{len(removed)}")
for path in removed:
    print(f"  删除：{path.relative_to(root)}")

pyproject = root / "pyproject.toml"
text = pyproject.read_text(encoding="utf-8")
text = re.sub(r'version\s*=\s*"[^"]+"', 'version = "0.3.5"', text, count=1)
pyproject.write_text(text, encoding="utf-8")
print("已更新：pyproject.toml -> 0.3.5")

version_file = root / "src" / "climara" / "_version.py"
version_file.write_text('__version__ = "0.3.5"\n', encoding="utf-8")
print("已更新：src/climara/_version.py -> 0.3.5")

test_file = root / "tests" / "test_imports.py"
if test_file.exists():
    text = test_file.read_text(encoding="utf-8")
    text = re.sub(r'__version__\s*==\s*"[^"]+"', '__version__ == "0.3.5"', text)
    test_file.write_text(text, encoding="utf-8")
    print("已更新：tests/test_imports.py -> 0.3.5")

readme = root / "README.md"
if readme.exists():
    text = readme.read_text(encoding="utf-8")
    for old in ["0.3.4", "0.3.3", "0.3.2", "0.3.1", "0.3.0"]:
        text = text.replace(f"@v{old}", "@v0.3.5")
        text = text.replace(f"Current version: `v{old}`", "Current version: `v0.3.5`")
    readme.write_text(text, encoding="utf-8")
    print("已更新：README.md 版本号")

notes = root / "docs" / "v0.3.5_notes.md"
notes.write_text(
    """# v0.3.5 notes

这个版本是 v0.3.x 阶段的 cleanup 版本。

## 主要内容

- 清理 v0.3.1 到 v0.3.4 开发过程中留下的临时备份文件。
- 保留正式的 src、examples、docs 内容。
- 将版本号更新到 0.3.5。
- 不新增核心绘图功能。

## 当前 v0.3.x 阶段总结

- v0.3.1：Panel / LabelBar / TickMark。
- v0.3.2：ContourPlot 高级参数。
- v0.3.3：MapPlot / 投影 / mp 资源体系。
- v0.3.4：资源查询与投影示例。
- v0.3.5：清理和稳定。
""",
    encoding="utf-8",
)
print("已写入：docs/v0.3.5_notes.md")

print("开始语法检查...")
subprocess.run([sys.executable, "-m", "compileall", "src", "tests", "examples", "scripts"], check=True)

print("v0.3.5 cleanup 完成。")
