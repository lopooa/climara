from __future__ import annotations

import math

from ._contour import ncl_contour_map
from ._panel import ncl_panel_maps


def _copy_res(res):
    if res is None:
        return {}

    return dict(res)


def _apply_defaults(res, defaults):
    out = _copy_res(res)

    for key, value in defaults.items():
        out.setdefault(key, value)

    return out


def gsn_csm_contour_map(data, lon=None, lat=None, res=None, fig=None, ax=None, wks=None):
    defaults = {
        "cnFillOn": True,
        "cnLinesOn": False,
        "cnLineLabelsOn": False,
        "cnFillPalette": "viridis",
        "mpProjection": "CylindricalEquidistant",
        "mpCenterLonF": 0,
        "mpOutlineOn": True,
        "mpGridAndLimbOn": False,
        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "pmLabelBarOrthogonalPosF": 0.135,
        "gsnAddCyclic": True,
        "gsnDraw": True,
        "gsnFrame": False,
    }

    final_res = _apply_defaults(res, defaults)

    return ncl_contour_map(
        data,
        lon=lon,
        lat=lat,
        res=final_res,
        fig=fig,
        ax=ax,
        wks=wks,
    )


def gsn_csm_contour_map_polar(
    data,
    lon=None,
    lat=None,
    res=None,
    hemisphere=None,
    fig=None,
    ax=None,
    wks=None,
):
    final_res = _copy_res(res)

    if hemisphere is None:
        if float(final_res.get("mpCenterLatF", 90)) < 0:
            hemisphere = "SH"
        else:
            hemisphere = "NH"

    hemisphere = hemisphere.upper()

    base_defaults = {
        "mpProjection": "Stereographic",
        "mpCenterLonF": 0,
        "mpOutlineOn": True,
        "mpGridAndLimbOn": True,
        "mpGridLineColor": "0.65",
        "mpGridLineThicknessF": 0.4,
        "mpGridLineDashPattern": "--",
        "mpPerimOn": True,
        "mpPolarBoundaryOn": True,
        "cnFillOn": True,
        "cnLinesOn": False,
        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "gsnAddCyclic": True,
        "gsnDraw": True,
        "gsnFrame": False,
        "gsnPolar": True,
        "gsnPolarLabelOn": True,
        "gsnPolarLabelDistance": 1.08,
        "gsnPolarLabelFontHeightF": 9.0,
        "gsnPolarLongitudeLabelsOn": True,
        "gsnPolarLatitudeLabelOn": True,
        "gsnPolarLatitudeLabelPosition": "inside_bottom",
        "gsnPolarClampBottomLabelsOn": True,
        "gsnPolarBottomLabelYF": 0.025,
        "mpPolarHideRectangularFrameOn": True,
    }

    if hemisphere == "SH":
        defaults = {
            **base_defaults,
            "mpCenterLatF": -90,
            "mpMaxLatF": -20,
            "gsnPolarLatitudeLabelString": "20°S",
        }
    else:
        defaults = {
            **base_defaults,
            "mpCenterLatF": 90,
            "mpMinLatF": 20,
            "gsnPolarLatitudeLabelString": "20°N",
        }

    final_res = _apply_defaults(final_res, defaults)

    return ncl_contour_map(
        data,
        lon=lon,
        lat=lat,
        res=final_res,
        fig=fig,
        ax=ax,
        wks=wks,
    )


def gsn_panel(
    data_list,
    lon=None,
    lat=None,
    res=None,
    titles=None,
    nrow=None,
    ncol=None,
    figsize=None,
    common_labelbar=True,
    wks=None,
    panel_res_list=None,
):
    if ncol is None:
        if nrow is not None:
            ncol = math.ceil(len(data_list) / nrow)
        else:
            ncol = 2

    return ncl_panel_maps(
        data_list,
        lon=lon,
        lat=lat,
        res=res,
        titles=titles,
        ncols=ncol,
        figsize=figsize,
        common_labelbar=common_labelbar,
        wks=wks,
        panel_res_list=panel_res_list,
    )


gsn_panel_maps = gsn_panel
