from __future__ import annotations

from ._ndc import gsn_text_ndc
from ._polygon import gsn_polygon_ndc
from ._polyline import gsn_polyline_ndc
from ._polymarker import gsn_polymarker_ndc


def _panel_group_bounds(panel_layout):
    views = panel_layout.get("views", [])

    if views:
        left = min(v.left for v in views)
        right = max(v.right for v in views)
        bottom = min(v.bottom for v in views)
        top = max(v.top for v in views)
        return left, bottom, right, top

    rects = panel_layout.get("rects", [])

    if not rects:
        raise ValueError("panel_layout must contain views or rects")

    left = min(r[0] for r in rects)
    right = max(r[0] + r[2] for r in rects)
    bottom = min(r[1] for r in rects)
    top = max(r[1] + r[3] for r in rects)

    return left, bottom, right, top


def _add_box_outline(wks, primitives, x1, x2, y1, y2, res):
    primitives.append(
        gsn_polyline_ndc(
            wks,
            [x1, x2, x2, x1, x1],
            [y1, y1, y2, y2, y1],
            {
                "gsLineColor": res.get("legendLineColor", "black"),
                "gsLineThicknessF": res.get("legendLineThicknessF", 1.0),
                "gsnDraw": False,
            },
        )
    )


def _add_not_significant_box(wks, primitives, x1, x2, y1, y2, res):
    _add_box_outline(wks, primitives, x1, x2, y1, y2, res)

    marker_res = {
        "gsMarkerIndex": res.get("legendMarkerIndex", 5),
        "gsMarkerSizeF": res.get("legendMarkerSizeF", 0.0016),
        "gsMarkerThicknessF": res.get("legendMarkerThicknessF", 0.5),
        "gsMarkerOpacityF": res.get("legendMarkerOpacityF", 0.6),
        "gsMarkerColor": res.get("legendMarkerColor", "black"),
        "gsnDraw": False,
    }

    # NCL source style: staggered 3-2-3 marker layout.
    for j in [0, 2]:
        for i in range(3):
            primitives.append(
                gsn_polymarker_ndc(
                    wks,
                    [x1 + (i + 0.5) * (x2 - x1) / 3.0],
                    [y1 + (j + 0.5) * (y2 - y1) / 3.0],
                    marker_res,
                )
            )

    for j in [1]:
        for i in range(2):
            primitives.append(
                gsn_polymarker_ndc(
                    wks,
                    [x1 + (i + 1.0) * (x2 - x1) / 3.0],
                    [y1 + (j + 0.5) * (y2 - y1) / 3.0],
                    marker_res,
                )
            )


def _clip_diag_segment(width, height, c):
    # Local box: 0 <= x <= width, 0 <= y <= height
    # Diagonal family: y = x - c
    pts = []

    xx = c
    if 0.0 <= xx <= width:
        pts.append((xx, 0.0))

    xx = c + height
    if 0.0 <= xx <= width:
        pts.append((xx, height))

    yy = -c
    if 0.0 <= yy <= height:
        pts.append((0.0, yy))

    yy = width - c
    if 0.0 <= yy <= height:
        pts.append((width, yy))

    unique = []

    for px, py in pts:
        if not any(abs(px - qx) < 1e-10 and abs(py - qy) < 1e-10 for qx, qy in unique):
            unique.append((px, py))

    if len(unique) < 2:
        return None

    return unique[0], unique[-1]


