"""
SVG renderer for HLU-style graphics objects.

The plot renderer uses an HLU-style geometry split:
outer rectangle, annotation rectangle, and data rectangle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any, Sequence


Rect = tuple[float, float, float, float]


@dataclass
class SvgDocument:
    """Simple SVG document builder."""

    width: int = 1000
    height: int = 800
    background: str | None = "white"
    elements: list[str] = field(default_factory=list)

    def add(self, element: str) -> None:
        self.elements.append(element)

    def tostring(self) -> str:
        body: list[str] = []
        if self.background not in (None, "none", "transparent"):
            body.append(
                f'<rect x="0" y="0" width="{self.width}" height="{self.height}" '
                f'fill="{escape(str(self.background))}" />'
            )

        body.extend(self.elements)
        joined = "\n  ".join(body)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">\n'
            f'  {joined}\n'
            f'</svg>\n'
        )

    def write(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.tostring(), encoding="utf-8")
        return output


def _get(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)

    resources = getattr(obj, "resources", None)
    if isinstance(resources, dict):
        for name in names:
            if name in resources:
                return resources[name]

    return default


def _resources(obj: Any) -> dict[str, Any]:
    value = getattr(obj, "resources", None)
    if isinstance(value, dict):
        return value
    return {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if hasattr(value, "tolist"):
        value = value.tolist()
    try:
        return list(value)
    except TypeError:
        return [value]


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _rgb_to_hex(value: Sequence[Any]) -> str:
    vals = [_num(item) for item in _as_list(value)[:3]]
    if not vals:
        return "black"

    if max(abs(item) for item in vals) <= 1.0:
        vals = [item * 255.0 for item in vals]

    vals = [min(255, max(0, round(item))) for item in vals]
    return "#{:02x}{:02x}{:02x}".format(vals[0], vals[1], vals[2])


def _color(value: Any, default: str = "black") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence):
        return _rgb_to_hex(value)
    return str(value)


def _rect_from_any(value: Any, default: Rect) -> Rect:
    items = _as_list(value)
    if len(items) < 4:
        return default

    return (
        _num(items[0], default[0]),
        _num(items[1], default[1]),
        _num(items[2], default[2]),
        _num(items[3], default[3]),
    )


def _object_rect(obj: Any) -> Rect:
    rect = _get(obj, "rect", "bbox", default=None)
    if rect is not None:
        return _rect_from_any(rect, (0.12, 0.20, 0.76, 0.64))

    res = _resources(obj)
    left = _num(res.get("vpXF", 0.12), 0.12)
    top = _num(res.get("vpYF", 0.86), 0.86)
    width = _num(res.get("vpWidthF", 0.76), 0.76)
    height = _num(res.get("vpHeightF", 0.64), 0.64)
    bottom = top - height
    return (left, bottom, width, height)


def _plot_regions(obj: Any) -> dict[str, Rect]:
    outer = _object_rect(obj)
    left, bottom, width, height = outer

    res = _resources(obj)
    anno_frac = _num(res.get("vpAnnotationHeightF", 0.16), 0.16)
    anno_frac = _clamp(anno_frac, 0.0, 0.40)

    data_height = height * (1.0 - anno_frac)
    anno_height = height - data_height

    data = (left, bottom, width, data_height)
    annotation = (left, bottom + data_height, width, anno_height)

    return {
        "outer": outer,
        "annotation": annotation,
        "data": data,
    }


def _rect_to_pixels(rect: Rect, doc: SvgDocument) -> tuple[float, float, float, float]:
    left, bottom, width, height = rect
    x = left * doc.width
    y = (1.0 - bottom - height) * doc.height
    w = width * doc.width
    h = height * doc.height
    return x, y, w, h


def _to_global_x(value: Any, doc: SvgDocument, viewport: Rect | None = None) -> float:
    x = _num(value)
    if viewport is not None:
        left, bottom, width, height = viewport
        x = left + x * width
    return x * doc.width


def _to_global_y(value: Any, doc: SvgDocument, viewport: Rect | None = None) -> float:
    y = _num(value)
    if viewport is not None:
        left, bottom, width, height = viewport
        y = bottom + y * height
    return (1.0 - y) * doc.height


def _class_name(obj: Any) -> str:
    return obj.__class__.__name__.lower()


def _is_text_object(obj: Any) -> bool:
    return "text" in _class_name(obj)


def _text_region(obj: Any) -> str:
    value = _resources(obj).get("climaraTextRegion")
    if value is None:
        return "data"
    return str(value)


def _child_viewport(child: Any, regions: dict[str, Rect]) -> Rect:
    if _is_text_object(child) and _text_region(child) == "annotation":
        return regions["annotation"]
    return regions["data"]


def _stroke_width(obj: Any, default: float = 1.0) -> float:
    return _num(
        _get(
            obj,
            "gsLineThicknessF",
            "line_width",
            "stroke_width",
            "width",
            default=default,
        ),
        default,
    )


def _points_from_xy(
    obj: Any,
    doc: SvgDocument,
    viewport: Rect | None = None,
) -> list[tuple[float, float]]:
    points = _get(obj, "points", "xy", default=None)
    if points is not None:
        out = []
        for point in points:
            if len(point) >= 2:
                out.append(
                    (
                        _to_global_x(point[0], doc, viewport),
                        _to_global_y(point[1], doc, viewport),
                    )
                )
        return out

    xs = _as_list(_get(obj, "x", "xs", "lon", "lons", default=[]))
    ys = _as_list(_get(obj, "y", "ys", "lat", "lats", default=[]))
    return [
        (_to_global_x(x, doc, viewport), _to_global_y(y, doc, viewport))
        for x, y in zip(xs, ys)
    ]


def _render_polyline(obj: Any, doc: SvgDocument, viewport: Rect | None = None) -> None:
    points = _points_from_xy(obj, doc, viewport)
    if not points:
        return

    data = " ".join(f"{x:.3f},{y:.3f}" for x, y in points)
    stroke = _color(_get(obj, "gsLineColor", "line_color", "stroke", default="black"))
    width = _stroke_width(obj)

    doc.add(
        f'<polyline points="{data}" fill="none" stroke="{escape(stroke)}" '
        f'stroke-width="{width:.3f}" />'
    )


def _render_polygon(obj: Any, doc: SvgDocument, viewport: Rect | None = None) -> None:
    points = _points_from_xy(obj, doc, viewport)
    if not points:
        return

    data = " ".join(f"{x:.3f},{y:.3f}" for x, y in points)
    fill = _color(_get(obj, "gsFillColor", "fill_color", "fill", default="none"), "none")
    stroke = _color(_get(obj, "gsLineColor", "line_color", "stroke", default="black"))
    width = _stroke_width(obj)

    doc.add(
        f'<polygon points="{data}" fill="{escape(fill)}" stroke="{escape(stroke)}" '
        f'stroke-width="{width:.3f}" />'
    )


def _render_marker(obj: Any, doc: SvgDocument, viewport: Rect | None = None) -> None:
    points = _points_from_xy(obj, doc, viewport)
    if not points:
        return

    color = _color(_get(obj, "gsMarkerColor", "marker_color", "color", default="black"))
    size = _num(_get(obj, "gsMarkerSizeF", "marker_size", "size", default=0.008), 0.008)
    radius = max(1.0, size * min(doc.width, doc.height))

    for x, y in points:
        doc.add(
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius:.3f}" '
            f'fill="{escape(color)}" stroke="{escape(color)}" />'
        )


def _annotation_just_key(value: Any) -> str:
    key = str(value or "bottomright").replace("_", "").replace("-", "").lower()
    mapping = {
        "bottomright": "bottomright",
        "topright": "topright",
        "topleft": "topleft",
        "bottomleft": "bottomleft",
    }
    return mapping.get(key, "bottomright")


def _annotation_signs(just: str) -> tuple[float, float]:
    key = _annotation_just_key(just)

    if key == "bottomright":
        return 1.0, 1.0
    if key == "topright":
        return 1.0, -1.0
    if key == "topleft":
        return -1.0, -1.0
    if key == "bottomleft":
        return -1.0, 1.0

    return 1.0, 1.0


def _annotation_text_just(just: str) -> str:
    key = _annotation_just_key(just)
    mapping = {
        "bottomright": "BottomRight",
        "topright": "TopRight",
        "topleft": "TopLeft",
        "bottomleft": "BottomLeft",
    }
    return mapping.get(key, "BottomRight")


def _annotation_default_offsets(just: str, viewport: Rect) -> tuple[float, float]:
    left, bottom, width, height = viewport
    len_pct = 0.025

    if width < height:
        wsp_hpct = (len_pct * width) / height
        wsp_wpct = len_pct
    else:
        wsp_hpct = len_pct
        wsp_wpct = (len_pct * height) / width

    para_sign, orth_sign = _annotation_signs(just)

    para = para_sign * (0.5 - wsp_wpct)
    orth = orth_sign * (0.5 - wsp_hpct)

    return para, orth


def _panel_figure_string_position(
    obj: Any,
    viewport: Rect,
) -> tuple[float, float, str]:
    res = _resources(obj)
    just = _annotation_just_key(res.get("amJust", "bottomright"))

    para_default, orth_default = _annotation_default_offsets(just, viewport)

    para = _num(res.get("amParallelPosF", para_default), para_default)
    orth = _num(res.get("amOrthogonalPosF", orth_default), orth_default)

    x = _clamp(0.5 + para, 0.0, 1.0)
    y = _clamp(0.5 - orth, 0.0, 1.0)

    return x, y, _annotation_text_just(just)

def _text_anchor(just: str) -> str:
    text = str(just).lower()
    if "left" in text:
        return "start"
    if "right" in text:
        return "end"
    return "middle"


def _text_dy(just: str) -> str:
    key = str(just).lower()

    if "top" in key:
        return "0.85em"
    if "center" in key:
        return "0.35em"
    if "bottom" in key:
        return "-0.15em"

    return "0em"

def _render_text(obj: Any, doc: SvgDocument, viewport: Rect | None = None) -> None:
    text = _get(obj, "text", "string", default="")
    if text in (None, ""):
        return

    res = _resources(obj)

    if res.get("climaraPanelFigureString") is True and viewport is not None:
        local_x, local_y, just = _panel_figure_string_position(obj, viewport)
        x = _to_global_x(local_x, doc, viewport)
        y = _to_global_y(local_y, doc, viewport)
    else:
        just = _get(obj, "txJust", "justify", default="CenterCenter")
        x = _to_global_x(_get(obj, "x", default=0.5), doc, viewport)
        y = _to_global_y(_get(obj, "y", default=0.5), doc, viewport)

    size = _num(_get(obj, "txFontHeightF", "font_size", default=0.014), 0.014)
    size_px = max(1.0, size * doc.height)
    color = _color(_get(obj, "txFontColor", "font_color", default="black"))
    angle = _num(_get(obj, "txAngleF", "angle", default=0.0), 0.0)

    transform = ""
    if angle:
        transform = f' transform="rotate({-angle:.3f} {x:.3f} {y:.3f})"'

    doc.add(
        f'<text x="{x:.3f}" y="{y:.3f}" dy="{_text_dy(just)}" '
        f'font-size="{size_px:.3f}" fill="{escape(color)}" '
        f'text-anchor="{_text_anchor(just)}"{transform}>{escape(str(text))}</text>'
    )

def _render_view_box(obj: Any, doc: SvgDocument) -> None:
    rect = _get(obj, "rect", "bbox", default=None)
    if rect is None:
        return

    x, y, w, h = _rect_to_pixels(_rect_from_any(rect, (0.0, 0.0, 1.0, 1.0)), doc)
    stroke = _color(_get(obj, "box_color", "stroke", default="none"), "none")
    fill = _color(_get(obj, "fill", default="none"), "none")

    doc.add(
        f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
        f'fill="{escape(fill)}" stroke="{escape(stroke)}" />'
    )


def _flatten_numbers(rows: list[list[Any]]) -> list[float]:
    values: list[float] = []
    for row in rows:
        for item in row:
            try:
                value = float(item)
            except (TypeError, ValueError):
                continue
            if value == value:
                values.append(value)
    return values


def _to_2d_rows(data: Any) -> list[list[Any]]:
    if data is None:
        return []

    if hasattr(data, "values"):
        data = data.values
    if hasattr(data, "tolist"):
        data = data.tolist()

    rows = _as_list(data)
    if not rows:
        return []

    first = rows[0]
    if isinstance(first, (int, float)):
        return [rows]

    return [_as_list(row) for row in rows]


def _levels_from_resources(obj: Any, values: list[float]) -> list[float]:
    levels = _get(obj, "levels", "cnLevels", default=None)
    if levels is not None:
        return [float(item) for item in _as_list(levels)]

    res = _resources(obj)
    required = {"cnMinLevelValF", "cnMaxLevelValF", "cnLevelSpacingF"}
    if required.issubset(set(res)):
        start = float(res["cnMinLevelValF"])
        stop = float(res["cnMaxLevelValF"])
        step = float(res["cnLevelSpacingF"])
        if step <= 0:
            step = 1.0

        out: list[float] = []
        value = start
        guard = 0
        while value <= stop + step * 1e-8:
            out.append(round(value, 10))
            value += step
            guard += 1
            if guard > 10000:
                break
        return out

    if not values:
        return [0.0, 1.0]

    low = min(values)
    high = max(values)
    if low == high:
        return [low - 0.5, high + 0.5]

    step = (high - low) / 10.0
    return [low + i * step for i in range(11)]


def _colors_from_object(obj: Any, n: int) -> list[str]:
    colors = _get(obj, "colors", "cnFillPalette", default=None)
    if colors is not None and hasattr(colors, "to_hex_list"):
        out = list(colors.to_hex_list())
    else:
        out = [_color(item) for item in _as_list(colors)]

    if not out:
        out = [
            "#313695",
            "#4575b4",
            "#74add1",
            "#abd9e9",
            "#e0f3f8",
            "#ffffbf",
            "#fee090",
            "#fdae61",
            "#f46d43",
            "#d73027",
            "#a50026",
        ]

    while len(out) < n:
        out.append(out[-1])
    return out


def _color_index(value: float, levels: list[float], ncolors: int) -> int:
    if not levels:
        return 0

    if value <= levels[0]:
        return 0

    for i in range(1, len(levels)):
        if value <= levels[i]:
            return min(i - 1, ncolors - 1)

    return ncolors - 1


def _render_map_box(obj: Any, doc: SvgDocument, rect: Rect) -> None:
    x, y, width, height = _rect_to_pixels(rect, doc)
    res = _resources(obj)

    fill = _color(res.get("mpFillColor", "none"), "none")
    stroke = _color(res.get("mpGeophysicalLineColor", res.get("mpOutlineBoundaryColor", "#333333")))
    line_width = _num(res.get("mpGeophysicalLineThicknessF", 0.8), 0.8)

    doc.add(
        f'<rect x="{x:.3f}" y="{y:.3f}" width="{width:.3f}" height="{height:.3f}" '
        f'fill="{escape(fill)}" stroke="{escape(stroke)}" stroke-width="{line_width:.3f}" />'
    )





def _grid_sequence(start: float, stop: float, step: float) -> list[float]:
    step = abs(step)
    if step <= 0:
        return []

    values: list[float] = []
    value = start
    guard = 0

    while value <= stop + step * 1e-8:
        values.append(round(value, 10))
        value += step
        guard += 1
        if guard > 1000:
            break

    return values


def _map_lon_values(res: dict[str, Any]) -> list[float]:
    spacing = _num(res.get("mpGridLonSpacingF", 60.0), 60.0)
    spacing = _clamp(abs(spacing), 1.0, 360.0)

    start = _num(res.get("mpMinLonF", -180.0), -180.0)
    stop = _num(res.get("mpMaxLonF", 180.0), 180.0)

    if stop <= start:
        start, stop = -180.0, 180.0

    return _grid_sequence(start, stop, spacing)


def _map_lat_values(res: dict[str, Any]) -> list[float]:
    spacing = _num(res.get("mpGridLatSpacingF", 30.0), 30.0)
    spacing = _clamp(abs(spacing), 1.0, 180.0)

    start = _num(res.get("mpMinLatF", -90.0), -90.0)
    stop = _num(res.get("mpMaxLatF", 90.0), 90.0)

    start = _clamp(start, -90.0, 90.0)
    stop = _clamp(stop, -90.0, 90.0)

    if stop <= start:
        start, stop = -90.0, 90.0

    return _grid_sequence(start, stop, spacing)


def _lon_to_fraction(value: float, res: dict[str, Any]) -> float:
    start = _num(res.get("mpMinLonF", -180.0), -180.0)
    stop = _num(res.get("mpMaxLonF", 180.0), 180.0)
    if stop <= start:
        start, stop = -180.0, 180.0
    return _clamp((value - start) / (stop - start), 0.0, 1.0)


def _lat_to_fraction(value: float, res: dict[str, Any]) -> float:
    start = _num(res.get("mpMinLatF", -90.0), -90.0)
    stop = _num(res.get("mpMaxLatF", 90.0), 90.0)
    if stop <= start:
        start, stop = -90.0, 90.0
    return _clamp((value - start) / (stop - start), 0.0, 1.0)


def _format_lon_label(value: float) -> str:
    if abs(value) < 1e-9:
        return "0°"
    if value < 0:
        return f"{abs(int(value))}°W"
    return f"{int(value)}°E"


def _format_lat_label(value: float) -> str:
    if abs(value) < 1e-9:
        return "0°"
    if value < 0:
        return f"{abs(int(value))}°S"
    return f"{int(value)}°N"


def _map_grid_labels_on(res: dict[str, Any]) -> bool:
    if "mpGridLabelsOn" in res:
        return bool(res["mpGridLabelsOn"])

    mode = str(res.get("pmTickMarkDisplayMode", "")).lower()
    return mode in {"always", "conditional"}


def _draw_svg_text(
    doc: SvgDocument,
    text: str,
    x: float,
    y: float,
    font_size: float,
    color: str,
    anchor: str = "middle",
) -> None:
    doc.add(
        f'<text x="{x:.3f}" y="{y:.3f}" font-size="{font_size:.3f}" '
        f'fill="{escape(color)}" text-anchor="{escape(anchor)}">{escape(text)}</text>'
    )


def _render_map_grid(obj: Any, doc: SvgDocument, rect: Rect) -> None:
    res = _resources(obj)

    if not bool(res.get("mpGridAndLimbOn", False)):
        return

    x, y, width, height = _rect_to_pixels(rect, doc)

    color = _color(res.get("mpGridLineColor", "#999999"))
    line_width = _num(res.get("mpGridLineThicknessF", 0.6), 0.6)
    dash = res.get("mpGridLineDashPattern", "3 3")

    lon_values = _map_lon_values(res)
    lat_values = _map_lat_values(res)

    for lon in lon_values:
        frac = _lon_to_fraction(lon, res)
        xpos = x + width * frac
        doc.add(
            f'<line x1="{xpos:.3f}" y1="{y:.3f}" '
            f'x2="{xpos:.3f}" y2="{y + height:.3f}" '
            f'stroke="{escape(color)}" stroke-width="{line_width:.3f}" '
            f'stroke-dasharray="{escape(str(dash))}" />'
        )

    for lat in lat_values:
        frac = _lat_to_fraction(lat, res)
        ypos = y + height * (1.0 - frac)
        doc.add(
            f'<line x1="{x:.3f}" y1="{ypos:.3f}" '
            f'x2="{x + width:.3f}" y2="{ypos:.3f}" '
            f'stroke="{escape(color)}" stroke-width="{line_width:.3f}" '
            f'stroke-dasharray="{escape(str(dash))}" />'
        )

    if not _map_grid_labels_on(res):
        return

    label_font = _num(res.get("tmLabelFontHeightF", 0.011), 0.011)
    label_size = max(1.0, label_font * doc.height)
    label_color = _color(res.get("tmLabelFontColor", "black"))
    gap = _num(res.get("tmLabelGapF", 0.012), 0.012) * doc.height

    for lon in lon_values:
        frac = _lon_to_fraction(lon, res)
        xpos = x + width * frac
        if x <= xpos <= x + width:
            _draw_svg_text(
                doc,
                _format_lon_label(lon),
                xpos,
                y + height + gap + label_size,
                label_size,
                label_color,
                "middle",
            )

    for lat in lat_values:
        frac = _lat_to_fraction(lat, res)
        ypos = y + height * (1.0 - frac)
        if y <= ypos <= y + height:
            _draw_svg_text(
                doc,
                _format_lat_label(lat),
                x - gap,
                ypos + label_size * 0.35,
                label_size,
                label_color,
                "end",
            )

def _render_contour_grid(obj: Any, doc: SvgDocument, rect: Rect) -> None:
    rows = _to_2d_rows(_get(obj, "data", default=None))
    if not rows:
        return

    nrows = len(rows)
    ncols = max(len(row) for row in rows)
    if nrows <= 0 or ncols <= 0:
        return

    values = _flatten_numbers(rows)
    levels = _levels_from_resources(obj, values)
    colors = _colors_from_object(obj, max(len(levels), 1))

    x0, y0, width, height = _rect_to_pixels(rect, doc)
    cell_w = width / ncols
    cell_h = height / nrows

    for row_index, row in enumerate(rows):
        for col_index, item in enumerate(row):
            try:
                value = float(item)
            except (TypeError, ValueError):
                continue
            if value != value:
                continue

            fill = colors[_color_index(value, levels, len(colors))]
            x = x0 + col_index * cell_w
            y = y0 + row_index * cell_h

            doc.add(
                f'<rect x="{x:.3f}" y="{y:.3f}" width="{cell_w:.3f}" '
                f'height="{cell_h:.3f}" fill="{escape(fill)}" stroke="none" />'
            )

    if bool(_resources(obj).get("cnLinesOn", False)):
        doc.add(
            f'<rect x="{x0:.3f}" y="{y0:.3f}" width="{width:.3f}" '
            f'height="{height:.3f}" fill="none" stroke="black" stroke-width="0.8" />'
        )



def _labelbar_labels(obj: Any) -> list[str]:
    labels = getattr(obj, "visible_label_strings", None)

    if labels is None:
        labels = getattr(obj, "label_strings", None)

    if labels is None:
        labels = getattr(obj, "labels", None)

    if labels is None:
        resources = getattr(obj, "resources", {}) or {}
        if isinstance(resources, dict):
            labels = resources.get("lbLabelStrings")

    return [str(item) for item in _labelbar_sequence(labels)]


def _labelbar_label_positions(*args, **kwargs) -> list[float]:
    obj = None
    rest = args

    if args and hasattr(args[0], "label_axis_positions"):
        obj = args[0]
        rest = args[1:]
    elif "obj" in kwargs:
        obj = kwargs["obj"]

    if obj is not None:
        positions = getattr(obj, "label_axis_positions", None)
        labels = getattr(obj, "visible_label_strings", None)

        if positions is not None:
            out = [float(item) for item in _labelbar_sequence(positions)]
            expected = None
            if labels is not None:
                expected = len(_labelbar_sequence(labels))
            if out and (expected is None or len(out) == expected):
                return out

    nlabels = (
        kwargs.get("nlabels")
        or kwargs.get("label_count")
        or kwargs.get("count")
    )

    labels_arg = kwargs.get("labels")
    if nlabels is None and labels_arg is not None:
        nlabels = len(_labelbar_sequence(labels_arg))

    if nlabels is None:
        for item in rest:
            if isinstance(item, int):
                nlabels = item
                break
            if isinstance(item, (list, tuple)) and not isinstance(item, str):
                nlabels = len(item)
                break

    if nlabels is None:
        nlabels = 0

    nlabels = max(0, int(nlabels))

    if nlabels <= 0:
        return []
    if nlabels == 1:
        return [0.5]

    return [i / (nlabels - 1) for i in range(nlabels)]

def _labelbar_sequence(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def _labelbar_pick(res, *names, default=None):
    for name in names:
        if name in res:
            return res[name]
    return default


def _render_labelbar(obj, doc, viewport=None):
    from ._labelbar_svg_adapter import labelbar_to_svg_primitives

    res = _resources(obj)

    stroke = _color(_labelbar_pick(res, "lbPerimColor", default="black"))
    text_fill = _color(_labelbar_pick(res, "lbLabelFontColor", default="black"))
    font_ndc = _num(_labelbar_pick(res, "lbLabelFontHeightF", default=0.012), 0.012)
    font_size = max(1.0, font_ndc * doc.height)

    primitives = labelbar_to_svg_primitives(
        obj,
        doc.width,
        doc.height,
        stroke=stroke,
        text_fill=text_fill,
    )

    for polygon in primitives.polygons:
        points = " ".join(
            f"{point.x:.3f},{point.y:.3f}"
            for point in polygon.points
        )
        doc.add(
            f'<polygon points="{escape(points)}" '
            f'fill="{escape(_color(polygon.fill))}" '
            f'stroke="{escape(_color(polygon.stroke))}" '
            f'stroke-width="0.25" />'
        )

    for line in primitives.lines:
        doc.add(
            f'<line x1="{line.p1.x:.3f}" y1="{line.p1.y:.3f}" '
            f'x2="{line.p2.x:.3f}" y2="{line.p2.y:.3f}" '
            f'stroke="{escape(_color(line.stroke))}" stroke-width="0.5" />'
        )

    if primitives.orientation == "Horizontal":
        anchor = "middle"
    elif primitives.label_position == "Left":
        anchor = "end"
    else:
        anchor = "start"

    for text_item in primitives.texts:
        transform = ""
        if text_item.angle:
            transform = (
                f' transform="rotate({text_item.angle:.3f} '
                f'{text_item.x:.3f} {text_item.y:.3f})"'
            )

        doc.add(
            f'<text x="{text_item.x:.3f}" y="{text_item.y:.3f}" '
            f'font-size="{font_size:.3f}" '
            f'fill="{escape(_color(text_item.fill))}" '
            f'text-anchor="{anchor}"{transform}>{escape(str(text_item.text))}</text>'
        )

def render_object(
    obj: Any,
    doc: SvgDocument,
    viewport: Rect | None = None,
) -> SvgDocument:
    """Render one object and its children into an SVG document."""

    name = _class_name(obj)

    if "contourplot" in name:
        regions = _plot_regions(obj)
        _render_map_box(obj, doc, regions["data"])
        _render_map_grid(obj, doc, regions["data"])
        _render_contour_grid(obj, doc, regions["data"])

        for child in _as_list(_get(obj, "children", default=[])):
            render_object(child, doc, _child_viewport(child, regions))
        return doc

    if "mapplot" in name:
        regions = _plot_regions(obj)
        _render_map_box(obj, doc, regions["data"])
        _render_map_grid(obj, doc, regions["data"])

        for child in _as_list(_get(obj, "children", default=[])):
            render_object(child, doc, _child_viewport(child, regions))
        return doc

    if "polyline" in name:
        _render_polyline(obj, doc, viewport)
    elif "polygon" in name:
        _render_polygon(obj, doc, viewport)
    elif "marker" in name:
        _render_marker(obj, doc, viewport)
    elif "text" in name:
        _render_text(obj, doc, viewport)
    elif "labelbar" in name:
        _render_labelbar(obj, doc)
    elif "panelitem" in name:
        _render_view_box(obj, doc)

    for child in _as_list(_get(obj, "children", default=[])):
        render_object(child, doc, viewport)

    for plot in _as_list(_get(obj, "plots", default=[])):
        render_object(plot, doc, viewport)

    return doc


def render_svg(
    obj: Any,
    path: str | Path | None = None,
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
) -> str:
    """Render an object tree to SVG text, optionally writing it to a file."""

    doc = SvgDocument(width=width, height=height, background=background)
    render_object(obj, doc)

    text = doc.tostring()
    if path is not None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    return text


def save_svg(
    obj: Any,
    path: str | Path,
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
) -> Path:
    """Render and save an object tree as SVG."""

    render_svg(obj, path=path, width=width, height=height, background=background)
    return Path(path)


__all__ = [
    "SvgDocument",
    "render_object",
    "render_svg",
    "save_svg",
]
