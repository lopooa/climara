import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import (
    ncl_style,
    gsn_open_wks,
    gsn_csm_contour_map,
    gsn_panel,
)


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
)

wks = gsn_open_wks(
    "png",
    "demo_15_workstation",
    output_dir=".",
    dpi=300,
    close_after_frame=True,
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
    "mpGridSpacingF": 30,
    "mpNationalLineOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "tiMainString": "NCL-style workstation: frame 1",
    "gsnAddCyclic": True,
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
path1 = wks.frame(fig)

data_list = [
    data,
    -data,
    data * 0.5,
    np.sin(np.deg2rad(lon2d * 4.0)),
]

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
    "mpGridSpacingF": 60,
    "mpNationalLineOn": True,
    "lbTitleString": "demo units",
    "gsnPanelMainString": "NCL-style workstation: frame 2",
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

path2 = wks.frame(fig)

print(f"saved {path1}")
print(f"saved {path2}")
