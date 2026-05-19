import numpy as np
import matplotlib.pyplot as plt

from climara.plotting import (
    ncl_style,
    gsn_csm_contour_map,
    overlay_contour,
    overlay_vectors,
    overlay_markers,
    overlay_text,
    overlay_polyline,
    overlay_polygon,
    overlay_rectangle,
    add_hatching,
    add_stipple,
)


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
    "mpGridSpacingF": 30,
    "mpNationalLineOn": True,
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "tiMainString": "Overlay / Annotation v0.2.5",
    "gsnAddCyclic": True,
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)

overlay_contour(
    ax,
    data,
    lon=lon,
    lat=lat,
    res={
        "cnLevelSelectionMode": "ExplicitLevels",
        "cnLevels": [-4, -2, 0, 2, 4],
        "cnLineColors": ["0.2", "0.25", "black"],
        "cnLineThicknesses": [0.5, 0.7, 1.0],
        "cnLineDashPatterns": ["dashed", "solid", "dotted"],
        "cnLineLabelsOn": True,
        "cnLineLabelInterval": 1,
        "cnLineLabelFontHeightF": 7,
        "cnLineLabelBackgroundColor": "white",
        "gsnAddCyclic": True,
    },
)

mask_hatch = (lat2d > 20) & (lat2d < 55) & (lon2d > 40) & (lon2d < 120)

add_hatching(
    ax,
    mask_hatch,
    lon=lon,
    lat=lat,
    res={
        "gsnHatchPattern": "/",
        "gsnHatchDensityF": 2,
        "gsnHatchColor": "black",
        "gsnHatchAlphaF": 0.65,
        "gsnAddCyclic": True,
    },
)

mask_stipple = data > 3.0

add_stipple(
    ax,
    mask_stipple,
    lon=lon,
    lat=lat,
    res={
        "gsnStippleMarker": ".",
        "gsnStippleColor": "black",
        "gsnStippleSizeF": 4,
        "gsnStippleAlphaF": 0.7,
        "gsnStippleStride": 5,
    },
)

overlay_markers(
    ax,
    x=[116.4, 139.7, 77.2, 2.35, 264.0],
    y=[39.9, 35.7, 28.6, 48.9, 40.7],
    res={
        "gsMarkerIndex": 4,
        "gsMarkerColor": "yellow",
        "gsMarkerEdgeColor": "black",
        "gsMarkerLineThicknessF": 0.7,
        "gsMarkerSizeF": 70,
    },
)

overlay_text(
    ax,
    116.4,
    45,
    "Beijing",
    res={
        "txFontHeightF": 9,
        "txFontColor": "black",
        "txJust": "BottomCenter",
        "txBackgroundFillColor": "white",
        "txBackgroundAlphaF": 0.75,
    },
)

overlay_polyline(
    ax,
    x=[-160, -120, -80, -40, 0, 40],
    y=[-20, -10, 0, 10, 5, 15],
    res={
        "gsLineColor": "purple",
        "gsLineThicknessF": 2.0,
        "gsLineDashPattern": "dashdot",
        "gsLineAlphaF": 0.9,
    },
)

overlay_polygon(
    ax,
    xy=[
        (70, 5),
        (110, 5),
        (120, 35),
        (80, 35),
    ],
    res={
        "gsFillColor": "none",
        "gsEdgeColor": "limegreen",
        "gsLineThicknessF": 2.0,
        "gsLineDashPattern": "solid",
    },
)

overlay_rectangle(
    ax,
    -130,
    20,
    -60,
    55,
    res={
        "gsFillColor": "none",
        "gsEdgeColor": "black",
        "gsLineThicknessF": 1.5,
        "gsLineDashPattern": "dashed",
    },
)

u = np.cos(np.deg2rad(lat2d)) * 2.0
v = np.sin(np.deg2rad(lon2d)) * 1.5

overlay_vectors(
    ax,
    u,
    v,
    lon=lon,
    lat=lat,
    res={
        "vcMinDistanceF": 8,
        "vcVectorColor": "0.15",
        "vcVectorScaleF": 80,
        "vcLineArrowThicknessF": 0.002,
        "vcRefAnnoOn": True,
        "vcRefMagnitudeF": 2,
        "vcRefAnnoString": "2 units",
        "vcRefAnnoXF": 0.86,
        "vcRefAnnoYF": -0.10,
    },
)

fig.savefig("demo_13_overlay_annotation.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_13_overlay_annotation.png")
