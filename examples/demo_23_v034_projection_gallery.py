import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    2.8 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.2 * np.sin(np.deg2rad(lat2d * 2.0))
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

    "mpFillOn": True,
    "mpLandFillColor": "0.96",
    "mpOceanFillColor": "white",
    "mpOutlineOn": True,
    "mpGeophysicalLineColor": "0.25",
    "mpGeophysicalLineThicknessF": 0.8,
    "mpNationalLineOn": True,
    "mpNationalLineColor": "0.5",
    "mpNationalLineThicknessF": 0.25,
    "mpGridAndLimbOn": True,
    "mpGridLineColor": "0.72",
    "mpGridLineThicknessF": 0.35,
    "mpGridLabelsOn": False,

    "lbTitleString": "demo units",
    "lbLabelAutoStride": True,
    "lbLabelMaxCount": 7,
}

cases = [
    (
        "platecarree",
        {
            "mpProjection": "CylindricalEquidistant",
            "mpCenterLonF": 180,
            "mpGridLabelsOn": True,
            "mpGridLonValues": [60, 120, 180, 240, 300],
            "mpGridLatSpacingF": 30,
            "tiMainString": "CylindricalEquidistant",
        },
    ),
    (
        "robinson",
        {
            "mpProjection": "Robinson",
            "mpCenterLonF": 180,
            "tiMainString": "Robinson",
        },
    ),
    (
        "mollweide",
        {
            "mpProjection": "Mollweide",
            "mpCenterLonF": 180,
            "tiMainString": "Mollweide",
        },
    ),
    (
        "orthographic",
        {
            "mpProjection": "Orthographic",
            "mpCenterLonF": 105,
            "mpCenterLatF": 20,
            "tiMainString": "Orthographic",
        },
    ),
    (
        "north_polar_stereo",
        {
            "mpProjection": "NorthPolarStereo",
            "mpCenterLonF": 0,
            "mpMinLatF": 20,
            "mpGridLabelsOn": False,
            "tiMainString": "NorthPolarStereo",
        },
    ),
    (
        "lambert_conformal",
        {
            "mpProjection": "LambertConformal",
            "mpCenterLonF": 105,
            "mpCenterLatF": 35,
            "mpLambertParallel1F": 25,
            "mpLambertParallel2F": 45,
            "mpLimitMode": "LatLon",
            "mpMinLonF": 60,
            "mpMaxLonF": 150,
            "mpMinLatF": 5,
            "mpMaxLatF": 60,
            "mpGridLabelsOn": True,
            "mpGridLonValues": [60, 90, 120, 150],
            "mpGridLatSpacingF": 20,
            "tiMainString": "LambertConformal",
        },
    ),
]

for name, extra in cases:
    res = dict(base_res)
    res.update(extra)

    fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
    filename = f"demo_23_v034_projection_{name}.png"
    fig.savefig(filename, bbox_inches="tight", dpi=220)
    plt.close(fig)
    print(f"已保存：{filename}")
