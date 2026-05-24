from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ._labelbar import (
    _merge_labelbar_resources,
    _normalize_labelbar_color_resources,
    _normalize_orientation,
)
from ._primitive import HluPolygon, HluPolyline
from ._resources import bool_resource
from ._text_item import HluTextItem
from ._view import HluView


@dataclass
class HluLabelBar:
    view: HluView
    orientation: str = "horizontal"
    boundaries: list = field(default_factory=list)
    fill_colors: list = field(default_factory=list)
    labels: list = field(default_factory=list)
    title: str | None = None
    end_cap_style: str = "none"
    resources: dict = field(default_factory=dict)
    primitives: list = field(default_factory=list)


def _labelbar_boundaries_from_mappable(mappable):
    norm = getattr(mappable, "norm", None)
    boundaries = getattr(norm, "boundaries", None)

    if boundaries is not None:
        arr = np.asarray(boundaries, dtype=float)

        if arr.size >= 2:
            return arr.tolist()

    levels = getattr(mappable, "levels", None)

    if levels is not None:
        arr = np.asarray(levels, dtype=float)

        if arr.size >= 2:
            return arr.tolist()

    try:
        vmin, vmax = mappable.get_clim()
    except Exception:
        vmin, vmax = -1.0, 1.0

    return np.linspace(float(vmin), float(vmax), 11).tolist()


def _labelbar_fill_colors_from_mappable(mappable, boundaries):
    cmap = getattr(mappable, "cmap", None)
    norm = getattr(mappable, "norm", None)

    if cmap is None:
        return ["white"] * max(0, len(boundaries) - 1)

    mids = 0.5 * (np.asarray(boundaries[:-1]) + np.asarray(boundaries[1:]))

    colors = []

    for value in mids:
        try:
            if norm is not None:
                colors.append(cmap(norm(value)))
            else:
                colors.append(cmap(value))
        except Exception:
            colors.append(cmap(0.5))

    return colors


def _format_label(value, lbres):
    fmt = lbres.get("lbLabelFormat", None)
    value = float(value)

    if abs(value) < 1e-12:
        value = 0.0

    if fmt is not None:
        try:
            return fmt % value
        except Exception:
            pass

    if abs(value - round(value)) < 1e-10:
        return str(int(round(value)))

    return f"{value:g}"


def _labelbar_labels_from_boundaries(boundaries, lbres):
    label_strings = lbres.get("lbLabelStrings", None)

    if label_strings is not None:
        return [str(item) for item in label_strings]

    return [_format_label(v, lbres) for v in boundaries]


def _labelbar_end_cap_style(lbres):
    style = str(lbres.get("lbBoxEndCapStyle", "None")).lower()

    if "triangleboth" in style or "both" in style:
        return "both"

    if "trianglelow" in style or "min" in style or "low" in style:
        return "min"

    if "trianglehigh" in style or "max" in style or "high" in style:
        return "max"

    return "none"


def _make_polygon(x, y, fill_color, line_color, line_thickness, name):
    return HluPolygon(
        x=list(x),
        y=list(y),
        coord_system="ndc",
        name=name,
        resources={
            "fill_color": fill_color,
            "line_color": line_color,
            "line_thickness": line_thickness,
        },
    )


def _make_polyline(x, y, line_color, line_thickness, name):
    return HluPolyline(
        x=list(x),
        y=list(y),
        coord_system="ndc",
        name=name,
        resources={
            "gsLineColor": line_color,
            "gsLineThicknessF": line_thickness,
        },
    )


def _make_text_item(text, x, y, just, size, color, angle, name):
    return HluTextItem(
        txString=str(text),
        txPosXF=float(x),
        txPosYF=float(y),
        txJust=str(just),
        txFontHeightF=float(size),
        txFontColor=color,
        txAngleF=float(angle),
        coord_system="ndc",
        name=name,
    )


