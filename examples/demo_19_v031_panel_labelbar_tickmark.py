import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_panel


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

base = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
)

data_list = [base, -base, base * 0.5, np.sin(np.deg2rad(lon2d * 3.0))]

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
    "mpGridLonSpacingF": 90,
    "mpGridLatSpacingF": 30,
    "mpGridLineColor": "0.75",
    "mpNationalLineOn": True,
    "tmXBOn": True,
    "tmXTOn": True,
    "tmYLOn": True,
    "tmYROn": True,
    "tmXBLabelFontHeightF": 7,
    "tmYLLabelFontHeightF": 7,
    "tmLabelClipOn": True,
    "lbTitleString": "demo units",
    "lbLabelAutoStride": True,
    "lbLabelMaxCount": 6,
    "gsnPanelMainString": "v0.3.1 panel labelbar and outer tick labels",
    "gsnPanelLeft": 0.06,
    "gsnPanelRight": 0.94,
    "gsnPanelBottom": 0.16,
    "gsnPanelTop": 0.88,
    "gsnPanelXWhiteSpacePercent": 3.0,
    "gsnPanelYWhiteSpacePercent": 5.0,
    "gsnPanelLabelBar": True,
    "gsnPanelLabelBarSide": "Bottom",
    "gsnPanelLabelBarWidthF": 0.58,
    "gsnPanelLabelBarHeightF": 0.025,
    "gsnPanelLabelBarOrthogonalPosF": 0.065,
    "gsnPanelAutoTickLabels": True,
    "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
}

fig, axes, out = gsn_panel(
    data_list,
    lon=lon,
    lat=lat,
    res=res,
    titles=["field", "-field", "half", "wave"],
    ncol=2,
    figsize=(10, 7),
    common_labelbar=True,
)

fig.savefig("demo_19_v031_panel_labelbar_tickmark.png", bbox_inches="tight", dpi=300)
plt.close(fig)

print("saved demo_19_v031_panel_labelbar_tickmark.png")
