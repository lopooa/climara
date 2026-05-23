import numpy as np
import matplotlib

matplotlib.use("Agg")

from climara import __version__
from climara.graphics import (
    ncl_style,
    gsn_csm_contour_map,
    ScalarField,
    ContourMapPlot,
    export_resource_compatibility,
)


ncl_style()

lon = np.linspace(0, 357.5, 72)
lat = np.linspace(-90, 90, 37)
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
    "mpGridSpacingF": 60,
    "mpNationalLineOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "tiMainString": f"climara smoke test v{__version__}",
    "gsnAddCyclic": True,
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_18_v030_smoke_function.png", bbox_inches="tight")

field = ScalarField(data=data, lon=lon, lat=lat, name="smoke")
plot = ContourMapPlot(field, res=res)
plot.save("demo_18_v030_smoke_object.png")

export_resource_compatibility()

print(f"climara version: {__version__}")
print("saved demo_18_v030_smoke_function.png")
print("saved demo_18_v030_smoke_object.png")
print("updated docs/ncl_resource_compatibility.md")
