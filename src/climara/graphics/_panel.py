from __future__ import annotations

import math
import matplotlib.pyplot as plt

from ._contour import ncl_contour_map
from ._labelbar import add_labelbar
from ._labelbar_object import build_hlu_labelbar
from ._render_mpl import render_ndc_primitives_mpl
from ._maps import create_projection
from ._panel_layout import compute_gsn_panel_layout
from ._resources import bool_resource, split_resources
from ._view import HluView
from ._text_item import HluTextItem
from ._workflow import apply_gsn_workflow


def _copy_res_without_labelbar(res):
    new_res = dict(res or {})
    new_res["lbLabelBarOn"] = False
    return new_res


def _as_int_list(values):
    if values is None:
        return None

    if isinstance(values, str):
        values = values.replace(",", " ").split()

    try:
        return [int(v) for v in values]
    except TypeError:
        return [int(values)]


def _panel_row_counts(n, ncols, panel_res):
    ncols = max(1, int(ncols))

    use_row_spec = bool_resource(panel_res, "gsnPanelRowSpec", False)

    raw = panel_res.get(
        "gsnPanelRows",
        panel_res.get(
            "gsnPanelRowSpecValues",
            panel_res.get("gsnPanelRowCounts", None),
        ),
    )

    if use_row_spec and raw is not None:
        counts = _as_int_list(raw)
        counts = [max(1, int(v)) for v in counts]

        total = sum(counts)

        if total < n:
            base = max(counts) if counts else ncols
            remaining = n - total

            while remaining > 0:
                value = min(base, remaining)
                counts.append(value)
                remaining -= value

        return counts, True

    counts = []
    remaining = n

    while remaining > 0:
        value = min(ncols, remaining)
        counts.append(value)
        remaining -= value

    return counts, False


def _panel_layout_info(n, ncols, panel_res, plot_res=None, common_labelbar=True):
    """Return NCL-style panel layout information.

    The layout calculation lives in _panel_layout.py and is backend independent.
    This wrapper preserves the existing _panel.py return shape while moving
    the layout policy away from Matplotlib.
    """
    return compute_gsn_panel_layout(
        nplots=n,
        ncols=ncols,
        panel_res=panel_res,
        plot_res=plot_res,
        common_labelbar=common_labelbar,
    )


def _layout_rects(n, ncols, panel_res):
    return _panel_layout_info(n, ncols, panel_res)["rects"]

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
            bottom = y0 - orthogonal - height
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


def _set_panel_tick_policy(res, i, ncols, nrows, panel_res, layout_info=None):
    if layout_info is not None:
        row = layout_info["rows"][i]
        col = layout_info["cols"][i]
        row_ncols = layout_info["row_counts"][row]
        nrows = layout_info["nrows"]
    else:
        row = i // ncols
        col = i % ncols
        row_ncols = ncols

    # Panel maps use compact label defaults.
    # By default, hide map/grid/polar coordinate labels in panel plots.
    # Users can explicitly enable them with:
    #   gsnPanelMapLabelsOn = True
    if not bool_resource(panel_res, "gsnPanelMapLabelsOn", False):
        res["tmYLLabelsOn"] = False
        res["tmYRLabelsOn"] = False
        res["tmXBLabelsOn"] = False
        res["tmXTLabelsOn"] = False

        res["mpGridLabelsOn"] = False
        res["mpGridLeftLabelsOn"] = False
        res["mpGridRightLabelsOn"] = False
        res["mpGridBottomLabelsOn"] = False
        res["mpGridTopLabelsOn"] = False

        res["gsnPolarLabelOn"] = False
        res["gsnPolarLongitudeLabelsOn"] = False
        res["gsnPolarLatitudeLabelOn"] = False

        return res

    if not bool_resource(panel_res, "gsnPanelAutoTickLabels", True):
        return res

    res.setdefault("mpGridLabelsOn", True)
    res.setdefault("gsnPolarLabelOn", True)
    res.setdefault("gsnPolarLongitudeLabelsOn", True)
    res.setdefault("gsnPolarLatitudeLabelOn", True)

    left_on = bool_resource(panel_res, "gsnPanelLeftLabelsOn", True) and col == 0
    right_on = bool_resource(panel_res, "gsnPanelRightLabelsOn", False) and col == row_ncols - 1
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

    res = _trim_inner_panel_lon_tick_values(res, col, row_ncols, panel_res)

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

