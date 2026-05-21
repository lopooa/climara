from __future__ import annotations

import math
import matplotlib.pyplot as plt

from ._contour import ncl_contour_map
from ._labelbar import add_labelbar
from ._maps import create_projection
from ._resources import bool_resource, split_resources
from ._workflow import apply_gsn_workflow


def _copy_res_without_labelbar(res):
    new_res = dict(res or {})
    new_res["lbLabelBarOn"] = False
    return new_res


def _layout_rects(n, ncols, panel_res):
    nrows = math.ceil(n / ncols)

    left = float(panel_res.get("gsnPanelLeft", 0.06))
    right = float(panel_res.get("gsnPanelRight", 0.96))
    bottom = float(panel_res.get("gsnPanelBottom", 0.14))
    top = float(panel_res.get("gsnPanelTop", 0.92))

    xgap = float(panel_res.get("gsnPanelXGap", 0.035))
    ygap = float(panel_res.get("gsnPanelYGap", 0.055))

    if "gsnPanelXWhiteSpacePercent" in panel_res:
        xgap = (right - left) * float(panel_res["gsnPanelXWhiteSpacePercent"]) / 100.0

    if "gsnPanelYWhiteSpacePercent" in panel_res:
        ygap = (top - bottom) * float(panel_res["gsnPanelYWhiteSpacePercent"]) / 100.0

    width = (right - left - xgap * (ncols - 1)) / ncols
    height = (top - bottom - ygap * (nrows - 1)) / nrows

    rects = []

    for i in range(n):
        row = i // ncols
        col = i % ncols

        x0 = left + col * (width + xgap)
        y0 = top - (row + 1) * height - row * ygap

        rects.append([x0, y0, width, height])

    return rects


def _bounds_from_axes(axes):
    xs0 = []
    ys0 = []
    xs1 = []
    ys1 = []

    for ax in axes:
        pos = ax.get_position()
        xs0.append(pos.x0)
        ys0.append(pos.y0)
        xs1.append(pos.x1)
        ys1.append(pos.y1)

    return min(xs0), min(ys0), max(xs1), max(ys1)


def _normalize_panel_labelbar_side(panel_res, lbres, pmres):
    side = str(
        panel_res.get(
            "gsnPanelLabelBarSide",
            pmres.get("pmLabelBarSide", ""),
        )
    ).lower()

    if side in ["top", "bottom", "left", "right"]:
        return side

    orientation = str(
        panel_res.get(
            "gsnPanelLabelBarOrientation",
            lbres.get("lbOrientation", "horizontal"),
        )
    ).lower()

    if orientation in ["vertical", "v"]:
        return "right"

    return "bottom"


def _normalize_panel_labelbar_orientation(side, panel_res, lbres):
    orientation = str(
        panel_res.get(
            "gsnPanelLabelBarOrientation",
            lbres.get("lbOrientation", ""),
        )
    ).lower()

    if orientation in ["vertical", "v"]:
        return "vertical"

    if orientation in ["horizontal", "h"]:
        return "horizontal"

    if side in ["left", "right"]:
        return "vertical"

    return "horizontal"


