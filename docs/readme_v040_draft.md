# climara

`climara` 是一个面向 **气候诊断** 和 **地学数据科学绘图** 的 Python 第三方库。

它借鉴 NCL 简洁高效的资源字典式绘图方式，尝试把常用的 NCL-style plotting 工作流迁移到 Python 生态中，让用户可以用更接近 NCL 的方式，在 Python 中完成等值线图、地图图、多图 panel、共享色标、tick label 控制和投影绘图。

当前项目仍处于早期开发阶段，API 可能继续调整，但已经具备一套基础的 NCL-style 绘图接口。

---

## 项目定位

`climara` 主要面向以下场景：

- 气候诊断图绘制。
- 地学数据科学可视化。
- NCL 绘图脚本向 Python 迁移。
- xarray / numpy 数据的快速地图绘图。
- IPCC-style 或论文风格的多面板图绘制。
- 字典式资源参数控制绘图细节。

它不是要完整复制 NCL，也不是要替代 Matplotlib / Cartopy，而是希望在 Python 生态中提供一个更接近 NCL 使用体验的绘图封装。

---

## 当前重点

当前版本重点是 **NCL-style plotting**。

目前已经初步支持：

- 字典式资源调用。
- 对象式绘图流程。
- 等值线填色图。
- pcolormesh 填色图。
- 等值线标签。
- info label。
- 常数场安全处理。
- 地图投影。
- 地理边界。
- 经纬网。
- Panel 多图布局。
- 共享 labelbar。
- 外侧 tick labels。
- figure strings。
- 常见 NCL-style 资源名。

---

## 示例图

### Panel / LabelBar / TickMark

![panel labelbar tickmark](docs/assets/panel_labelbar_tickmark.png)

这个示例展示：

- 多图 panel 布局。
- 共享 labelbar。
- 外侧 tick labels。
- figure strings。
- panel 内部 tick label 自动隐藏。

### ContourPlot with line labels

![contour line labels](docs/assets/contour_line_labels.png)

这个示例展示：

- 填色图。
- 等值线。
- 等值线标签。
- info label。
- 手动 contour levels。

### Constant field fallback

![constant field](docs/assets/contour_constant_field.png)

这个示例展示常数场的安全回退处理。

### Robinson projection

![projection robinson](docs/assets/projection_robinson.png)

### Orthographic projection

![projection orthographic](docs/assets/projection_orthographic.png)

更多示例见：

```text
docs/gallery/index.md
```

---

## 安装

当前建议使用本地开发安装方式：

```bash
git clone https://github.com/lopooa/climara.git
cd climara
python -m pip install -e .
```

如果你正在开发源码，建议使用 editable mode，这样修改 `src/climara` 中的代码后，不需要反复重新安装。

---

## 主要依赖

核心绘图依赖包括：

```text
numpy
matplotlib
cartopy
```

部分数据处理或示例可能会用到：

```text
xarray
netCDF4
```

如果你使用 conda / mamba 环境，建议优先通过 conda-forge 安装 Cartopy 相关依赖。

---

## 快速开始：NCL-style 字典式绘图

下面是一个最小示例。

```python
import numpy as np

from climara.plotting import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)

lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
)

res = {
    "cnFillOn": True,
    "cnFillMode": "Pcolormesh",
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",

    "mpProjection": "Robinson",
    "mpCenterLonF": 180,
    "mpOutlineOn": True,
    "mpNationalLineOn": True,
    "mpGridAndLimbOn": True,

    "lbTitleString": "demo units",
    "tiMainString": "climara quick start",
}

fig, ax, out = gsn_csm_contour_map(
    data,
    lon=lon,
    lat=lat,
    res=res,
)

fig.savefig("quick_start.png", dpi=300, bbox_inches="tight")
```

---

## 对象式绘图流程

除了 NCL-style 字典式调用，`climara` 也支持对象式绘图流程。

```python
from climara.plotting import ScalarField, ContourMapPlot


field = ScalarField(
    data=data,
    lon=lon,
    lat=lat,
    name="demo_field",
)

plot = ContourMapPlot(field, res=res)
plot.save("object_example.png")
```

字典式接口适合从 NCL 脚本迁移，或者快速复现 NCL-style plotting。

对象式接口适合更 Pythonic 的项目组织方式。

---

## NCL-style resources

`climara` 的核心设计之一是使用类似 NCL 的资源字典控制绘图行为。

例如：

```python
res = {
    "cnFillOn": True,
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,

    "mpProjection": "Robinson",
    "mpCenterLonF": 180,
    "mpGridAndLimbOn": True,

    "lbTitleString": "units",
}
```

这些资源名并不是完整复刻 NCL，而是尽量保留 NCL 用户熟悉的命名方式，同时映射到 Matplotlib / Cartopy 的绘图逻辑。

---

## 查看当前支持的资源

可以使用下面的函数查看当前支持的资源分组和投影别名：

```python
from climara.plotting import print_resource_groups
from climara.plotting import print_projection_aliases


print_resource_groups()
print_projection_aliases()
```

也可以直接获取字典：

```python
from climara.plotting import resource_groups
from climara.plotting import projection_aliases


groups = resource_groups()
aliases = projection_aliases()
```

---

## ContourPlot

当前 `ContourPlot` 重点支持填色图和等值线图。

### 常用资源

```text
cnFillOn
cnFillMode
cnLinesOn
cnLineLabelsOn
cnInfoLabelOn
cnLevelSelectionMode
cnMinLevelValF
cnMaxLevelValF
cnLevelSpacingF
cnFillPalette
cnConstantFieldMode
cnConstFLabelOn
```

### 示例

