from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._labelbar_geometry import (
    LabelBarGeometry,
    NdcPoint,
    compute_labelbar_box_polygons,
    compute_labelbar_geometry,
)


@dataclass(frozen=True)
class SvgPoint:
    x: float
    y: float


@dataclass(frozen=True)
class SvgPolygonPrimitive:
    points: tuple[SvgPoint, ...]
    fill: Any
    stroke: Any


@dataclass(frozen=True)
class SvgTextPrimitive:
    x: float
    y: float
    text: str
    angle: float
    fill: Any


@dataclass(frozen=True)
class SvgLinePrimitive:
    p1: SvgPoint
    p2: SvgPoint
    stroke: Any


@dataclass(frozen=True)
class SvgLabelBarPrimitives:
    polygons: tuple[SvgPolygonPrimitive, ...]
    lines: tuple[SvgLinePrimitive, ...]
    texts: tuple[SvgTextPrimitive, ...]
    orientation: str
    label_alignment: str
    label_position: str


def ndc_to_svg_point(x: float, y: float, svg_width: float, svg_height: float) -> SvgPoint:
    return SvgPoint(
        x=float(x) * float(svg_width),
        y=(1.0 - float(y)) * float(svg_height),
    )


def ndc_polygon_to_svg(
    points: tuple[NdcPoint, ...],
    svg_width: float,
    svg_height: float,
) -> tuple[SvgPoint, ...]:
    return tuple(
        ndc_to_svg_point(x, y, svg_width, svg_height)
        for x, y in points
    )


def _sequence(value: Any | None) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, str):
        return (value,)
    try:
        return tuple(value)
    except TypeError:
        return (value,)


def _resource_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "off", "no"}
    return bool(value)


def _hollow_fill(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        key = value.strip().lower()
        return "hollow" in key or key in {"none", "transparent", "nofill"}
    return False


def _fill_values(obj: Any, count: int) -> tuple[Any, ...]:
    values = getattr(obj, "fill_colors", None)
    if values is None:
        values = getattr(obj, "colors", None)

    if values is None:
        resources = getattr(obj, "resources", None)
        if isinstance(resources, dict):
            values = resources.get("lbFillColors")

    out = _sequence(values)

    if not out:
        out = tuple(None for _ in range(count))

    if len(out) < count:
        out = out + tuple(out[-1] for _ in range(count - len(out)))

    return out[:count]


def _text_values(obj: Any, count: int) -> tuple[str, ...]:
    resources = getattr(obj, "resources", None)
    if not isinstance(resources, dict):
        resources = {}

    candidates = [
        getattr(obj, "visible_label_strings", None),
        getattr(obj, "label_strings", None),
        getattr(obj, "labels", None),
        getattr(obj, "levels", None),
        resources.get("lbLabelStrings"),
        resources.get("levels"),
        resources.get("lbLevels"),
    ]

    for candidate in candidates:
        values = tuple(str(item) for item in _sequence(candidate))
        if values:
            if len(values) < count:
                values = values + tuple(values[-1] for _ in range(count - len(values)))
            return values[:count]

    return tuple(f"Label_{index}" for index in range(count))


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    svg_width: float,
    svg_height: float,
    stroke: Any,
) -> SvgLinePrimitive:
    return SvgLinePrimitive(
        p1=ndc_to_svg_point(x1, y1, svg_width, svg_height),
        p2=ndc_to_svg_point(x2, y2, svg_width, svg_height),
        stroke=stroke,
    )


def _box_lines(
    geometry: LabelBarGeometry,
    svg_width: float,
    svg_height: float,
    *,
    box_lines_on: bool,
    box_separator_lines_on: bool,
    stroke: Any,
) -> tuple[SvgLinePrimitive, ...]:
    if not box_lines_on:
        return ()

    lines: list[SvgLinePrimitive] = []

    l = geometry.adj_bar.l
    r = geometry.adj_bar.r
    b = geometry.adj_bar.b
    t = geometry.adj_bar.t

    lines.append(_line(l, b, r, b, svg_width, svg_height, stroke))
    lines.append(_line(r, b, r, t, svg_width, svg_height, stroke))
    lines.append(_line(r, t, l, t, svg_width, svg_height, stroke))
    lines.append(_line(l, t, l, b, svg_width, svg_height, stroke))

    if box_separator_lines_on:
        if geometry.orientation == "Horizontal":
            for loc in geometry.box_locs[1:-1]:
                lines.append(_line(loc, b, loc, t, svg_width, svg_height, stroke))
        else:
            for loc in geometry.box_locs[1:-1]:
                lines.append(_line(l, loc, r, loc, svg_width, svg_height, stroke))

    return tuple(lines)


def _perim_polygon(
    geometry: LabelBarGeometry,
    svg_width: float,
    svg_height: float,
    *,
    fill: Any,
    stroke: Any,
) -> SvgPolygonPrimitive:
    points = (
        (geometry.perim.l, geometry.perim.b),
        (geometry.perim.r, geometry.perim.b),
        (geometry.perim.r, geometry.perim.t),
        (geometry.perim.l, geometry.perim.t),
        (geometry.perim.l, geometry.perim.b),
    )
    return SvgPolygonPrimitive(
        points=ndc_polygon_to_svg(points, svg_width, svg_height),
        fill=fill,
        stroke=stroke,
    )


