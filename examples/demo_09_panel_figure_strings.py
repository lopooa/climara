import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_panel


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

titles = ["NAM", "NAO", "SAM", "PNA"]

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
    "mpPerimOn": False,
    "lbTitleString": "demo units",
    "gsnPanelMainString": "gsn_panel figure strings / row-col titles",
    "gsnPanelMainFontHeightF": 14,
    "gsnPanelLeft": 0.07,
    "gsnPanelRight": 0.95,
    "gsnPanelBottom": 0.16,
    "gsnPanelTop": 0.87,
    "gsnPanelXWhiteSpacePercent": 4,
    "gsnPanelYWhiteSpacePercent": 6,
    "gsnPanelLabelBar": True,
    "gsnPanelLabelBarLeft": 0.25,
    "gsnPanelLabelBarBottom": 0.07,
    "gsnPanelLabelBarWidth": 0.50,
    "gsnPanelLabelBarHeight": 0.025,
    "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
    "gsnPanelFigureStringsJust": "top_left",
    "gsnPanelFigureStringsFontHeightF": 12,
    "gsnPanelFigureStringsFontWeight": "bold",
    "gsnPanelColTitles": ["Column 1", "Column 2"],
    "gsnPanelRowTitles": ["Row 1", "Row 2"],
}

fig, axes, out = gsn_panel(
    data_list,
    lon=lon,
    lat=lat,
    res=res,
    titles=titles,
    ncol=2,
    common_labelbar=True,
)

fig.savefig("demo_09_panel_figure_strings.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_09_panel_figure_strings.png")