```python
res = {
    "cnFillOn": True,
    "cnFillMode": "Auto",
    "cnLinesOn": True,
    "cnLineLabelsOn": True,
    "cnLineLabelInterval": 2,
    "cnLineLabelFontHeightF": 7,

    "cnInfoLabelOn": True,

    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
}
```

### 当前支持内容

- 手动 levels。
- 自动 levels。
- `contourf` 风格填色。
- `pcolormesh` 风格填色。
- `Auto` fallback。
- 等值线。
- 等值线标签。
- info label。
- 常数场 fallback。

---

## MapPlot

当前 `MapPlot` 基于 Cartopy 实现。

### 常用资源

```text
mpProjection
mpCenterLonF
mpCenterLatF
mpLimitMode
mpMinLonF
mpMaxLonF
mpMinLatF
mpMaxLatF
mpFillOn
mpLandFillColor
mpOceanFillColor
mpOutlineOn
mpNationalLineOn
mpGridAndLimbOn
mpGridLabelsOn
mpGridLonValues
mpGridLatValues
mpGridLonSpacingF
mpGridLatSpacingF
```

### 投影示例

```python
res = {
    "mpProjection": "Robinson",
    "mpCenterLonF": 180,
    "mpOutlineOn": True,
    "mpGridAndLimbOn": True,
}
```

区域图示例：

```python
res = {
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
}
```

### 当前支持的投影别名

当前支持或部分支持的投影名包括：

```text
CylindricalEquidistant
PlateCarree
Robinson
Mollweide
Mercator
Orthographic
NorthPolarStereo
SouthPolarStereo
LambertConformal
AlbersEqualArea
LambertAzimuthalEqualArea
AzimuthalEquidistant
TransverseMercator
EqualEarth
Sinusoidal
RotatedPole
```

实际可用性取决于本地安装的 Cartopy 版本。

---

## Panel / LabelBar / TickMark

`climara` 提供了基础的 panel 绘图能力，适合绘制多张地图组成的气候诊断图。

### 常用 Panel 资源

```text
gsnPanelLabelBar
gsnPanelLabelBarSide
gsnPanelLabelBarWidthF
gsnPanelLabelBarHeightF
gsnPanelLabelBarOrthogonalPosF
gsnPanelLabelBarParallelPosF
gsnPanelAutoTickLabels
gsnPanelFigureStrings
gsnPanelMainString
```

### 常用 LabelBar 资源

```text
lbLabelBarOn
lbOrientation
lbTitleString
lbLabelAutoStride
lbLabelMaxCount
pmLabelBarWidthF
pmLabelBarHeightF
```

### 常用 TickMark 资源

```text
tmXBOn
tmXTOn
tmYLOn
tmYROn
tmXBLabelsOn
tmXTLabelsOn
tmYLLabelsOn
tmYRLabelsOn
tmLabelClipOn
tmPlainAxisTicksOn
```

### Panel 示例

```python
from climara.plotting import gsn_panel


fig, axes, out = gsn_panel(
    data_list,
    lon=lon,
    lat=lat,
    res=res,
    titles=["field", "-field", "half", "wave"],
    ncol=2,
    figsize=(10, 7),
    common_labelbar=True,
)
```

---

## 示例脚本

当前重要示例包括：

```text
examples/demo_19_v031_panel_labelbar_tickmark.py
examples/demo_20_v032_contour_advanced.py
examples/demo_22_v033_mapplot_resources.py
examples/demo_23_v034_projection_gallery.py
```

运行示例：

```bash
python examples/demo_23_v034_projection_gallery.py
```

---

## 文档和 gallery

示例图片整理在：

```text
docs/assets/
```

gallery 文档：

```text
docs/gallery/index.md
```

版本说明：

```text
docs/v0.3.1_notes.md
docs/v0.3.2_notes.md
docs/v0.3.3_notes.md
docs/v0.3.4_notes.md
docs/v0.3.5_notes.md
docs/v0.4.0_notes.md
```

---

## 当前开发阶段

当前路线：

```text
v0.3.1  Panel / LabelBar / TickMark
v0.3.2  ContourPlot 高级参数
v0.3.3  MapPlot / Projection / mp 资源体系
v0.3.4  资源查询和投影示例
v0.3.5  cleanup 和稳定
v0.4.0  文档展示准备
```

`v0.4.0` 是文档展示和发布准备阶段，不等于马上发布 PyPI。

---

## 设计思路

`climara` 当前的设计思路是：

1. 尽量保留 NCL 用户熟悉的资源名。
2. 使用 Python 字典承载绘图参数。
3. 底层基于 Matplotlib 和 Cartopy。
4. 同时保留对象式接口，便于 Python 项目化使用。
5. 优先服务气候诊断和地学数据绘图。
6. 在可控范围内逐步增强，而不是一次性追求完整复刻 NCL。

---

## 与 NCL 的关系

`climara` 受到 NCL 绘图思想启发，但不是 NCL 的绑定或封装。

它不会调用 NCL，也不依赖 NCL。

它的目标是在 Python 生态中提供一种类似 NCL 的绘图体验。

---

## 与 Matplotlib / Cartopy 的关系

`climara` 并不替代 Matplotlib 和 Cartopy。

它更像是一个面向气候绘图的上层封装：

- Matplotlib 负责底层绘图。
- Cartopy 负责地图投影和地理要素。
- climara 负责提供 NCL-style 资源接口和气候绘图常用布局。

---

## 状态说明

当前项目仍处于早期开发阶段。

推荐使用场景：

- 本地实验。
- 气候绘图原型开发。
- NCL 脚本迁移探索。
- Python 绘图接口设计实验。

暂不建议在不检查输出图像的情况下直接用于正式业务生产环境。

---

## 反馈

欢迎试用，bug 和建议都欢迎反馈。

GitHub:

```text
https://github.com/lopooa/climara
```

---

## License

See the repository license file.
