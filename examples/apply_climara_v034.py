from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys

root = Path.cwd()

if not (root / "pyproject.toml").exists() or not (root / "src" / "climara").exists():
    raise SystemExit("请在 climara 项目根目录运行，也就是能看到 pyproject.toml 和 src/climara 的目录。")


def backup(path: Path) -> None:
    path = Path(path)
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak_v034")
        if not bak.exists():
            shutil.copy2(path, bak)


def write_text(rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    backup(path)
    path.write_text(text.lstrip("\n"), encoding="utf-8")
    print(f"已写入：{rel}")


def replace_file(rel: str, func) -> None:
    path = root / rel
    if not path.exists():
        print(f"跳过，文件不存在：{rel}")
        return

    backup(path)
    old = path.read_text(encoding="utf-8")
    new = func(old)

    if new != old:
        path.write_text(new, encoding="utf-8")
        print(f"已更新：{rel}")
    else:
        print(f"未变化：{rel}")


ncl_resources = r'''
from __future__ import annotations


def resource_groups():
    return {
        "ContourPlot": [
            "cnFillOn",
            "cnFillMode",
            "cnLinesOn",
            "cnLineLabelsOn",
            "cnInfoLabelOn",
            "cnLevelSelectionMode",
            "cnMinLevelValF",
            "cnMaxLevelValF",
            "cnLevelSpacingF",
            "cnFillPalette",
            "cnConstantFieldMode",
            "cnConstFLabelOn",
        ],
        "MapPlot": [
            "mpProjection",
            "mpCenterLonF",
            "mpCenterLatF",
            "mpLimitMode",
            "mpMinLonF",
            "mpMaxLonF",
            "mpMinLatF",
            "mpMaxLatF",
            "mpFillOn",
            "mpLandFillColor",
            "mpOceanFillColor",
            "mpOutlineOn",
            "mpNationalLineOn",
            "mpGridAndLimbOn",
            "mpGridLabelsOn",
            "mpGridLonValues",
            "mpGridLatValues",
            "mpGridLonSpacingF",
            "mpGridLatSpacingF",
        ],
        "LabelBar": [
            "lbLabelBarOn",
            "lbOrientation",
            "lbTitleString",
            "lbLabelAutoStride",
            "lbLabelMaxCount",
            "pmLabelBarWidthF",
            "pmLabelBarHeightF",
        ],
        "TickMark": [
            "tmXBOn",
            "tmXTOn",
            "tmYLOn",
            "tmYROn",
            "tmXBLabelsOn",
            "tmXTLabelsOn",
            "tmYLLabelsOn",
            "tmYRLabelsOn",
            "tmLabelClipOn",
            "tmPlainAxisTicksOn",
        ],
        "Panel": [
            "gsnPanelLabelBar",
            "gsnPanelLabelBarSide",
            "gsnPanelLabelBarWidthF",
            "gsnPanelLabelBarHeightF",
            "gsnPanelAutoTickLabels",
            "gsnPanelFigureStrings",
            "gsnPanelMainString",
        ],
        "Titles": [
            "tiMainString",
            "gsnLeftString",
            "gsnCenterString",
            "gsnRightString",
        ],
    }


def print_resource_groups():
    for group, names in resource_groups().items():
        print(f"[{group}]")
        for name in names:
            print(f"  - {name}")
        print()


def projection_aliases():
    return {
        "CylindricalEquidistant": "PlateCarree",
        "PlateCarree": "PlateCarree",
        "Robinson": "Robinson",
        "Mollweide": "Mollweide",
        "Mercator": "Mercator",
        "Orthographic": "Orthographic",
        "NorthPolarStereo": "Stereographic",
        "SouthPolarStereo": "Stereographic",
        "LambertConformal": "LambertConformal",
        "AlbersEqualArea": "AlbersEqualArea",
        "LambertAzimuthalEqualArea": "LambertAzimuthalEqualArea",
        "AzimuthalEquidistant": "AzimuthalEquidistant",
        "TransverseMercator": "TransverseMercator",
        "EqualEarth": "EqualEarth",
        "Sinusoidal": "Sinusoidal",
        "RotatedPole": "RotatedPole",
    }


def print_projection_aliases():
    for key, value in projection_aliases().items():
        print(f"{key} -> {value}")
'''

write_text("src/climara/graphics/_ncl_resources.py", ncl_resources)


demo = r'''
import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    2.8 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.2 * np.sin(np.deg2rad(lat2d * 2.0))
)

base_res = {
    "cnFillOn": True,
    "cnFillMode": "Pcolormesh",
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",

    "mpFillOn": True,
    "mpLandFillColor": "0.96",
    "mpOceanFillColor": "white",
    "mpOutlineOn": True,
    "mpGeophysicalLineColor": "0.25",
    "mpGeophysicalLineThicknessF": 0.8,
    "mpNationalLineOn": True,
    "mpNationalLineColor": "0.5",
    "mpNationalLineThicknessF": 0.25,
    "mpGridAndLimbOn": True,
    "mpGridLineColor": "0.72",
    "mpGridLineThicknessF": 0.35,
    "mpGridLabelsOn": False,

    "lbTitleString": "demo units",
    "lbLabelAutoStride": True,
    "lbLabelMaxCount": 7,
}

cases = [
    (
        "platecarree",
        {
            "mpProjection": "CylindricalEquidistant",
            "mpCenterLonF": 180,
            "mpGridLabelsOn": True,
            "mpGridLonValues": [60, 120, 180, 240, 300],
            "mpGridLatSpacingF": 30,
            "tiMainString": "CylindricalEquidistant",
        },
    ),
    (
        "robinson",
        {
            "mpProjection": "Robinson",
            "mpCenterLonF": 180,
            "tiMainString": "Robinson",
        },
    ),
    (
        "mollweide",
        {
            "mpProjection": "Mollweide",
            "mpCenterLonF": 180,
            "tiMainString": "Mollweide",
        },
    ),
    (
        "orthographic",
        {
            "mpProjection": "Orthographic",
            "mpCenterLonF": 105,
            "mpCenterLatF": 20,
            "tiMainString": "Orthographic",
        },
    ),
    (
        "north_polar_stereo",
        {
            "mpProjection": "NorthPolarStereo",
            "mpCenterLonF": 0,
            "mpMinLatF": 20,
            "mpGridLabelsOn": False,
            "tiMainString": "NorthPolarStereo",
        },
    ),
    (
        "lambert_conformal",
        {
            "mpProjection": "LambertConformal",
            "mpCenterLonF": 105,
            "mpCenterLatF": 35,
            "mpLambertParallel1F": 25,
            "mpLambertParallel2F": 45,
            "mpLimitMode": "LatLon",
            "mpMinLonF": 60,
            "mpMaxLonF": 150,
            "mpMinLatF": 5,
            "mpMaxLatF": 60,
            "mpGridLabelsOn": True,
            "mpGridLonValues": [60, 90, 120, 150],
            "mpGridLatSpacingF": 20,
            "tiMainString": "LambertConformal",
        },
    ),
]

for name, extra in cases:
    res = dict(base_res)
    res.update(extra)

    fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
    filename = f"demo_23_v034_projection_{name}.png"
    fig.savefig(filename, bbox_inches="tight", dpi=220)
    plt.close(fig)
    print(f"已保存：{filename}")
'''

write_text("examples/demo_23_v034_projection_gallery.py", demo)


notes = r'''
# v0.3.4 notes

这个版本是 v0.3.x 这一轮 NCL-style plotting 的小收口版本。

## 主要目的

v0.3.1、v0.3.2、v0.3.3 已经分别补强了：

- Panel、LabelBar、TickMark。
- ContourPlot 高级参数。
- MapPlot、投影和 mp 资源体系。

v0.3.4 不继续堆大功能，而是补两个辅助内容：

- 增加资源分组查询函数。
- 增加投影示例脚本。

## 新增模块

```text
src/climara/graphics/_ncl_resources.py
```

新增公开函数：

```python
from climara.graphics import resource_groups
from climara.graphics import print_resource_groups
from climara.graphics import projection_aliases
from climara.graphics import print_projection_aliases
```

## 新增示例

```text
examples/demo_23_v034_projection_gallery.py
```

这个示例会分别生成这些投影图：

- CylindricalEquidistant
- Robinson
- Mollweide
- Orthographic
- NorthPolarStereo
- LambertConformal
'''

write_text("docs/v0.3.4_notes.md", notes)


init_path = root / "src" / "climara" / "plotting" / "__init__.py"
if init_path.exists():
    backup(init_path)
    init_text = init_path.read_text(encoding="utf-8")
    line = "from ._ncl_resources import print_projection_aliases, print_resource_groups, projection_aliases, resource_groups\n"

    if "from ._ncl_resources import" not in init_text:
        init_text = init_text.rstrip() + "\n" + line
        init_path.write_text(init_text, encoding="utf-8")
        print("已更新：src/climara/graphics/__init__.py")
    else:
        print("未变化：src/climara/graphics/__init__.py")


replace_file(
    "pyproject.toml",
    lambda s: re.sub(r'version\s*=\s*"[^"]+"', 'version = "0.3.4"', s, count=1),
)

write_text("src/climara/_version.py", '__version__ = "0.3.4"\n')

replace_file(
    "README.md",
    lambda s: (
        s.replace("@v0.3.3", "@v0.3.4")
         .replace("@v0.3.2", "@v0.3.4")
         .replace("@v0.3.1", "@v0.3.4")
         .replace("@v0.3.0", "@v0.3.4")
         .replace("@v0.1.0", "@v0.3.4")
         .replace("Current version: `v0.3.3`", "Current version: `v0.3.4`")
         .replace("Current version: `v0.3.2`", "Current version: `v0.3.4`")
         .replace("Current version: `v0.3.1`", "Current version: `v0.3.4`")
         .replace("Current version: `v0.3.0`", "Current version: `v0.3.4`")
         .replace("Current version: `v0.1.0`", "Current version: `v0.3.4`")
    ),
)

replace_file(
    "tests/test_imports.py",
    lambda s: re.sub(r'__version__\s*==\s*"[^"]+"', '__version__ == "0.3.4"', s),
)

replace_file(
    "docs/ncl_resource_compatibility.md",
    lambda s: (
        s
        if "v0.3.4 resource and projection summary" in s
        else s.rstrip() + "\n\n" + notes.replace("# v0.3.4 notes", "## v0.3.4 resource and projection summary") + "\n"
    ),
)

print("开始语法检查...")
subprocess.run([sys.executable, "-m", "compileall", "src", "tests", "examples"], check=True)

print("完成：climara v0.3.4 收口补丁已应用。")
print("下一步运行：python examples/demo_23_v034_projection_gallery.py")
