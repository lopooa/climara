import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import (
    ncl_style,
    gsn_panel,
    overlay_contour,
    add_hatching,
    overlay_text,
)


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

titles = ["A", "B", "C", "D"]

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
    "gsnPanelMainString": "gsn_panel + overlay demo",
    "gsnPanelLeft": 0.05,
    "gsnPanelRight": 0.95,
    "gsnPanelBottom": 0.15,
    "gsnPanelTop": 0.90,
}

fig, axes, results = gsn_panel(
    data_list,
    lon=lon,
    lat=lat,
    res=res,
    titles=titles,
    ncol=2,
    common_labelbar=True,
)

for ax, data, title in zip(axes, data_list, titles):
    overlay_contour(
        ax,
        data,
        lon=lon,
        lat=lat,
        res={
            "cnLevelSelectionMode": "ExplicitLevels",
            "cnLevels": [-3, -1, 1, 3],
            "cnLineColor": "black",
            "cnLineThicknessF": 0.5,
        },
    )

    mask = np.abs(data) < 1.0

    add_hatching(
        ax,
        mask,
        lon=lon,
        lat=lat,
        res={
            "gsnHatchPattern": "...",
            "gsnHatchColor": "black",
            "gsnHatchAlphaF": 0.5,
            "gsnAddCyclic": True,
        },
    )

    overlay_text(
        ax,
        0,
        30,
        title,
        res={
            "txFontHeightF": 12,
            "txFontColor": "black",
        },
    )

fig.savefig("demo_07_gsn_panel_overlay.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_07_gsn_panel_overlay.png")
