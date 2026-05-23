import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map, overlay_contour, overlay_markers, overlay_text, overlay_polyline

ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)
data = 4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))

res = {
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "BlWhRe",
    "mpGridAndLimbOn": True,
    "lbTitleString": "demo units",
    "tiMainString": "overlays",
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)

overlay_contour(
    ax,
    data,
    lon=lon,
    lat=lat,
    res={
        "cnLevelSelectionMode": "ExplicitLevels",
        "cnLevels": [-3, -1, 1, 3],
        "cnLineColor": "black",
        "cnLineThicknessF": 0.6,
    },
)

overlay_markers(ax, [0, 80, 160], [0, 30, -20], res={"gsMarkerIndex": "x", "gsMarkerSizeF": 50})
overlay_text(ax, 0, 60, "text", res={"txFontHeightF": 12})
overlay_polyline(ax, [-100, 100], [20, 20], res={"gsLineColor": "black", "gsLineThicknessF": 1.5})

fig.savefig("demo_03_overlay.png", bbox_inches="tight")
plt.close(fig)
print("saved demo_03_overlay.png")