def _panel_labelbar_rect(fig, axes, panel_res, lbres, pmres):
    explicit_keys = [
        "gsnPanelLabelBarLeft",
        "gsnPanelLabelBarBottom",
        "gsnPanelLabelBarWidth",
        "gsnPanelLabelBarHeight",
    ]

    if all(key in panel_res for key in explicit_keys):
        return [
            float(panel_res["gsnPanelLabelBarLeft"]),
            float(panel_res["gsnPanelLabelBarBottom"]),
            float(panel_res["gsnPanelLabelBarWidth"]),
            float(panel_res["gsnPanelLabelBarHeight"]),
        ]

    x0, y0, x1, y1 = _bounds_from_axes(axes)
    width_all = x1 - x0
    height_all = y1 - y0

    side = _normalize_panel_labelbar_side(panel_res, lbres, pmres)
    orientation = _normalize_panel_labelbar_orientation(side, panel_res, lbres)

    default_width = width_all * 0.66 if orientation == "horizontal" else 0.025
    default_height = 0.025 if orientation == "horizontal" else height_all * 0.78

    width = float(
        panel_res.get(
            "gsnPanelLabelBarWidthF",
            panel_res.get("gsnPanelLabelBarWidth", pmres.get("pmLabelBarWidthF", default_width)),
        )
    )
    height = float(
        panel_res.get(
            "gsnPanelLabelBarHeightF",
            panel_res.get("gsnPanelLabelBarHeight", pmres.get("pmLabelBarHeightF", default_height)),
        )
    )
    parallel = float(
        panel_res.get(
            "gsnPanelLabelBarParallelPosF",
            pmres.get("pmLabelBarParallelPosF", 0.0),
        )
    )
    orthogonal = float(
        panel_res.get(
            "gsnPanelLabelBarOrthogonalPosF",
            pmres.get("pmLabelBarOrthogonalPosF", 0.06),
        )
    )

    if side in ["top", "bottom"]:
        left = x0 + (width_all - width) / 2 + parallel

        if side == "top":
            bottom = y1 + orthogonal
        else:
            bottom = y0 - orthogonal
    else:
        bottom = y0 + (height_all - height) / 2 + parallel

        if side == "left":
            left = x0 - orthogonal - width
        else:
            left = x1 + orthogonal

    return [left, bottom, width, height]


def _as_float_list(values):
    if values is None:
        return None

    if isinstance(values, str):
        values = values.replace(",", " ").split()

    try:
        return [float(v) for v in values]
    except TypeError:
        return [float(values)]


def _values_from_spacing(vmin, vmax, spacing):
    spacing = float(spacing)

    if spacing <= 0:
        return None

    start = math.ceil(vmin / spacing) * spacing
    values = []
    value = start

    while value <= vmax + spacing * 0.25:
        if value >= vmin - spacing * 0.25:
            values.append(float(value))
        value += spacing

    return values


def _panel_lon_tick_values(res):
    values = _as_float_list(
        res.get(
            "tmXBValues",
            res.get(
                "tmXTValues",
                res.get("mpGridLonValues", None),
            ),
        )
    )

    if values is not None:
        return values

    spacing = res.get("mpGridLonSpacingF", res.get("mpGridSpacingF", None))

    if spacing is None:
        return None

    vmin = float(res.get("mpMinLonF", -180.0))
    vmax = float(res.get("mpMaxLonF", 180.0))

    return _values_from_spacing(vmin, vmax, spacing)


def _drop_nearest_boundary_value(values, side):
    if values is None or len(values) == 0:
        return values

    values = [float(v) for v in values]

    if side == "left":
        target = min(values)
    elif side == "right":
        target = max(values)
    else:
        return values

    return [v for v in values if abs(v - target) > 1e-8]


def _trim_inner_panel_lon_tick_values(res, col, ncols, panel_res):
    if not bool_resource(panel_res, "gsnPanelTrimInnerEdgeLonLabels", True):
        return res

    values = _panel_lon_tick_values(res)

    if values is None:
        return res

    if col > 0:
        values = _drop_nearest_boundary_value(values, "left")

    if col < ncols - 1:
        values = _drop_nearest_boundary_value(values, "right")

    # 这里只裁剪 Cartopy gridliner 的经度标签。
    # 不要写 tmXBValues / tmXTValues，否则 Matplotlib 轴刻度会和
    # Cartopy 经纬度标签同时出现，导致底部标签叠加、顶部 tick 冒出来。
    res["mpGridLonValues"] = values

    return res


