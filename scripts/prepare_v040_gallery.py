from pathlib import Path
import shutil

root = Path.cwd()

if not (root / "pyproject.toml").exists() or not (root / "src" / "climara").exists():
    raise SystemExit("请在 climara 项目根目录运行。")

assets = root / "docs" / "assets"
gallery = root / "docs" / "gallery"
assets.mkdir(parents=True, exist_ok=True)
gallery.mkdir(parents=True, exist_ok=True)

image_map = {
    "demo_19_v031_panel_labelbar_tickmark.png": "panel_labelbar_tickmark.png",
    "demo_20_v032_contour_line_labels.png": "contour_line_labels.png",
    "demo_21_v032_contour_constant_field.png": "contour_constant_field.png",
    "demo_22_v033_map_robinson.png": "map_robinson.png",
    "demo_22_v033_map_orthographic.png": "map_orthographic.png",
    "demo_23_v034_projection_platecarree.png": "projection_platecarree.png",
    "demo_23_v034_projection_robinson.png": "projection_robinson.png",
    "demo_23_v034_projection_mollweide.png": "projection_mollweide.png",
    "demo_23_v034_projection_orthographic.png": "projection_orthographic.png",
    "demo_23_v034_projection_north_polar_stereo.png": "projection_north_polar_stereo.png",
    "demo_23_v034_projection_lambert_conformal.png": "projection_lambert_conformal.png",
}

copied = []

for src_name, dst_name in image_map.items():
    src = root / src_name
    dst = assets / dst_name

    if src.exists():
        shutil.copy2(src, dst)
        copied.append((src_name, dst_name))

print(f"已复制示例图片数量：{len(copied)}")
for src_name, dst_name in copied:
    print(f"  {src_name} -> docs/assets/{dst_name}")

gallery_md = """# climara gallery

这个页面整理 climara v0.3.x 阶段的主要绘图示例。

## Panel / LabelBar / TickMark

![panel labelbar tickmark](../assets/panel_labelbar_tickmark.png)

这个示例展示：

- panel 布局。
- 共享 labelbar。
- 外侧 tick labels。
- NCL-style figure strings。

## ContourPlot

### Line labels and info label

![contour line labels](../assets/contour_line_labels.png)

这个示例展示：

- 填色图。
- 等值线。
- 等值线标签。
- info label。

### Constant field fallback

![constant field](../assets/contour_constant_field.png)

这个示例展示常数场的安全回退处理。

## MapPlot

### Robinson

![map robinson](../assets/map_robinson.png)

### Orthographic

![map orthographic](../assets/map_orthographic.png)

## Projection examples

### CylindricalEquidistant

![projection platecarree](../assets/projection_platecarree.png)

### Robinson

![projection robinson](../assets/projection_robinson.png)

### Mollweide

![projection mollweide](../assets/projection_mollweide.png)

### Orthographic

![projection orthographic](../assets/projection_orthographic.png)

### NorthPolarStereo

![projection north polar stereo](../assets/projection_north_polar_stereo.png)

### LambertConformal

![projection lambert conformal](../assets/projection_lambert_conformal.png)
"""

(gallery / "index.md").write_text(gallery_md, encoding="utf-8")
print("已写入：docs/gallery/index.md")

notes = """# v0.4.0 notes

这个版本开始进入 climara 的文档展示准备阶段。

## 当前目标

v0.4.0 不是 PyPI 正式发布版，而是发布准备版。

主要目标：

- 整理示例图片。
- 建立 gallery 文档。
- 重写 README 草稿。
- 检查打包信息。
- 为后续 PyPI 发布做准备。

## v0.4.0-1

本步骤完成：

- 新增 `docs/assets/`。
- 新增 `docs/gallery/index.md`。
- 将 v0.3.x 阶段的核心示例图片复制到文档资源目录。
"""

(root / "docs" / "v0.4.0_notes.md").write_text(notes, encoding="utf-8")
print("已写入：docs/v0.4.0_notes.md")

print("完成：v0.4.0-1 gallery 准备完成。")
