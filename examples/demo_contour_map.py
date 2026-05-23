import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, ncl_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)

lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.5 * np.sin(np.deg2rad(lat2d * 3.0))
)

res = {
    "cnFillOn": True,
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",
    "mpProjection": "CylindricalEquidistant",
    "mpCenterLonF": 0,
    "mpGridAndLimbOn": True,
    "mpNationalLineOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "tiMainString": "NCL-style contour map in Python",
    "gsnAddCyclic": True,
}

fig, ax, out = ncl_contour_map(data, lon=lon, lat=lat, res=res)

fig.savefig("demo_contour_map.png", bbox_inches="tight")
plt.show()