def _build_horizontal_labelbar_primitives(labelbar: HluLabelBar):
    """Build NCL-like horizontal LabelBar primitives.

    Important NCL-style rule:
    pmLabelBarWidthF is treated as the full labelbar width, including
    triangular end caps. The rectangular boxes live inside that width.
    """
    view = labelbar.view
    lbres = dict(labelbar.resources)

    x0 = view.left
    x1 = view.right
    y0 = view.bottom
    y1 = view.top

    width = x1 - x0
    height = y1 - y0

    boundaries = labelbar.boundaries
    colors = labelbar.fill_colors
    labels = labelbar.labels

    nbox = len(colors)

    if nbox <= 0:
        return []

    draw_low = labelbar.end_cap_style in ["both", "min"]
    draw_high = labelbar.end_cap_style in ["both", "max"]

    # NCL triangular end caps are part of the labelbar width.
    # Treat each cap as half of one box by default.
    cap_ratio = float(lbres.get("lbBoxEndCapRatioF", 0.5))

    ncap = 0.0

    if draw_low:
        ncap += cap_ratio

    if draw_high:
        ncap += cap_ratio

    box_width = width / (float(nbox) + ncap)
    cap_width = cap_ratio * box_width

    body_x0 = x0 + (cap_width if draw_low else 0.0)
    body_x1 = x1 - (cap_width if draw_high else 0.0)

    dx = (body_x1 - body_x0) / float(nbox)

    # Vertical geometry.  The box sits in the upper half of the labelbar
    # view; labels sit below it; the unit title sits below the labels.
    box_y0 = y0 + float(lbres.get("lbBoxBottomRatioF", 0.62)) * height
    box_y1 = y0 + float(lbres.get("lbBoxTopRatioF", 0.84)) * height
    box_ym = 0.5 * (box_y0 + box_y1)

    label_y = y0 + float(lbres.get("lbLabelYRatioF", 0.50)) * height
    title_y = y0 + float(lbres.get("lbTitleYRatioF", 0.10)) * height

    line_color = lbres.get("lbBoxLineColor", "black")
    line_thickness = float(lbres.get("lbBoxLineThicknessF", 0.45))
    sep_line_thickness = float(
        lbres.get("lbBoxSeparatorLineThicknessF", line_thickness)
    )

    primitives = []

    if draw_low:
        primitives.append(
            _make_polygon(
                [x0, body_x0, body_x0],
                [box_ym, box_y1, box_y0],
                colors[0],
                line_color,
                line_thickness,
                "labelbar_left_endcap",
            )
        )

    for i, color in enumerate(colors):
        xa = body_x0 + i * dx
        xb = xa + dx

        primitives.append(
            _make_polygon(
                [xa, xb, xb, xa],
                [box_y0, box_y0, box_y1, box_y1],
                color,
                line_color,
                line_thickness,
                f"labelbar_box_{i}",
            )
        )

    if draw_high:
        primitives.append(
            _make_polygon(
                [body_x1, body_x1, x1],
                [box_y0, box_y1, box_ym],
                colors[-1],
                line_color,
                line_thickness,
                "labelbar_right_endcap",
            )
        )

    if bool_resource(lbres, "lbBoxLinesOn", True):
        for i in range(1, nbox):
            xx = body_x0 + i * dx
            primitives.append(
                _make_polyline(
                    [xx, xx],
                    [box_y0, box_y1],
                    line_color,
                    sep_line_thickness,
                    f"labelbar_sep_{i}",
                )
            )

    if bool_resource(lbres, "lbTickMarksOn", True):
        tick_color = lbres.get("lbTickMarkColor", line_color)
        tick_thickness = float(lbres.get("lbTickThicknessF", 0.6))
        tick_length = float(lbres.get("lbTickLengthF", 0.08 * height))

        # If users pass an NCL-like small ratio, keep it as page/NDC distance.
        # If they pass a larger visual value, interpret it as percent.
        if tick_length > 1.0:
            tick_length = tick_length / 100.0

        tick_y0 = box_y0
        tick_y1 = box_y0 - tick_length

        for i in range(len(boundaries)):
            xx = body_x0 + i * dx
            primitives.append(
                _make_polyline(
                    [xx, xx],
                    [tick_y0, tick_y1],
                    tick_color,
                    tick_thickness,
                    f"labelbar_tick_{i}",
                )
            )

    if bool_resource(lbres, "lbLabelsOn", True):
        label_size = float(lbres.get("lbLabelFontHeightF", 0.010))
        label_color = lbres.get("lbLabelFontColor", "black")
        label_angle = float(lbres.get("lbLabelAngleF", 0.0))

        for i, label in enumerate(labels):
            xx = body_x0 + i * dx
            primitives.append(
                _make_text_item(
                    label,
                    xx,
                    label_y,
                    "top_center",
                    label_size,
                    label_color,
                    label_angle,
                    f"labelbar_label_{i}",
                )
            )

    if bool_resource(lbres, "lbTitleOn", False) and labelbar.title is not None:
        title_size = float(lbres.get("lbTitleFontHeightF", 0.010))
        title_color = lbres.get("lbTitleFontColor", "black")
        title_position = str(lbres.get("lbTitlePosition", "Bottom")).lower()

        if title_position in ["top", "above"]:
            title_y_final = y0 + 0.94 * height
            title_just = "bottom_center"
        else:
            title_y_final = title_y
            title_just = "top_center"

        primitives.append(
            _make_text_item(
                labelbar.title,
                0.5 * (body_x0 + body_x1),
                title_y_final,
                title_just,
                title_size,
                title_color,
                0.0,
                "labelbar_title",
            )
        )

    return primitives



def build_hlu_labelbar(view: HluView, mappable, lbres: dict | None = None, pmres=None):
    lbres = _merge_labelbar_resources(lbres, pmres)
    lbres = _normalize_labelbar_color_resources(lbres)

    orientation = _normalize_orientation(lbres)

    boundaries = _labelbar_boundaries_from_mappable(mappable)
    fill_colors = _labelbar_fill_colors_from_mappable(mappable, boundaries)
    labels = _labelbar_labels_from_boundaries(boundaries, lbres)
    title = lbres.get("lbTitleString", None)
    end_cap_style = _labelbar_end_cap_style(lbres)

    labelbar = HluLabelBar(
        view=view,
        orientation=orientation,
        boundaries=list(boundaries),
        fill_colors=list(fill_colors),
        labels=list(labels),
        title=title,
        end_cap_style=end_cap_style,
        resources=dict(lbres),
    )

    if orientation == "horizontal":
        labelbar.primitives = _build_horizontal_labelbar_primitives(labelbar)
    else:
        labelbar.primitives = []

    return labelbar
