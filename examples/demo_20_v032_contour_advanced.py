import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.6 * np.sin(np.deg2rad(lat2d * 2.0))
)

res = {
    "cnFillOn": True,
    "cnFillMode": "Auto",
    "cnLinesOn": True,
    "cnLineLabelsOn": True,
    "cnLineLabelInterval": 2,
    "cnLineLabelFontHeightF": 7,
    "cnLineColor": "0.15",
    "cnLineThicknessF": 0.45,
    "cnInfoLabelOn": True,
    "mpGridLonValues": [60, 120, 180, 240, 300],
    "cnInfoLabelFontHeightF": 7,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",
    "mpProjection": "Robinson",
    "mpCenterLonF": 180,
    "mpGridAndLimbOn": True,
    "mpGridLabelsOn": False,
    "mpGridLonSpacingF": 60,
    "mpGridLatSpacingF": 30,
    "mpGridLineColor": "0.75",
    "mpNationalLineOn": True,
    "lbTitleString": "demo units",
    "lbLabelAutoStride": True,
    "lbLabelMaxCount": 7,
    "tiMainString": "v0.3.2 ContourPlot: fill, line labels, info label",
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_20_v032_contour_line_labels.png", bbox_inches="tight", dpi=300)
plt.close(fig)

constant = np.ones_like(data) * 2.0

res_const = dict(res)
res_const.update(
    {
        "tiMainString": "v0.3.2 ContourPlot: constant field fallback",
        "cnLinesOn": True,
        "cnLineLabelsOn": True,
        "cnInfoLabelOn": True,
        "cnConstFLabelOn": True,
        "cnConstFLabelString": "constant field",
        "cnFillMode": "Auto",
    }
)

fig, ax, out = gsn_csm_contour_map(constant, lon=lon, lat=lat, res=res_const)
fig.savefig("demo_21_v032_contour_constant_field.png", bbox_inches="tight", dpi=300)
plt.close(fig)

print("saved demo_20_v032_contour_line_labels.png")
print("saved demo_21_v032_contour_constant_field.png")