def _panel_text_just_to_mpl(just):
    just = str(just).replace("-", "_").replace(" ", "_").lower()

    if "left" in just:
        ha = "left"
    elif "right" in just:
        ha = "right"
    else:
        ha = "center"

    if "top" in just:
        va = "top"
    elif "bottom" in just:
        va = "bottom"
    else:
        va = "center"

    return ha, va


def _panel_font_height_to_mpl_points(value):
    value = float(value)

    if 0.0 < value < 1.0:
        return value * 1000.0

    return value


def _draw_panel_text_item_mpl(fig, item, bbox=None):
    """Temporary renderer bridge for panel-level HLU TextItem objects."""
    ha, va = _panel_text_just_to_mpl(item.txJust)

    return fig.text(
        item.txPosXF,
        item.txPosYF,
        item.txString,
        ha=ha,
        va=va,
        fontsize=_panel_font_height_to_mpl_points(item.txFontHeightF),
        color=item.txFontColor,
        rotation=item.txAngleF,
        fontweight=item.resources.get("txFontWeight", item.resources.get("fontweight", "normal")),
        bbox=bbox,
    )


def _make_panel_text_item(
    text,
    x,
    y,
    just,
    font_height,
    color="black",
    angle=0.0,
    name=None,
    resources=None,
):
    return HluTextItem(
        txString=str(text),
        txPosXF=float(x),
        txPosYF=float(y),
        txJust=str(just),
        txFontHeightF=float(font_height),
        txFontColor=color,
        txAngleF=float(angle),
        coord_system="ndc",
        name=name,
        resources=dict(resources or {}),
    )


def _add_panel_figure_strings(fig, axes, panel_res, return_items=False):
    strings = panel_res.get("gsnPanelFigureStrings", None)

    if strings is None:
        if return_items:
            return [], []
        return []

    artists = []
    items = []

    size = float(panel_res.get("gsnPanelFigureStringsFontHeightF", 11))
    color = panel_res.get("gsnPanelFigureStringsFontColor", "black")
    just = str(panel_res.get("gsnPanelFigureStringsJust", "top_left")).lower()
    xoff = float(panel_res.get("gsnPanelFigureStringsXOffset", 0.01))
    yoff = float(panel_res.get("gsnPanelFigureStringsYOffset", 0.01))

    for ax, text_value in zip(axes, strings):
        pos = ax.get_position()

        if just in ["top_left", "topleft", "left"]:
            x = pos.x0 + xoff
            y = pos.y1 - yoff
            txjust = "top_left"
        elif just in ["top_right", "topright", "right"]:
            x = pos.x1 - xoff
            y = pos.y1 - yoff
            txjust = "top_right"
        elif just in ["bottom_left", "bottomleft"]:
            x = pos.x0 + xoff
            y = pos.y0 + yoff
            txjust = "bottom_left"
        elif just in ["bottom_right", "bottomright"]:
            x = pos.x1 - xoff
            y = pos.y0 + yoff
            txjust = "bottom_right"
        else:
            x = pos.x0 + xoff
            y = pos.y1 - yoff
            txjust = "top_left"

        resources = {
            "fontweight": panel_res.get("gsnPanelFigureStringsFontWeight", "normal"),
            "source": "gsnPanelFigureStrings",
        }

        item = _make_panel_text_item(
            text_value,
            x,
            y,
            txjust,
            size,
            color=color,
            name="gsnPanelFigureString",
            resources=resources,
        )

        bbox = None

        if bool_resource(panel_res, "gsnPanelFigureStringsBackgroundOn", False):
            bbox = {
                "facecolor": panel_res.get("gsnPanelFigureStringsBackgroundColor", "white"),
                "edgecolor": panel_res.get("gsnPanelFigureStringsPerimColor", "none"),
                "alpha": float(panel_res.get("gsnPanelFigureStringsBackgroundAlphaF", 0.0)),
                "pad": float(panel_res.get("gsnPanelFigureStringsBackgroundPadF", 0.2)),
            }

        artist = _draw_panel_text_item_mpl(fig, item, bbox=bbox)

        artists.append(artist)
        items.append(item)

    if return_items:
        return artists, items

    return artists



