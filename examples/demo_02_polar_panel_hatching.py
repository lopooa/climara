import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_panel, add_hatching

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

res = {
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "BlueWhiteOrangeRed",
    "mpProjection": "Stereographic",
    "mpCenterLonF": 0,
    "mpCenterLatF": 90,
    "mpMinLatF": 20,
    "mpGridAndLimbOn": True,
    "gsnPanelMainString": "polar panel + hatching",
    "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
}

fig, axes, results = gsn_panel(data_list, lon=lon, lat=lat, res=res, titles=["A", "B", "C", "D"], ncol=2)

for ax, data in zip(axes, data_list):
    add_hatching(
        ax,
        np.abs(data) < 1.0,
        lon=lon,
        lat=lat,
        res={
            "gsnHatchPattern": "...",
            "gsnHatchColor": "black",
            "gsnHatchAlphaF": 0.6,
        },
    )

fig.savefig("demo_02_polar_panel_hatching.png", bbox_inches="tight")
plt.close(fig)
print("saved demo_02_polar_panel_hatching.png")
