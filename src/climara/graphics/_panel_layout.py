from __future__ import annotations

from ._resources import bool_resource
from ._view import HluView, HluBoundingBox


def _as_int_list(values):
    if values is None:
        return None

    if isinstance(values, str):
        values = values.replace(",", " ").split()

    try:
        return [int(v) for v in values]
    except TypeError:
        return [int(values)]


def _as_float_sequence(values, n, name):
    if values is None:
        return None

    if isinstance(values, str):
        values = values.replace(",", " ").split()

    try:
        out = list(values)
    except TypeError:
        out = [values] * n

    if len(out) != n:
        raise ValueError(f"{name} must have length {n}, got {len(out)}")

    return [float(v) for v in out]


def _panel_row_counts(nplots, ncols, panel_res):
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

        if total < nplots:
            base = max(counts) if counts else ncols
            remaining = nplots - total

            while remaining > 0:
                value = min(base, remaining)
                counts.append(value)
                remaining -= value

        return counts, True

    counts = []
    remaining = nplots

    while remaining > 0:
        value = min(ncols, remaining)
        counts.append(value)
        remaining -= value

    return counts, False


def _is_polar_like_plot(plot_res):
    plot_res = dict(plot_res or {})

    if bool_resource(plot_res, "gsnPolar", False):
        return True

    projection = str(plot_res.get("mpProjection", "")).lower()

    if "stereo" in projection:
        return True

    return False


def _default_reference_view(plot_res, page_aspect=1.0):
    """Return the reference HLU View used by gsn_panel layout.

    NCL's gsn_csm_contour_map_polar creates a polar plot whose original
    viewport is typically:

        vpWidthF  = 0.62
        vpHeightF = 0.62

    This is visible in gsnPanelDebug output as:

        orig wdt,hgt = 0.62,0.62

    The page aspect is intentionally not used here. NCL panel layout works
    from HLU View and BoundingBox resources, not from a backend canvas size.
    """
    plot_res = dict(plot_res or {})

    if _is_polar_like_plot(plot_res):
        default_size = 0.62
    else:
        default_size = 1.0

    vp_width = float(plot_res.get("vpWidthF", default_size))
    vp_height = float(plot_res.get("vpHeightF", default_size))

    return HluView(
        vpXF=float(plot_res.get("vpXF", 0.0)),
        vpYF=float(plot_res.get("vpYF", 1.0)),
        vpWidthF=vp_width,
        vpHeightF=vp_height,
    )


def _reference_bounding_box_from_view(view, plot_res):
    """Return an NCL-like plot bounding box for panel layout.

    NCL gsn_panel uses plot bounding boxes, not only viewport rectangles.
    For polar map panels with gsnCenterString titles, the bounding box is
    slightly larger than the viewport, especially above the plot.

    The default values below are calibrated from NCL gsnPanelDebug output for
    gsn_csm_contour_map_polar:

        orig viewport: 0.62 x 0.62
        effective bbox width  ≈ 0.64513
        effective bbox height ≈ 0.692455
    """
    plot_res = dict(plot_res or {})

    if _is_polar_like_plot(plot_res):
        left_pad = float(plot_res.get("gsnPanelReferenceBBLeftPadF", 0.012565))
        right_pad = float(plot_res.get("gsnPanelReferenceBBRightPadF", 0.012565))
        top_pad = float(plot_res.get("gsnPanelReferenceBBTopPadF", 0.060000))
        bottom_pad = float(plot_res.get("gsnPanelReferenceBBBottomPadF", 0.012455))
    else:
        left_pad = float(plot_res.get("gsnPanelReferenceBBLeftPadF", 0.0))
        right_pad = float(plot_res.get("gsnPanelReferenceBBRightPadF", 0.0))
        top_pad = float(plot_res.get("gsnPanelReferenceBBTopPadF", 0.0))
        bottom_pad = float(plot_res.get("gsnPanelReferenceBBBottomPadF", 0.0))

    return HluBoundingBox(
        top=view.top + top_pad,
        bottom=view.bottom - bottom_pad,
        left=view.left - left_pad,
        right=view.right + right_pad,
    )

