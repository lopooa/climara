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


def _box_separator_lines(
    geometry: LabelBarGeometry,
    svg_width: float,
    svg_height: float,
    stroke: Any,
) -> tuple[SvgLinePrimitive, ...]:
    box_locs = geometry.box_locs

    if len(box_locs) <= 2:
        return ()

    lines: list[SvgLinePrimitive] = []

    if geometry.orientation == "Horizontal":
        for loc in box_locs[1:-1]:
            p1 = ndc_to_svg_point(loc, geometry.adj_bar.b, svg_width, svg_height)
            p2 = ndc_to_svg_point(loc, geometry.adj_bar.t, svg_width, svg_height)
            lines.append(SvgLinePrimitive(p1=p1, p2=p2, stroke=stroke))
    else:
        for loc in box_locs[1:-1]:
            p1 = ndc_to_svg_point(geometry.adj_bar.l, loc, svg_width, svg_height)
            p2 = ndc_to_svg_point(geometry.adj_bar.r, loc, svg_width, svg_height)
            lines.append(SvgLinePrimitive(p1=p1, p2=p2, stroke=stroke))

    return tuple(lines)


def labelbar_geometry_to_svg_primitives(
    geometry: LabelBarGeometry,
    svg_width: float,
    svg_height: float,
    *,
    fills: tuple[Any, ...] | None = None,
    stroke: Any = "black",
    text_fill: Any = "black",
) -> SvgLabelBarPrimitives:
    ndc_polygons = compute_labelbar_box_polygons(geometry)
    polygon_count = len(ndc_polygons)

    fill_values = fills
    if not fill_values:
        fill_values = tuple(None for _ in range(polygon_count))

    if len(fill_values) < polygon_count:
        fill_values = fill_values + tuple(fill_values[-1] for _ in range(polygon_count - len(fill_values)))

    polygons = tuple(
        SvgPolygonPrimitive(
            points=ndc_polygon_to_svg(points, svg_width, svg_height),
            fill=fill_values[index],
            stroke=stroke,
        )
        for index, points in enumerate(ndc_polygons)
    )

    lines = _box_separator_lines(
        geometry,
        svg_width,
        svg_height,
        stroke,
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
