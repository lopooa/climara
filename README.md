# climara

Climate diagnostics and scientific plotting in Python.

`climara` is being developed as a pure-Python NCL-style scientific plotting layer.  
The goal is not to call NCL, but to learn from NCL's plotting design and translate its ideas into Python.

## Current plotting design

`climara.plotting` currently supports:

- NCL-style resource dictionaries
- `gsn_csm_contour_map`
- `gsn_csm_contour_map_polar`
- `gsn_panel`
- NCL-style labelbar controls
- map projection controls using Cartopy
- contour / pcolormesh fill modes
- overlay layers
- hatching and stippling
- tickmark controls
- workstation-like frame saving
- object-oriented plotting workflow

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
fig.savefig("example.png", bbox_inches="tight")cd /mnt/d/Projects/climara

python - <<'PY'
from pathlib import Path
import re

p = Path("pyproject.toml")
text = p.read_text()
text = re.sub(r'version = ".*?"', 'version = "0.1.0"', text)
p.write_text(text)
PY

cat > src/climara/_version.py <<'EOF'
__version__ = "0.1.0"