def _clip_panel_region(left, right, bottom, top):
    left = max(0.0, min(1.0, float(left)))
    right = max(0.0, min(1.0, float(right)))
    bottom = max(0.0, min(1.0, float(bottom)))
    top = max(0.0, min(1.0, float(top)))

    if right <= left:
        raise ValueError("gsnPanelRight must be greater than gsnPanelLeft")

    if top <= bottom:
        raise ValueError("gsnPanelTop must be greater than gsnPanelBottom")

    return left, right, bottom, top


def compute_gsn_panel_layout(
    nplots,
    ncols=2,
    panel_res=None,
    plot_res=None,
    common_labelbar=True,
):
    """Compute a backend-independent NCL-style gsn_panel layout.

    This function is backend-neutral.

    The returned HluView objects are the authoritative layout result.
    The rects describe backend-neutral panel viewports.
    """

    panel_res = dict(panel_res or {})
    nplots = int(nplots)

    row_counts, row_spec = _panel_row_counts(nplots, ncols, panel_res)

    if not row_counts:
        return {
            "views": [],
            "rects": [],
            "rows": [],
            "cols": [],
            "row_counts": [],
            "ncols": max(1, int(ncols)),
            "nrows": 0,
            "row_spec": row_spec,
            "labelbar_view": None,
            "labelbar_rect": None,
        }

    slot_cols = max(row_counts) if row_spec else max(1, int(ncols))
    nrows = len(row_counts)

    x_lft = float(panel_res.get("gsnPanelLeft", 0.0))
    x_rgt = float(panel_res.get("gsnPanelRight", 1.0))
    y_bot = float(panel_res.get("gsnPanelBottom", 0.0))
    y_top = float(panel_res.get("gsnPanelTop", 1.0))
    x_lft, x_rgt, y_bot, y_top = _clip_panel_region(x_lft, x_rgt, y_bot, y_top)

    ref_view = _default_reference_view(plot_res)
    bb = _reference_bounding_box_from_view(ref_view, plot_res)

    plot_width = bb.width
    plot_height = bb.height

    if plot_width <= 0.0 or plot_height <= 0.0:
        raise ValueError("reference plot viewport width/height must be positive")

    xwsp_perc = float(panel_res.get("gsnPanelXWhiteSpacePercent", 1.0))
    ywsp_perc = float(panel_res.get("gsnPanelYWhiteSpacePercent", 1.0))

    xwsp = xwsp_perc / 100.0 * plot_width
    ywsp = ywsp_perc / 100.0 * plot_height

    total_width = 2.0 * xwsp + plot_width
    total_height = 2.0 * ywsp + plot_height

    use_labelbar = common_labelbar and bool_resource(panel_res, "gsnPanelLabelBar", True)
    labelbar_side = str(panel_res.get("gsnPanelLabelBarSide", "bottom")).lower()
    lb_horizontal = labelbar_side not in ["left", "right"]

    if use_labelbar:
        if lb_horizontal:
            labelbar_height = 0.20 * plot_height + 2.0 * ywsp
            labelbar_width = (slot_cols - 1) * total_width if slot_cols > 1 else plot_width
        else:
            labelbar_height = (nrows - 1) * total_height if nrows > 1 else plot_height
            labelbar_width = 0.20 * plot_width + 2.0 * xwsp
    else:
        labelbar_height = 0.0
        labelbar_width = 0.0

    xrange = x_rgt - x_lft
    yrange = y_top - y_bot

    if lb_horizontal:
        row_scale = yrange / (nrows * total_height + labelbar_height)
        col_scale = xrange / (slot_cols * total_width)
        scale = min(col_scale, row_scale)
        yrange_for_plots = yrange - scale * labelbar_height
        xrange_for_plots = xrange
    else:
        row_scale = yrange / (nrows * total_height)
        col_scale = xrange / (slot_cols * total_width + labelbar_width)
        scale = min(col_scale, row_scale)
        yrange_for_plots = yrange
        xrange_for_plots = xrange - scale * labelbar_width

    new_plot_width = scale * plot_width
    new_plot_height = scale * plot_height

    xwsp = xwsp_perc / 100.0 * new_plot_width
    ywsp = ywsp_perc / 100.0 * new_plot_height

    new_total_width = 2.0 * xwsp + new_plot_width
    new_total_height = 2.0 * ywsp + new_plot_height

    ysp = yrange_for_plots - new_total_height * nrows
    xsp_all = xrange_for_plots - new_total_width * slot_cols

    dxl = scale * (ref_view.vpXF - bb.left)
    dyt = scale * (bb.top - ref_view.vpYF)

    y_positions = [
        y_top - ywsp - dyt - (ysp / 2.0 + new_total_height * row)
        for row in range(nrows)
    ]

    panel_center = bool_resource(panel_res, "gsnPanelCenter", True)
    x_values = _as_float_sequence(panel_res.get("gsnPanelXF"), nplots, "gsnPanelXF")
    y_values = _as_float_sequence(panel_res.get("gsnPanelYF"), nplots, "gsnPanelYF")

    views = []
    rows = []
    cols = []

    index = 0

    for row, count in enumerate(row_counts):
        count = int(count)

        if count <= 0:
            continue

        if panel_center:
            xsp = xrange_for_plots - new_total_width * count
        else:
            xsp = xsp_all

        for col in range(count):
            if index >= nplots:
                break

            vpXF = x_lft + xwsp + dxl + (xsp / 2.0 + new_total_width * col)
            vpYF = y_positions[row]

            if x_values is not None and 0.0 <= x_values[index] <= 1.0:
                vpXF = x_values[index]

            if y_values is not None and 0.0 <= y_values[index] <= 1.0:
                vpYF = y_values[index]

            views.append(
                HluView(
                    vpXF=vpXF,
                    vpYF=vpYF,
                    vpWidthF=scale * ref_view.vpWidthF,
                    vpHeightF=scale * ref_view.vpHeightF,
                )
            )
            rows.append(row)
            cols.append(col)
            index += 1

    labelbar_view = None

    if use_labelbar and views:
        lb_width = scale * labelbar_width
        lb_height = scale * labelbar_height

        if "pmLabelBarWidthF" in panel_res:
            lb_width = float(panel_res["pmLabelBarWidthF"])

        if "pmLabelBarHeightF" in panel_res:
            lb_height = float(panel_res["pmLabelBarHeightF"])

        parallel = float(panel_res.get("pmLabelBarParallelPosF", 0.0))
        orthogonal = float(panel_res.get("pmLabelBarOrthogonalPosF", 0.0))

        left = min(v.left for v in views)
        right = max(v.right for v in views)
        bottom = min(v.bottom for v in views)
        top = max(v.top for v in views)
        group_width = right - left
        group_height = top - bottom

        if labelbar_side == "top":
            vpXF = left + (group_width - lb_width) / 2.0 + parallel
            vpYF = top + orthogonal + lb_height
        elif labelbar_side == "left":
            vpXF = left - orthogonal - lb_width
            vpYF = bottom + (group_height + lb_height) / 2.0 + parallel
        elif labelbar_side == "right":
            vpXF = right + orthogonal
            vpYF = bottom + (group_height + lb_height) / 2.0 + parallel
        else:
            vpXF = left + (group_width - lb_width) / 2.0 + parallel
            vpYF = bottom - orthogonal

        labelbar_view = HluView(
            vpXF=vpXF,
            vpYF=vpYF,
            vpWidthF=lb_width,
            vpHeightF=lb_height,
        )

    rects = [view.as_mpl_rect() for view in views]
    labelbar_rect = labelbar_view.as_mpl_rect() if labelbar_view is not None else None

    return {
        "views": views,
        "rects": rects,
        "rows": rows,
        "cols": cols,
        "row_counts": row_counts,
        "ncols": slot_cols,
        "nrows": nrows,
        "row_spec": row_spec,
        "labelbar_view": labelbar_view,
        "labelbar_rect": labelbar_rect,
        "scale": scale,
        "reference_view": ref_view,
    }