def _add_panel_row_col_titles(fig, axes, ncols, panel_res, return_items=False):
    artists = []
    items = []

    row_titles = panel_res.get("gsnPanelRowTitles", None)
    col_titles = panel_res.get("gsnPanelColTitles", None)

    if col_titles is not None:
        size = float(panel_res.get("gsnPanelColTitleFontHeightF", 12))

        for col, title in enumerate(col_titles):
            if col >= ncols or col >= len(axes):
                continue

            pos = axes[col].get_position()

            item = _make_panel_text_item(
                title,
                pos.x0 + pos.width / 2,
                pos.y1 + float(panel_res.get("gsnPanelColTitleOffsetF", 0.035)),
                "bottom_center",
                size,
                color=panel_res.get("gsnPanelColTitleFontColor", "black"),
                name="gsnPanelColTitle",
                resources={
                    "fontweight": panel_res.get("gsnPanelColTitleFontWeight", "normal"),
                    "source": "gsnPanelColTitles",
                },
            )

            artist = _draw_panel_text_item_mpl(fig, item)

            artists.append(artist)
            items.append(item)

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

            item = _make_panel_text_item(
                title,
                pos.x0 - float(panel_res.get("gsnPanelRowTitleOffsetF", 0.035)),
                pos.y0 + pos.height / 2,
                "center_right",
                size,
                color=panel_res.get("gsnPanelRowTitleFontColor", "black"),
                angle=float(panel_res.get("gsnPanelRowTitleAngleF", 90)),
                name="gsnPanelRowTitle",
                resources={
                    "fontweight": panel_res.get("gsnPanelRowTitleFontWeight", "normal"),
                    "source": "gsnPanelRowTitles",
                },
            )

            artist = _draw_panel_text_item_mpl(fig, item)

            artists.append(artist)
            items.append(item)

    if return_items:
        return artists, items

    return artists




def _as_panel_sequence(value, n, name):
    if value is None:
        return None

    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a number or a sequence of numbers")

    try:
        values = list(value)
    except TypeError:
        values = [value] * n

    if len(values) != n:
        raise ValueError(f"{name} must have length {n}, got {len(values)}")

    return [float(v) for v in values]


def _apply_manual_panel_positions(rects, panel_res):
    """Apply NCL-style gsnPanelXF / gsnPanelYF manual viewport positions.

    In NCL, vpXF and vpYF describe the upper-left corner of a plot viewport.
    Matplotlib add_axes uses [left, bottom, width, height], so y is converted
    with bottom = vpYF - height.
    """
    n = len(rects)
    x_values = _as_panel_sequence(panel_res.get("gsnPanelXF"), n, "gsnPanelXF")
    y_values = _as_panel_sequence(panel_res.get("gsnPanelYF"), n, "gsnPanelYF")

    if x_values is None and y_values is None:
        return rects

    new_rects = []

    for i, rect in enumerate(rects):
        left, bottom, width, height = rect

        if x_values is not None:
            left = x_values[i]

        if y_values is not None:
            bottom = y_values[i] - height

        new_rects.append([left, bottom, width, height])

    return new_rects


