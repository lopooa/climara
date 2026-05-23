import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)

lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.5 * np.sin(np.deg2rad(lat2d * 3.0))
)

res = {
    "cnFillOn": True,
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",
    "cnInfoLabelOn": True,
    "mpProjection": "CylindricalEquidistant",
    "mpGridAndLimbOn": True,
    "mpNationalLineOn": True,
    "mpFillOn": True,
    "mpLandFillColor": "0.92",
    "mpOceanFillColor": "white",
    "mpPerimOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "lbTitlePosition": "bottom",
    "lbBoxLineColor": "0.2",
    "lbBoxLineThicknessF": 0.8,
    "pmLabelBarWidthF": 0.55,
    "pmLabelBarHeightF": 0.025,
    "pmLabelBarOrthogonalPosF": 0.08,
    "gsnLeftString": "Left: dataset",
    "gsnCenterString": "Center: DJF",
    "gsnRightString": "Right: units",
    "gsnStringFontHeightF": 10,
    "gsnStringFontWeight": "bold",
    "gsnStringYF": 1.02,
    "tiMainString": "gsn strings + labelbar position + frame",
    "tiMainYF": 1.10,
    "tiMainFontHeightF": 14,
    "gsnFrame": True,
    "gsnFrameFileName": "demo_08_gsn_strings_frame.png",
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)

plt.close(fig)

print("saved demo_08_gsn_strings_frame.png")