def _set_panel_tick_policy(res, i, ncols, nrows, panel_res):
    if not bool_resource(panel_res, "gsnPanelAutoTickLabels", True):
        return res

    row = i // ncols
    col = i % ncols

    left_on = bool_resource(panel_res, "gsnPanelLeftLabelsOn", True) and col == 0
    right_on = bool_resource(panel_res, "gsnPanelRightLabelsOn", False) and col == ncols - 1
    bottom_on = bool_resource(panel_res, "gsnPanelBottomLabelsOn", True) and row == nrows - 1
    top_on = bool_resource(panel_res, "gsnPanelTopLabelsOn", False) and row == 0

    res["tmYLLabelsOn"] = left_on
    res["tmYRLabelsOn"] = right_on
    res["tmXBLabelsOn"] = bottom_on
    res["tmXTLabelsOn"] = top_on

    res["mpGridLeftLabelsOn"] = left_on
    res["mpGridRightLabelsOn"] = right_on
    res["mpGridBottomLabelsOn"] = bottom_on
    res["mpGridTopLabelsOn"] = top_on

    res = _trim_inner_panel_lon_tick_values(res, col, ncols, panel_res)

    return res


def _iter_gridliner_label_artists(gl):
    if gl is None:
        return []

    artists = []

    names = [
        "label_artists",
        "xlabel_artists",
        "ylabel_artists",
        "top_label_artists",
        "bottom_label_artists",
        "left_label_artists",
        "right_label_artists",
    ]

    for name in names:
        obj = getattr(gl, name, None)

        if obj is None:
            continue

        if isinstance(obj, (list, tuple)):
            artists.extend(obj)
        else:
            artists.append(obj)

    unique = []
    seen = set()

    for artist in artists:
        if artist is None:
            continue

        key = id(artist)

        if key in seen:
            continue

        seen.add(key)
        unique.append(artist)

    return unique


def _iter_axis_text_artists(ax):
    artists = []

    for child in ax.get_children():
        if not hasattr(child, "get_text"):
            continue

        try:
            text = child.get_text()
        except Exception:
            continue

        if text:
            artists.append(child)

    return artists


def _hide_panel_inner_edge_ticklabels(fig, axes, ncols, nrows, panel_res, results):
    if not bool_resource(panel_res, "gsnPanelHideInnerEdgeLabels", True):
        return

    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        return

    xpad = float(panel_res.get("gsnPanelInnerEdgeLabelPadF", 0.035))
    ypad = float(panel_res.get("gsnPanelInnerEdgeLabelYPadF", 0.065))

    for i, ax in enumerate(axes):
        row = i // ncols
        col = i % ncols
        pos = ax.get_position()

        result = results[i] if i < len(results) else {}
        gl = None

        if isinstance(result, dict):
            gl = result.get("gridliner", None)

        artists = _iter_gridliner_label_artists(gl)

        if not artists:
            artists = _iter_axis_text_artists(ax)

        for artist in artists:
            if not hasattr(artist, "get_window_extent"):
                continue

            try:
                bbox = artist.get_window_extent(renderer=renderer)
                fbbox = bbox.transformed(fig.transFigure.inverted())
            except Exception:
                continue

            cx = 0.5 * (fbbox.x0 + fbbox.x1)
            cy = 0.5 * (fbbox.y0 + fbbox.y1)

            near_left = abs(cx - pos.x0) <= xpad
            near_right = abs(cx - pos.x1) <= xpad
            near_bottom = cy <= pos.y0 + ypad
            near_top = cy >= pos.y1 - ypad

            is_x_edge_label = near_bottom or near_top

            if col < ncols - 1 and near_right and is_x_edge_label:
                artist.set_visible(False)

            if col > 0 and near_left and is_x_edge_label:
                artist.set_visible(False)

            is_y_edge_label = near_left or near_right

            if row < nrows - 1 and abs(cy - pos.y0) <= ypad and is_y_edge_label:
                artist.set_visible(False)

            if row > 0 and abs(cy - pos.y1) <= ypad and is_y_edge_label:
                artist.set_visible(False)

