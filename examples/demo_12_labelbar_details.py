import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
)

base_res = {
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
    "mpNationalLineOn": True,
    "gsnAddCyclic": True,
}

res = dict(base_res)
res.update(
    {
        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "lbTitleString": "custom labels on top",
        "lbTitlePosition": "top",
        "lbTitleFontHeightF": 11,
        "lbTitleFontWeight": "bold",
        "lbTitleOffsetF": 8,
        "lbLabelPositions": [-4, -2, 0, 2, 4],
        "lbLabelStrings": ["cold", "-2", "zero", "2", "warm"],
        "lbLabelFontHeightF": 9,
        "lbLabelFontColor": "0.1",
        "lbBoxLinesOn": True,
        "lbBoxLineColor": "0.15",
        "lbBoxLineThicknessF": 1.0,
        "lbBoxSeparatorLineThicknessF": 0.4,
        "lbTickLengthF": 5,
        "lbTickThicknessF": 0.8,
        "pmLabelBarSide": "Bottom",
        "pmLabelBarWidthF": 0.55,
        "pmLabelBarHeightF": 0.03,
        "pmLabelBarOrthogonalPosF": 0.13,
        "tiMainString": "LabelBar: custom strings / title on top",
    }
)

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_12_labelbar_horizontal.png", bbox_inches="tight")
plt.close(fig)

res = dict(base_res)
res.update(
    {
        "lbLabelBarOn": True,
        "lbOrientation": "vertical",
        "lbTitleString": "vertical units",
        "lbTitlePosition": "right",
        "lbTitleFontHeightF": 11,
        "lbLabelStride": 2,
        "lbLabelAngleF": 0,
        "lbLabelFontHeightF": 9,
        "lbBoxLinesOn": True,
        "lbBoxLineColor": "0.2",
        "lbBoxLineThicknessF": 1.0,
        "lbBoxSeparatorLineThicknessF": 0.3,
        "pmLabelBarSide": "Right",
        "pmLabelBarWidthF": 0.025,
        "pmLabelBarHeightF": 0.55,
        "pmLabelBarOrthogonalPosF": 0.035,
        "pmLabelBarParallelPosF": 0.0,
        "tiMainString": "LabelBar: vertical right side",
    }
)

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_12_labelbar_vertical.png", bbox_inches="tight")
plt.close(fig)

res = dict(base_res)
res.update(
    {
        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "lbTitleString": "top labelbar",
        "lbTitlePosition": "top",
        "lbLabelPosition": "top",
        "lbLabelStride": 2,
        "lbTickMarksOn": True,
        "lbBoxLinesOn": False,
        "pmLabelBarSide": "Top",
        "pmLabelBarWidthF": 0.50,
        "pmLabelBarHeightF": 0.025,
        "pmLabelBarOrthogonalPosF": 0.075,
        "tiMainString": "LabelBar: top side / no box lines",
        "tiMainYF": 1.03,
    }
)

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_12_labelbar_top.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_12_labelbar_horizontal.png")
print("saved demo_12_labelbar_vertical.png")
print("saved demo_12_labelbar_top.png")
