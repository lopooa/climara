import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, ncl_panel_maps


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(20, 90, 57)

lon2d, lat2d = np.meshgrid(lon, lat)

base = np.cos(np.deg2rad(lat2d)) * np.sin(np.deg2rad(lon2d * 2.0))

data_list = [
    5.0 * base,
    -4.0 * base,
    3.5 * np.cos(np.deg2rad(lon2d)) * np.sin(np.deg2rad(lat2d)),
    4.5 * np.sin(np.deg2rad(lon2d * 3.0)) * np.cos(np.deg2rad(lat2d)),
]

titles = [
    "Panel A",
    "Panel B",
    "Panel C",
    "Panel D",
]

res = {
    "cnFillOn": True,
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",
    "mpProjection": "Stereographic",
    "mpCenterLonF": 0,
    "mpCenterLatF": 90,
    "mpMinLatF": 20,
    "mpGridAndLimbOn": True,
    "mpNationalLineOn": False,
    "gsnAddCyclic": True,
    "gsnPanelMainString": "NCL-style polar panel in Python",
    "gsnPanelLeft": 0.05,
    "gsnPanelRight": 0.95,
    "gsnPanelBottom": 0.15,
    "gsnPanelTop": 0.90,
}

fig, axes, out = ncl_panel_maps(
    data_list,
    lon=lon,
    lat=lat,
    res=res,
    titles=titles,
    ncols=2,
    common_labelbar=True,
)

fig.savefig("demo_polar_panel.png", bbox_inches="tight")
plt.show()