def _add_panel_figure_strings(fig, axes, panel_res):
    strings = panel_res.get("gsnPanelFigureStrings", None)

    if strings is None:
        return []

    artists = []
    size = float(panel_res.get("gsnPanelFigureStringsFontHeightF", 11))
    color = panel_res.get("gsnPanelFigureStringsFontColor", "black")
    just = str(panel_res.get("gsnPanelFigureStringsJust", "top_left")).lower()
    xoff = float(panel_res.get("gsnPanelFigureStringsXOffset", 0.01))
    yoff = float(panel_res.get("gsnPanelFigureStringsYOffset", 0.01))

    for ax, text in zip(axes, strings):
        pos = ax.get_position()

        if just in ["top_left", "topleft", "left"]:
            x = pos.x0 + xoff
            y = pos.y1 - yoff
            ha = "left"
            va = "top"
        elif just in ["top_right", "topright", "right"]:
            x = pos.x1 - xoff
            y = pos.y1 - yoff
            ha = "right"
            va = "top"
        elif just in ["bottom_left", "bottomleft"]:
            x = pos.x0 + xoff
            y = pos.y0 + yoff
            ha = "left"
            va = "bottom"
        elif just in ["bottom_right", "bottomright"]:
            x = pos.x1 - xoff
            y = pos.y0 + yoff
            ha = "right"
            va = "bottom"
        else:
            x = pos.x0 + xoff
            y = pos.y1 - yoff
            ha = "left"
            va = "top"

        artist = fig.text(
            x,
            y,
            str(text),
            ha=ha,
            va=va,
            fontsize=size,
            color=color,
            fontweight=panel_res.get("gsnPanelFigureStringsFontWeight", "normal"),
            bbox=(
                {
                    "facecolor": panel_res.get("gsnPanelFigureStringsBackgroundColor", "white"),
                    "edgecolor": panel_res.get("gsnPanelFigureStringsPerimColor", "none"),
                    "alpha": float(panel_res.get("gsnPanelFigureStringsBackgroundAlphaF", 0.0)),
                    "pad": float(panel_res.get("gsnPanelFigureStringsBackgroundPadF", 0.2)),
                }
                if bool_resource(panel_res, "gsnPanelFigureStringsBackgroundOn", False)
                else None
            ),
        )
        artists.append(artist)

    return artists


def _add_panel_row_col_titles(fig, axes, ncols, panel_res):
    artists = []

    row_titles = panel_res.get("gsnPanelRowTitles", None)
    col_titles = panel_res.get("gsnPanelColTitles", None)

    if col_titles is not None:
        size = float(panel_res.get("gsnPanelColTitleFontHeightF", 12))

        for col, title in enumerate(col_titles):
            if col >= ncols or col >= len(axes):
                continue

            pos = axes[col].get_position()

            artist = fig.text(
                pos.x0 + pos.width / 2,
                pos.y1 + float(panel_res.get("gsnPanelColTitleOffsetF", 0.035)),
                str(title),
                ha="center",
                va="bottom",
                fontsize=size,
                color=panel_res.get("gsnPanelColTitleFontColor", "black"),
                fontweight=panel_res.get("gsnPanelColTitleFontWeight", "normal"),
            )
            artists.append(artist)

    if row_titles is not None:
        size = float(panel_res.get("gsnPanelRowTitleFontHeightF", 12))
        nrows = math.ceil(len(axes) / ncols)

        for row, title in enumerate(row_titles):
            if row >= nrows:
                continue

            idx = row * ncols

            if idx >= len(axes):
                continue

            pos = axes[idx].get_position()

            artist = fig.text(
                pos.x0 - float(panel_res.get("gsnPanelRowTitleOffsetF", 0.035)),
                pos.y0 + pos.height / 2,
                str(title),
                ha="right",
                va="center",
                rotation=float(panel_res.get("gsnPanelRowTitleAngleF", 90)),
                fontsize=size,
                color=panel_res.get("gsnPanelRowTitleFontColor", "black"),
                fontweight=panel_res.get("gsnPanelRowTitleFontWeight", "normal"),
            )
            artists.append(artist)

    return artists