def _print_panel_debug(rects, layout_info, panel_res):
    """Print NCL-style panel viewport diagnostics."""
    if not bool(panel_res.get("gsnPanelDebug", False)):
        return

    print("")
    print("climara.graphics gsn_panel debug")
    print("--------------------------------")
    print(f"nplots : {len(rects)}")
    print(f"nrows  : {layout_info.get('nrows')}")
    print(f"ncols  : {layout_info.get('ncols')}")

    for key in [
        "gsnPanelTop",
        "gsnPanelBottom",
        "gsnPanelLeft",
        "gsnPanelRight",
        "gsnPanelXWhiteSpacePercent",
        "gsnPanelYWhiteSpacePercent",
        "gsnPanelXGap",
        "gsnPanelYGap",
    ]:
        if key in panel_res:
            print(f"{key}: {panel_res[key]}")

    print("")
    print("plot viewport positions")
    print("index  left/vpXF   top/vpYF    width       height      bottom")
    print("-----  ---------   --------    -----       ------      ------")

    for i, rect in enumerate(rects):
        left, bottom, width, height = rect
        top = bottom + height

        print(
            f"{i:>5}  "
            f"{left:>9.4f}   "
            f"{top:>8.4f}    "
            f"{width:>7.4f}     "
            f"{height:>7.4f}     "
            f"{bottom:>7.4f}"
        )

    print("")



def _apply_panel_map_label_defaults(res):
    """Return panel-map resources.

    Coordinate label policy is applied later by _set_panel_tick_policy().
    This keeps the default-off behavior for panel maps, while still allowing
    users to re-enable labels with gsnPanelMapLabelsOn=True.
    """
    return res

