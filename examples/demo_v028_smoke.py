from __future__ import annotations

import numpy as np

from climara.plotting import (
    ContourMapPlot,
    PanelMapPlot,
    ScalarField,
    add_box,
    add_stipple,
    add_text,
    add_vectors,
    gsn_csm_contour_map,
    gsn_csm_contour_map_polar,
    gsn_open_wks,
)


def make_global_data():
    lon = np.linspace(0, 357.5, 144)
    lat = np.linspace(-90, 90, 73)
    lon2d, lat2d = np.meshgrid(lon, lat)

    data = (
        3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
        + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
    )

    return data, lon, lat


def make_regional_data():
    lon = np.linspace(60, 160, 101)
    lat = np.linspace(-10, 55, 66)
    lon2d, lat2d = np.meshgrid(lon, lat)

    data = (
        2.0 * np.sin(np.deg2rad(lon2d * 2.0))
        + 1.5 * np.cos(np.deg2rad(lat2d * 3.0))
    )

    u = np.cos(np.deg2rad(lat2d)) * 5.0
    v = np.sin(np.deg2rad(lon2d)) * 3.0

    return data, u, v, lon, lat


def smoke_contour():
    data, lon, lat = make_global_data()

    wks = gsn_open_wks("png", "v028_smoke_contour", output_dir="outputs/figures")

    res = {
        "gsnLeftString": "climara",
        "gsnRightString": "smoke contour",
        "gsnMaximize": True,
        "gsnFrame": True,

        "cnFillOn": True,
        "cnLinesOn": False,
        "cnFillMode": "Contourf",
        "cnLevelSelectionMode": "ManualLevels",
        "cnMinLevelValF": -5,
        "cnMaxLevelValF": 5,
        "cnLevelSpacingF": 1,
        "cnFillPalette": "BlueWhiteOrangeRed",

        "mpProjection": "Robinson",
        "mpCenterLonF": 180,
        "mpOutlineOn": True,
        "mpGridAndLimbOn": True,

        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
    }

    fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res, wks=wks)

    return out["frame_file"]


def smoke_polar():
    data, lon, lat = make_global_data()

    paths = []

    for hemi in ["NH", "SH"]:
        wks = gsn_open_wks(
            "png",
            f"v028_smoke_polar_{hemi.lower()}",
            output_dir="outputs/figures",
        )

        if hemi == "NH":
            lat_key = "mpMinLatF"
            lat_val = 20
        else:
            lat_key = "mpMaxLatF"
            lat_val = -20

        res = {
            "gsnLeftString": "climara",
            "gsnRightString": f"smoke polar {hemi}",
            "gsnMaximize": True,
            "gsnFrame": True,

            "cnFillOn": True,
            "cnLinesOn": False,
            "cnFillMode": "Contourf",
            "cnLevelSelectionMode": "ManualLevels",
            "cnMinLevelValF": -5,
            "cnMaxLevelValF": 5,
            "cnLevelSpacingF": 1,
            "cnFillPalette": "BlueWhiteOrangeRed",

            "mpCenterLonF": 0,
            lat_key: lat_val,
            "mpGridAndLimbOn": True,
            "mpGridLabelsOn": False,
            "mpPerimOn": True,

            "gsnPolarLabelOn": True,
            "gsnPolarLongitudeLabelsOn": True,
            "gsnPolarLatitudeLabelOn": True,
            "gsnPolarLatitudeLabelYF": 0.025,

            "lbLabelBarOn": True,
            "lbOrientation": "horizontal",
            "pmLabelBarOrthogonalPosF": 0.135,
        }

        fig, ax, out = gsn_csm_contour_map_polar(
            data,
            lon=lon,
            lat=lat,
            res=res,
            hemisphere=hemi,
            wks=wks,
        )

        paths.append(out["frame_file"])

    return paths