def ncl_panel_maps(
    data_list,
    lon=None,
    lat=None,
    res=None,
    titles=None,
    ncols=2,
    figsize=None,
    common_labelbar=True,
    wks=None,
):
    groups = split_resources(res)
    panel_res = groups["gsn"]
    mpres = groups["map"]
    tmres = groups["tickmark"]
    lbres = groups["labelbar"]
    pmres = groups["plotmanager"]

    mpres = {**mpres, **tmres}

    n = len(data_list)
    nrows = math.ceil(n / ncols)

    if figsize is None:
        figsize = (4.2 * ncols, 3.6 * nrows)

    fig = plt.figure(figsize=figsize)

    rects = _layout_rects(n, ncols, panel_res)
    axes = []
    results = []

    plot_res = _copy_res_without_labelbar(res)
    plot_res["gsnFrame"] = False


    for i, data in enumerate(data_list):
        projection = create_projection(mpres)
        ax = fig.add_axes(rects[i], projection=projection)

        this_res = dict(plot_res)
        this_res = _set_panel_tick_policy(this_res, i, ncols, nrows, panel_res)

        if titles is not None:
            this_res["tiMainString"] = titles[i]

        fig, ax, result = ncl_contour_map(
            data,
            lon=lon,
            lat=lat,
            res=this_res,
            fig=fig,
            ax=ax,
        )

        axes.append(ax)
        results.append(result)

    cbar = None

    if common_labelbar and bool_resource(panel_res, "gsnPanelLabelBar", True):
        first_mappable = None

        for result in results:
            if result["mappable"] is not None:
                first_mappable = result["mappable"]
                break

        if first_mappable is not None:
            side = _normalize_panel_labelbar_side(panel_res, lbres, pmres)
            orientation = _normalize_panel_labelbar_orientation(side, panel_res, lbres)
            cax = fig.add_axes(_panel_labelbar_rect(fig, axes, panel_res, lbres, pmres))

            panel_lbres = dict(lbres)
            panel_lbres["lbLabelBarOn"] = True
            panel_lbres.setdefault("lbOrientation", orientation)
            panel_lbres.setdefault("lbLabelAutoStride", True)

            if side in ["top", "bottom"]:
                panel_lbres.setdefault("lbLabelPosition", "bottom" if side == "bottom" else "top")
            else:
                panel_lbres.setdefault("lbLabelPosition", "right" if side == "right" else "left")

            if "gsnPanelLabelBarLabelFontHeightF" in panel_res:
                panel_lbres["lbLabelFontHeightF"] = panel_res["gsnPanelLabelBarLabelFontHeightF"]

            if "gsnPanelLabelBarTitleString" in panel_res:
                panel_lbres["lbTitleString"] = panel_res["gsnPanelLabelBarTitleString"]

            cbar = add_labelbar(fig, axes[-1], first_mappable, panel_lbres, cax=cax, pmres=pmres)

    figure_string_artists = _add_panel_figure_strings(fig, axes, panel_res)
    title_artists = _add_panel_row_col_titles(fig, axes, ncols, panel_res)

    if "gsnPanelMainString" in panel_res:
        fig.suptitle(
            panel_res["gsnPanelMainString"],
            fontsize=float(panel_res.get("gsnPanelMainFontHeightF", 13)),
            y=float(panel_res.get("gsnPanelMainYF", 0.98)),
        )

    out = {
        "panel_results": results,
        "colorbar": cbar,
        "figure_string_artists": figure_string_artists,
        "title_artists": title_artists,
        "groups": groups,
    }

    fig, _, out = apply_gsn_workflow(
        fig,
        ax=None,
        out=out,
        gsnres=panel_res,
        wks=wks,
    )

    return fig, axes, out