def _labelbar_view_from_rect(rect):
    """Convert [left, bottom, width, height] to an HLU-style View."""
    left, bottom, width, height = rect

    return HluView(
        vpXF=float(left),
        vpYF=float(bottom + height),
        vpWidthF=float(width),
        vpHeightF=float(height),
    )


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
    panel_res_list=None,
):
    groups = split_resources(res)
    panel_res = groups["gsn"]
    mpres = groups["map"]
    tmres = groups["tickmark"]
    lbres = groups["labelbar"]
    pmres = groups["plotmanager"]

    mpres = {**mpres, **tmres}

    n = len(data_list)

    # gsn_panel layout needs both gsnPanel* and pmLabelBar* resources.
    # split_resources() separates them into panel_res and pmres, but NCL's
    # gsn_panel sees them together through the panel resource list.
    layout_panel_res = {
        **panel_res,
        **pmres,
    }

    # Some labelbar orientation/style resources can also affect the panel
    # labelbar placement policy.
    for key in [
        "lbOrientation",
        "lbLabelPosition",
        "lbTitlePosition",
    ]:
        if key in lbres:
            layout_panel_res[key] = lbres[key]

    if not common_labelbar:
        layout_panel_res["gsnPanelLabelBar"] = False

    # NCL-style panel layout is computed before any backend axes are created.
    # The returned rects are only used as a temporary Matplotlib bridge.
    layout_info = _panel_layout_info(
        n,
        ncols,
        layout_panel_res,
        plot_res=res,
        common_labelbar=common_labelbar,
    )
    rects = layout_info["rects"]
    ncols = layout_info["ncols"]
    nrows = layout_info["nrows"]

    # gsnPanelXF / gsnPanelYF are handled by compute_gsn_panel_layout().
    layout_info = {**layout_info, "rects": rects}

    _print_panel_debug(rects, layout_info, panel_res)

    if figsize is not None:
        fig = plt.figure(figsize=figsize)
    elif hasattr(wks, "figure"):
        fig = wks.figure()
    else:
        figsize = (4.2 * ncols, 3.6 * nrows)
        fig = plt.figure(figsize=figsize)

    axes = []
    results = []

    plot_res = _copy_res_without_labelbar(res)
    plot_res["gsnFrame"] = False
    plot_res = _apply_panel_map_label_defaults(plot_res)

    if panel_res_list is None:
        panel_res_list = [None] * n

    if len(panel_res_list) != n:
        raise ValueError(
            "panel_res_list must have the same length as data_list "
            f"({len(panel_res_list)} != {n})"
        )

    for i, data in enumerate(data_list):
        this_res = dict(plot_res)

        panel_specific_res = panel_res_list[i]

        if panel_specific_res is not None:
            this_res.update(_copy_res_without_labelbar(panel_specific_res))
            this_res["gsnFrame"] = False
            this_res = _apply_panel_map_label_defaults(this_res)

        this_groups = split_resources(this_res)
        this_mpres = {
            **this_groups["map"],
            **this_groups["tickmark"],
        }

        projection = create_projection(this_mpres)
        ax = fig.add_axes(rects[i], projection=projection)

        this_res = _set_panel_tick_policy(
            this_res,
            i,
            ncols,
            nrows,
            panel_res,
            layout_info=layout_info,
        )

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
    labelbar_object = None
    labelbar_primitives = []
    labelbar_artists = []

    if common_labelbar and bool_resource(panel_res, "gsnPanelLabelBar", True):
        first_mappable = None

        for result in results:
            if result["mappable"] is not None:
                first_mappable = result["mappable"]
                break

        if first_mappable is not None:
            side = _normalize_panel_labelbar_side(panel_res, lbres, pmres)
            orientation = _normalize_panel_labelbar_orientation(side, panel_res, lbres)
            labelbar_rect = layout_info.get("labelbar_rect")

            if labelbar_rect is None:
                labelbar_rect = _panel_labelbar_rect(fig, axes, panel_res, lbres, pmres)

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

            labelbar_view = _labelbar_view_from_rect(labelbar_rect)

            labelbar_object = build_hlu_labelbar(
                view=labelbar_view,
                mappable=first_mappable,
                lbres=panel_lbres,
                pmres=pmres,
            )
            labelbar_primitives = list(labelbar_object.primitives)
            labelbar_artists = render_ndc_primitives_mpl(fig, labelbar_primitives)

            # Keep the old output key useful while the renderer is being refactored.
            cbar = labelbar_object


    figure_string_artists, figure_string_items = _add_panel_figure_strings(
        fig,
        axes,
        panel_res,
        return_items=True,
    )
    title_artists, title_items = _add_panel_row_col_titles(
        fig,
        axes,
        ncols,
        panel_res,
        return_items=True,
    )

    main_title_artist = None
    main_title_item = None

    if "gsnPanelMainString" in panel_res:
        main_title_item = _make_panel_text_item(
            panel_res["gsnPanelMainString"],
            0.5,
            float(panel_res.get("gsnPanelMainYF", 0.98)),
            "top_center",
            float(panel_res.get("gsnPanelMainFontHeightF", 13)),
            color=panel_res.get("gsnPanelMainFontColor", "black"),
            name="gsnPanelMainString",
            resources={
                "fontweight": panel_res.get("gsnPanelMainFontWeight", "normal"),
                "source": "gsnPanelMainString",
            },
        )
        main_title_artist = _draw_panel_text_item_mpl(fig, main_title_item)

    panel_text_items = [
        *figure_string_items,
        *title_items,
    ]

    if main_title_item is not None:
        panel_text_items.append(main_title_item)

    out = {
        "panel_results": results,
        "colorbar": cbar,
        "labelbar_object": labelbar_object,
        "labelbar_primitives": labelbar_primitives,
        "labelbar_artists": labelbar_artists,
        "figure_string_artists": figure_string_artists,
        "figure_string_items": figure_string_items,
        "title_artists": title_artists,
        "title_items": title_items,
        "main_title_artist": main_title_artist,
        "main_title_item": main_title_item,
        "panel_text_items": panel_text_items,
        "panel_layout": layout_info,
        "panel_res_list": panel_res_list,
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
