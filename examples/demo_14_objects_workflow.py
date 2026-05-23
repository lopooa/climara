import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import (
    ncl_style,
    ScalarField,
    ContourMapPlot,
    PanelMapPlot,
)


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
)

field = ScalarField(
    data=data,
    lon=lon,
    lat=lat,
    name="demo_field",
    attrs={"units": "demo units"},
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
    "tiMainString": "Object workflow: ContourMapPlot",
    "gsnAddCyclic": True,
}

plot = ContourMapPlot(field, res=res)

plot.add_contour(
    res={
        "cnLevelSelectionMode": "ExplicitLevels",
        "cnLevels": [-4, -2, 0, 2, 4],
        "cnLineColor": "black",
        "cnLineThicknessF": 0.6,
        "cnLineDashPattern": "dashed",
        "cnLineLabelsOn": True,
        "cnLineLabelInterval": 1,
        "cnLineLabelFontHeightF": 7,
        "cnLineLabelBackgroundColor": "white",
    }
)

plot.add_hatching(
    mask=(data > 3.0),
    res={
        "gsnHatchPattern": "/",
        "gsnHatchDensityF": 2,
        "gsnHatchColor": "black",
        "gsnHatchAlphaF": 0.6,
        "gsnAddCyclic": True,
    },
)

plot.add_markers(
    x=[116.4, 139.7, 2.35],
    y=[39.9, 35.7, 48.9],
    res={
        "gsMarkerIndex": 4,
        "gsMarkerColor": "yellow",
        "gsMarkerEdgeColor": "black",
        "gsMarkerSizeF": 80,
        "gsMarkerLineThicknessF": 0.7,
    },
)

plot.add_text(
    116.4,
    45,
    "Beijing",
    res={
        "txFontHeightF": 9,
        "txJust": "BottomCenter",
        "txBackgroundFillColor": "white",
        "txBackgroundAlphaF": 0.75,
    },
)

plot.add_rectangle(
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

plot.save("demo_14_object_contour_map.png")

fields = [
    field,
    ScalarField(data=-data, lon=lon, lat=lat, name="negative"),
    ScalarField(data=data * 0.5, lon=lon, lat=lat, name="half"),
    ScalarField(data=np.sin(np.deg2rad(lon2d * 4.0)), lon=lon, lat=lat, name="wave"),
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
    "gsnPanelMainString": "Object workflow: PanelMapPlot",
    "gsnPanelLeft": 0.06,
    "gsnPanelRight": 0.96,
    "gsnPanelBottom": 0.15,
    "gsnPanelTop": 0.88,
    "gsnPanelLabelBar": True,
    "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
    "gsnPanelFigureStringsFontHeightF": 11,
}

panel = PanelMapPlot(
    fields=fields,
    res=panel_res,
    titles=["field", "-field", "half", "wave"],
    ncol=2,
    common_labelbar=True,
)

panel.save("demo_14_object_panel_map.png", figsize=(10, 7))

print("saved demo_14_object_contour_map.png")
print("saved demo_14_object_panel_map.png")