def labelbar_geometry_to_svg_primitives(
    geometry: LabelBarGeometry,
    svg_width: float,
    svg_height: float,
    *,
    fills: tuple[Any, ...] | None = None,
    stroke: Any = "black",
    text_fill: Any = "black",
    box_lines_on: bool = True,
    box_separator_lines_on: bool = True,
    box_line_stroke: Any | None = None,
    perim_on: bool = False,
    perim_fill: Any = "none",
    perim_stroke: Any = "black",
) -> SvgLabelBarPrimitives:
    ndc_polygons = compute_labelbar_box_polygons(geometry)
    polygon_count = len(ndc_polygons)

    fill_values = fills
    if not fill_values:
        fill_values = tuple(None for _ in range(polygon_count))

    if len(fill_values) < polygon_count:
        fill_values = fill_values + tuple(fill_values[-1] for _ in range(polygon_count - len(fill_values)))

    box_polygons = tuple(
        SvgPolygonPrimitive(
            points=ndc_polygon_to_svg(points, svg_width, svg_height),
            fill=fill_values[index],
            stroke="none",
        )
        for index, points in enumerate(ndc_polygons)
    )

    if perim_on:
        polygons = (
            _perim_polygon(
                geometry,
                svg_width,
                svg_height,
                fill=perim_fill,
                stroke=perim_stroke,
            ),
        ) + box_polygons
    else:
        polygons = box_polygons

    if box_line_stroke is None:
        box_line_stroke = stroke

    lines = _box_lines(
        geometry,
        svg_width,
        svg_height,
        box_lines_on=box_lines_on,
        box_separator_lines_on=box_separator_lines_on,
        stroke=box_line_stroke,
    )

    text_values = tuple(item.text for item in geometry.label_text_positions)

    texts = tuple(
        SvgTextPrimitive(
            x=ndc_to_svg_point(item.x, item.y, svg_width, svg_height).x,
            y=ndc_to_svg_point(item.x, item.y, svg_width, svg_height).y,
            text=text_values[index],
            angle=geometry.label_angle,
            fill=text_fill,
        )
        for index, item in enumerate(geometry.label_text_positions)
    )

    return SvgLabelBarPrimitives(
        polygons=polygons,
        lines=lines,
        texts=texts,
        orientation=geometry.orientation,
        label_alignment=geometry.label_alignment,
        label_position=geometry.label_position,
    )


def labelbar_to_svg_primitives(
    obj: Any,
    svg_width: float,
    svg_height: float,
    *,
    stroke: Any = "black",
    text_fill: Any = "black",
) -> SvgLabelBarPrimitives:
    if hasattr(obj, "compute_geometry"):
        geometry = obj.compute_geometry()
    else:
        geometry = compute_labelbar_geometry(obj)

    fills = _fill_values(obj, len(compute_labelbar_box_polygons(geometry)))
    text_values = _text_values(obj, len(geometry.label_text_positions))

    resources = getattr(obj, "resources", None)
    if not isinstance(resources, dict):
        resources = {}

    box_lines_on = _resource_bool(resources.get("lbBoxLinesOn"), True)
    box_separator_lines_on = _resource_bool(resources.get("lbBoxSeparatorLinesOn"), True)
    box_line_stroke = resources.get("lbBoxLineColor", stroke)

    perim_on = _resource_bool(resources.get("lbPerimOn"), False)
    perim_stroke = resources.get("lbPerimColor", stroke)

    if _hollow_fill(resources.get("lbPerimFill", "HollowFill")):
        perim_fill = "none"
    else:
        perim_fill = resources.get("lbPerimFillColor", "none")

    geometry = type(geometry)(
        perim=geometry.perim,
        adj_perim=geometry.adj_perim,
        bar=geometry.bar,
        labels_area=geometry.labels_area,
        adj_bar=geometry.adj_bar,
        box_size=geometry.box_size,
        adj_box_size=geometry.adj_box_size,
        box_locs=geometry.box_locs,
        label_locs=geometry.label_locs,
        label_const_pos=geometry.label_const_pos,
        visible_label_strings=text_values,
        label_text_positions=tuple(
            type(item)(x=item.x, y=item.y, text=text_values[index])
            for index, item in enumerate(geometry.label_text_positions)
        ),
        multi_text_orientation=geometry.multi_text_orientation,
        label_keep_end_items=geometry.label_keep_end_items,
        label_angle=geometry.label_angle,
        orientation=geometry.orientation,
        label_position=geometry.label_position,
        label_alignment=geometry.label_alignment,
        label_stride=geometry.label_stride,
        label_draw_count=geometry.label_draw_count,
        box_major_extent=geometry.box_major_extent,
        box_end_cap_style=geometry.box_end_cap_style,
    )

    return labelbar_geometry_to_svg_primitives(
        geometry,
        svg_width,
        svg_height,
        fills=fills,
        stroke=stroke,
        text_fill=text_fill,
        box_lines_on=box_lines_on,
        box_separator_lines_on=box_separator_lines_on,
        box_line_stroke=box_line_stroke,
        perim_on=perim_on,
        perim_fill=perim_fill,
        perim_stroke=perim_stroke,
    )


__all__ = [
    "SvgLabelBarPrimitives",
    "SvgLinePrimitive",
    "SvgPoint",
    "SvgPolygonPrimitive",
    "SvgTextPrimitive",
    "labelbar_geometry_to_svg_primitives",
    "labelbar_to_svg_primitives",
    "ndc_polygon_to_svg",
    "ndc_to_svg_point",
]
