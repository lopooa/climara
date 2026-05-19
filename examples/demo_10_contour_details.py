import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)

lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.5 * np.sin(np.deg2rad(lat2d * 3.0))
    + 0.4 * np.sin(np.deg2rad(lon2d * 8.0))
)

fill_colors = [
    "#08306b",
    "#2171b5",
    "#6baed6",
    "#bdd7e7",
    "#eff3ff",
    "#fff5eb",
    "#fdd0a2",
    "#fdae6b",
    "#f16913",
    "#d94801",
    "#8c2d04",
    "#4d1600",
]

res = {
    "cnFillOn": True,
    "cnFillMode": "Pcolormesh",
    "cnLinesOn": True,
    "cnLineLabelsOn": True,
    "cnLineLabelInterval": 2,
    "cnLineLabelFontHeightF": 7,
    "cnLineLabelBackgroundColor": "white",
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillColors": fill_colors,
    "cnLineColors": ["0.15", "0.25", "0.35"],
    "cnLineThicknesses": [0.4, 0.6, 0.8],
    "cnLineDashPatterns": ["solid", "dashed", "dotted"],
    "cnSmoothingOn": True,
    "cnSmoothingSigmaF": 0.8,
    "cnInfoLabelOn": True,
    "cnInfoLabelJust": "bottom_left",
    "mpProjection": "CylindricalEquidistant",
    "mpGridAndLimbOn": True,
    "mpNationalLineOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "gsnLeftString": "ContourPlot details",
    "gsnCenterString": "v0.2.2",
    "gsnRightString": "line labels",
    "tiMainString": "cnFillColors + cnLineLabels + cnSmoothingOn",
    "tiMainFontHeightF": 14,
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_10_contour_details.png", bbox_inches="tight")
plt.close(fig)

constant = np.ones_like(data) * 2.0

res_const = {
    "cnFillOn": True,
    "cnFillMode": "Pcolormesh",
    "cnLinesOn": True,
    "cnConstFLabelOn": True,
    "cnConstFLabelString": "constant field = 2.0",
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",
    "mpProjection": "CylindricalEquidistant",
    "mpGridAndLimbOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "tiMainString": "cnConstFLabelOn demo",
}

fig, ax, out = gsn_csm_contour_map(constant, lon=lon, lat=lat, res=res_const)
fig.savefig("demo_10_constant_field.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_10_contour_details.png")
print("saved demo_10_constant_field.png")