def _add_sign_agreement_box(wks, primitives, x1, x2, y1, y2, res):
    # Keep NCL fill-index resources on the polygon object.
    primitives.append(
        gsn_polygon_ndc(
            wks,
            [x1, x2, x2, x1],
            [y1, y1, y2, y2],
            {
                "gsFillColor": res.get("legendPatternColor", "white"),
                "gsLineColor": res.get("legendLineColor", "black"),
                "gsLineThicknessF": res.get("legendLineThicknessF", 1.0),
                "gsFillIndex": res.get("legendFillIndex", 3),
                "gsFillScaleF": res.get("legendFillScaleF", 0.7),
                "gsnDraw": False,
            },
        )
    )

    # Current bridge renderer: draw exactly four black internal diagonal lines.
    hatch_color = res.get("legendHatchColor", "black")
    hatch_thickness = float(res.get("legendHatchThicknessF", 1.0))
    hatch_count = int(res.get("legendHatchLineCount", 4))

    width = x2 - x1
    height = y2 - y1

    if hatch_count > 0:
        # Four internal strokes, avoiding the outer border.
        cmin = -0.65 * height
        cmax = width - 0.35 * height

        if hatch_count == 1:
            c_values = [0.5 * (cmin + cmax)]
        else:
            step = (cmax - cmin) / float(hatch_count - 1)
            c_values = [cmin + i * step for i in range(hatch_count)]

        for c in c_values:
            segment = _clip_diag_segment(width, height, c)

            if segment is None:
                continue

            (xa, ya), (xb, yb) = segment

            primitives.append(
                gsn_polyline_ndc(
                    wks,
                    [x1 + xa, x1 + xb],
                    [y1 + ya, y1 + yb],
                    {
                        "gsLineColor": hatch_color,
                        "gsLineThicknessF": hatch_thickness,
                        "gsnDraw": False,
                    },
                )
            )

    _add_box_outline(wks, primitives, x1, x2, y1, y2, res)


def gsn_panel_pattern_legend_ndc(wks, panel_layout, labelbar, res=None):
    """Create IPCC-style spatial-pattern legend blocks.

    This follows the NCL source geometry, but derives the final NDC position
    from the panel group and common labelbar object instead of hard-coding
    final page coordinates.

    Geometry:
        box size ~= 0.4 * labelbar height
        box top  ~= labelbar top
        left box ~= panel group left + small offset
        right box ~= labelbar right + small offset
    """
    res = dict(res or {})

    primitives = []

    group_left, group_bottom, group_right, group_top = _panel_group_bounds(panel_layout)
    lbv = labelbar.view

    box_width = float(res.get("legendBoxWidthF", 0.32 * lbv.vpHeightF))
    box_height = float(res.get("legendBoxHeightF", 0.32 * lbv.vpHeightF))

    # NCL source block aligns visually with the upper part of the labelbar.
    # Do not lift it above the labelbar unless explicitly requested.
    box_top = float(res.get("legendBoxTopF", lbv.top))
    box_bottom = box_top - box_height
    text_y = 0.5 * (box_bottom + box_top)

    text_offset = float(res.get("legendTextOffsetXF", 0.005))

    left_box_x1 = float(
        res.get(
            "legendLeftBoxXF",
            group_left + float(res.get("legendLeftOffsetF", 0.012)),
        )
    )
    left_box_x2 = left_box_x1 + box_width

    right_box_x1 = float(
        res.get(
            "legendRightBoxXF",
            lbv.right + float(res.get("legendRightOffsetF", 0.006)),
        )
    )
    right_box_x2 = right_box_x1 + box_width

    _add_not_significant_box(
        wks,
        primitives,
        left_box_x1,
        left_box_x2,
        box_bottom,
        box_top,
        res,
    )

    primitives.append(
        gsn_text_ndc(
            wks,
            res.get("legendNotSignificantText", " not significant\n at 10% level"),
            left_box_x2 + text_offset,
            text_y,
            {
                "txJust": "center_left",
                "txFontHeightF": res.get("legendTextFontHeightF", 0.0075),
                "txFontColor": res.get("legendTextFontColor", "black"),
                "gsnDraw": False,
            },
        )
    )

    _add_sign_agreement_box(
        wks,
        primitives,
        right_box_x1,
        right_box_x2,
        box_bottom,
        box_top,
        res,
    )

    primitives.append(
        gsn_text_ndc(
            wks,
            res.get("legendAgreementText", " < 80% of runs\n agree on sign"),
            right_box_x2 + text_offset,
            text_y,
            {
                "txJust": "center_left",
                "txFontHeightF": res.get("legendTextFontHeightF", 0.0075),
                "txFontColor": res.get("legendTextFontColor", "black"),
                "gsnDraw": False,
            },
        )
    )

    return primitives
