
import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_csm_contour_map


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    2.5 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 1.5 * np.sin(np.deg2rad(lat2d * 2.0))
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
    "mpDataResolution": "110m",
    "mpFillOn": True,
    "mpLandFillColor": "0.94",
    "mpOceanFillColor": "white",
    "mpOutlineOn": True,
    "mpGeophysicalLineColor": "0.25",
    "mpGeophysicalLineThicknessF": 0.8,
    "mpNationalLineOn": True,
    "mpNationalLineColor": "0.45",
    "mpNationalLineThicknessF": 0.25,
    "mpGridAndLimbOn": True,
    "mpGridLineColor": "0.72",
    "mpGridLineThicknessF": 0.35,
    "mpGridLabelsOn": True,
    "mpGridLabelsAutoOffForCurvedGlobal": True,
    "mpGridLonValues": [60, 120, 180, 240, 300],
    "mpGridLatSpacingF": 30,
    "tmXBLabelFontHeightF": 8,
    "tmYLLabelFontHeightF": 8,
    "lbTitleString": "demo units",
    "lbLabelAutoStride": True,
    "lbLabelMaxCount": 7,
}

cases = [
    (
        "robinson",
        {
            "mpProjection": "Robinson",
            "mpCenterLonF": 180,
            "tiMainString": "v0.3.3 MapPlot: Robinson",
        },
    ),
    (
        "mollweide",
        {
            "mpProjection": "Mollweide",
            "mpCenterLonF": 180,
            "tiMainString": "v0.3.3 MapPlot: Mollweide",
        },
    ),
    (
        "orthographic",
        {
            "mpProjection": "Orthographic",
            "mpCenterLonF": 105,
            "mpCenterLatF": 20,
            "mpGridLabelsOn": False,
            "tiMainString": "v0.3.3 MapPlot: Orthographic",
        },
    ),
    (
        "lambert_azimuthal",
        {
            "mpProjection": "LambertAzimuthalEqualArea",
            "mpCenterLonF": 105,
            "mpCenterLatF": 35,
            "mpLimitMode": "LatLon",
            "mpMinLonF": 60,
            "mpMaxLonF": 150,
            "mpMinLatF": -5,
            "mpMaxLatF": 60,
            "mpGridLonValues": [60, 90, 120, 150],
            "mpGridLatSpacingF": 20,
            "tiMainString": "v0.3.3 MapPlot: Lambert Azimuthal Equal Area",
        },
    ),
]

for name, extra in cases:
    res = dict(base_res)
    res.update(extra)

    fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
    filename = f"demo_22_v033_map_{name}.png"
    fig.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"saved {filename}")