def smoke_overlay():
    data, u, v, lon, lat = make_regional_data()

    wks = gsn_open_wks("png", "v028_smoke_overlay", output_dir="outputs/figures")

    res = {
        "gsnLeftString": "climara",
        "gsnRightString": "smoke overlay",
        "gsnMaximize": True,
        "gsnFrame": False,

        "cnFillOn": True,
        "cnLinesOn": False,
        "cnFillMode": "Contourf",
        "cnLevelSelectionMode": "ManualLevels",
        "cnMinLevelValF": -4,
        "cnMaxLevelValF": 4,
        "cnLevelSpacingF": 1,
        "cnFillPalette": "BlueWhiteOrangeRed",

        "mpProjection": "CylindricalEquidistant",
        "mpMinLonF": 60,
        "mpMaxLonF": 160,
        "mpMinLatF": -10,
        "mpMaxLatF": 55,
        "mpDataResolution": "50m",
        "mpOutlineOn": True,
        "mpNationalLineOn": True,
        "mpGridAndLimbOn": True,
        "mpGridLabelsOn": True,

        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "pmLabelBarOrthogonalPosF": 0.13,
    }

    fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res, wks=wks)

    add_stipple(
        ax,
        data > 2.0,
        lon=lon,
        lat=lat,
        res={
            "gsStippleStride": 4,
            "gsStippleColor": "black",
            "gsStippleMarkerSizeF": 5,
            "gsStippleAlphaF": 0.55,
        },
    )

    add_box(
        ax,
        100,
        130,
        10,
        35,
        res={
            "gsLineColor": "black",
            "gsLineThicknessF": 1.6,
            "gsLineDashPattern": 1,
            "gsFillColor": "none",
        },
    )

    add_vectors(
        ax,
        u,
        v,
        lon=lon,
        lat=lat,
        res={
            "vcGlyphStyle": "LineArrow",
            "vcMinDistanceF": 8,
            "vcVectorColor": "black",
            "vcVectorScaleF": 80,
            "vcRefAnnoOn": True,
            "vcRefMagnitudeF": 5,
            "vcRefAnnoString": "5 m/s",
            "vcRefAnnoYF": -0.105,
        },
    )

    add_text(
        ax,
        0.02,
        0.03,
        "smoke overlay",
        res={
            "gsCoordinateMode": "axes",
            "txJust": "BottomLeft",
            "txFontHeightF": 9,
            "txBackgroundFillColor": "white",
            "txPerimOn": True,
        },
    )

    return wks.frame(fig)


def smoke_object_api():
    data, lon, lat = make_global_data()

    fields = [
        ScalarField(data, lon=lon, lat=lat, name="A"),
        ScalarField(data * 0.8, lon=lon, lat=lat, name="B"),
        ScalarField(data * -0.6, lon=lon, lat=lat, name="C"),
        ScalarField(data * 0.4, lon=lon, lat=lat, name="D"),
    ]

    wks = gsn_open_wks("png", "v028_smoke_object_panel", output_dir="outputs/figures")

    res = {
        "gsnPanelMainString": "Smoke object panel",
        "gsnPanelMainFontHeightF": 14,
        "gsnPanelFigureStrings": ["a", "b", "c", "d"],
        "gsnPanelLabelBar": True,
        "gsnMaximize": True,
        "gsnFrame": False,

        "cnFillOn": True,
        "cnLinesOn": False,
        "cnFillMode": "Contourf",
        "cnLevelSelectionMode": "ManualLevels",
        "cnMinLevelValF": -5,
        "cnMaxLevelValF": 5,
        "cnLevelSpacingF": 1,
        "cnFillPalette": "BlueWhiteOrangeRed",

        "mpProjection": "Robinson",
        "mpCenterLonF": 180,
        "mpOutlineOn": True,
        "mpGridAndLimbOn": False,

        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "pmLabelBarOrthogonalPosF": 0.08,
    }

    plot = PanelMapPlot(
        fields,
        res=res,
        titles=["A", "B", "C", "D"],
        ncols=2,
        figsize=(12, 7),
        common_labelbar=True,
        wks=wks,
    )

    fig, axes, out = plot.draw()

    return wks.frame(fig)


def main():
    paths = []

    paths.append(smoke_contour())
    paths.extend(smoke_polar())
    paths.append(smoke_overlay())
    paths.append(smoke_object_api())

    print("Generated smoke figures:")

    for path in paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()
