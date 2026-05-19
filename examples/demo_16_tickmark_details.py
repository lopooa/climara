import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_csm_contour_map, gsn_panel


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
    "mpGridLabelsOn": True,
    "mpGridLonSpacingF": 60,
    "mpGridLatSpacingF": 30,
    "mpGridLineColor": "0.65",
    "mpGridLineDashPattern": "--",
    "mpNationalLineOn": True,
    "tmXBOn": True,
    "tmXTOn": False,
    "tmYLOn": True,
    "tmYROn": False,
    "tmXBLabelFontHeightF": 9,
    "tmYLLabelFontHeightF": 9,
    "tmXBLabelFontColor": "0.1",
    "tmYLLabelFontColor": "0.1",
    "tmXBLabelAngleF": 0,
    "tmYLLabelAngleF": 0,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "tiMainString": "TickMark: bottom/left labels only",
    "gsnAddCyclic": True,
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_16_tickmark_single.png", bbox_inches="tight")
plt.close(fig)

data_list = [data, -data, data * 0.5, np.sin(np.deg2rad(lon2d * 4.0))]

panel_res = {
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
    "mpGridLabelsOn": True,
    "mpGridLonSpacingF": 90,
    "mpGridLatSpacingF": 30,
    "mpGridLineColor": "0.75",
    "mpNationalLineOn": True,
    "tmXBOn": True,
    "tmXTOn": False,
    "tmYLOn": True,
    "tmYROn": False,
    "tmXBLabelFontHeightF": 7,
    "tmYLLabelFontHeightF": 7,
    "lbTitleString": "demo units",
    "gsnPanelMainString": "TickMark: panel label control",
    "gsnPanelLeft": 0.06,
    "gsnPanelRight": 0.96,
    "gsnPanelBottom": 0.15,
    "gsnPanelTop": 0.88,
    "gsnPanelLabelBar": True,
    "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
}

fig, axes, out = gsn_panel(
    data_list,
    lon=lon,
    lat=lat,
    res=panel_res,
    titles=["field", "-field", "half", "wave"],
    ncol=2,
    figsize=(10, 7),
    common_labelbar=True,
)

fig.savefig("demo_16_tickmark_panel.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_16_tickmark_single.png")
print("saved demo_16_tickmark_panel.png")
