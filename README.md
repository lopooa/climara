# climara

`climara` is an experimental Python package for climate diagnostics and geoscience plotting.

It is inspired by the concise, resource-based plotting style of NCL, and aims to bring a similar plotting workflow to the Python ecosystem.

The package currently supports both dictionary-style plotting resources and object-oriented plotting workflows.

## Features

- NCL-style resource dictionaries
- Contour and filled-contour plotting
- Map plotting based on Cartopy
- Multiple map projections
- Panel plots and shared labelbars
- Tick label control
- Object-oriented plotting workflow

## Installation

For local development:

```bash
git clone https://github.com/lopooa/climara.git
cd climara
python -m pip install -e .
```

Main dependencies include:

```text
numpy
matplotlib
cartopy
```

## Quick start

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
    "mpGridAndLimbOn": True,

    "lbTitleString": "demo units",
    "tiMainString": "climara example",
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("example.png", dpi=300, bbox_inches="tight")
```

## Object-oriented workflow

```python
from climara.plotting import ScalarField, ContourMapPlot


field = ScalarField(data=data, lon=lon, lat=lat, name="demo_field")

plot = ContourMapPlot(field, res=res)
plot.save("object_example.png")
```

## Examples

Example scripts are available in:

```text
examples/
```

Useful examples include:

```text
examples/demo_19_v031_panel_labelbar_tickmark.py
examples/demo_20_v032_contour_advanced.py
examples/demo_22_v033_mapplot_resources.py
examples/demo_23_v034_projection_gallery.py
```

## Status

`climara` is still experimental and under active development. APIs may change before a stable release.

Bug reports, suggestions, and examples are welcome.

## License

See the repository license file.

Current version: `v0.1.1`
