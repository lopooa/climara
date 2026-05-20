# climara

Climate diagnostics and scientific plotting in Python.

`climara` is a pure-Python NCL-style scientific plotting layer built on Matplotlib, Cartopy, NumPy, and xarray.

The goal is not to call NCL directly, but to learn from NCL's plotting design and translate its ideas into Python.

## Features

`climara.plotting` currently supports:

- NCL-style resource dictionaries
- `gsn_csm_contour_map`
- `gsn_csm_contour_map_polar`
- `gsn_panel`
- NCL-style labelbar controls
- Cartopy map projections
- contour / pcolormesh fill modes
- overlay layers
- hatching and stippling
- tickmark controls
- workstation-like frame saving
- object-oriented plotting workflow

## Installation

Install from GitHub:

```bash
pip install git+https://github.com/lopooa/climara.git@v0.3.5
```

For local development:

```bash
git clone https://github.com/lopooa/climara.git
cd climara
pip install -e .
```

## Basic example

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

    "mpProjection": "CylindricalEquidistant",
    "mpGridAndLimbOn": True,
    "mpGridSpacingF": 30,
    "mpNationalLineOn": True,

    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",

    "tiMainString": "climara NCL-style plot",
    "gsnAddCyclic": True,
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)

fig.savefig("example.png", bbox_inches="tight", dpi=300)
```

## Object-style workflow

```python
from climara.plotting import ScalarField, ContourMapPlot


field = ScalarField(data=data, lon=lon, lat=lat, name="demo_field")

plot = ContourMapPlot(field, res=res)

plot.save("object_example.png")
```

## NCL-style design

| NCL concept | climara concept |
|---|---|
| workstation | `NclWorkstation`, `gsn_open_wks()` |
| resource list | Python dictionary |
| scalarFieldClass | `ScalarField` |
| contourPlotClass | `ContourMapPlot` |
| gsn_csm_contour_map | `gsn_csm_contour_map()` |
| gsn_panel | `gsn_panel()` |
| overlay | `overlay_*()` and `OverlayLayer` |

## Development status

Current version: `v0.3.5`

This package is experimental and under active development.