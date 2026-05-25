from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._labelbar_semantics import (
    LABEL_ALIGNMENT_BOX_CENTERS,
    LABEL_ALIGNMENT_EXTERNAL_EDGES,
    LABEL_ALIGNMENT_INTERIOR_EDGES,
    ORIENTATION_HORIZONTAL,
    ORIENTATION_VERTICAL,
    label_count_for_alignment,
    label_indices_for_stride,
    normalize_box_count,
    normalize_label_alignment,
    normalize_label_stride,
    normalize_orientation,
)


@dataclass(frozen=True)
class NdcRect:
    l: float
    r: float
    b: float
    t: float

    @property
    def width(self) -> float:
        return self.r - self.l

    @property
    def height(self) -> float:
        return self.t - self.b


@dataclass(frozen=True)
class NdcSize:
    x: float
    y: float


@dataclass(frozen=True)
class NdcTextPlacement:
    x: float
    y: float
    text: str


@dataclass(frozen=True)
class LabelBarGeometry:
    perim: NdcRect
    adj_perim: NdcRect
    bar: NdcRect
    labels_area: NdcRect
    adj_bar: NdcRect
    box_size: NdcSize
    adj_box_size: NdcSize
    box_locs: tuple[float, ...]
    label_locs: tuple[float, ...]
    label_const_pos: float
    visible_label_strings: tuple[str, ...]
    label_text_positions: tuple[NdcTextPlacement, ...]
    multi_text_orientation: str
    label_keep_end_items: bool
    label_angle: float
    orientation: str
    label_position: str
    label_alignment: str
    label_stride: int
    label_draw_count: int
    box_major_extent: float
    box_end_cap_style: str


def _resources(obj: Any) -> dict[str, Any]:
    res = getattr(obj, "resources", None)
    if isinstance(res, dict):
        return res
    return {}


def _pick(obj: Any, key: str, default: Any = None) -> Any:
    res = _resources(obj)
    if key in res:
        return res[key]
    return getattr(obj, key, default)


def _num(value: Any, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except Exception:
        return default


def _bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "off", "no"}
    return bool(value)


def _clamp_resource_fraction(value: Any, default: float) -> float:
    out = _num(value, default)
    if out < 0.0 or out > 1.0:
        return default
    return out


BOX_END_CAP_RECTANGLE_ENDS = "RectangleEnds"
BOX_END_CAP_TRIANGLE_LOW_END = "TriangleLowEnd"
BOX_END_CAP_TRIANGLE_HIGH_END = "TriangleHighEnd"
BOX_END_CAP_TRIANGLE_BOTH_ENDS = "TriangleBothEnds"

_BOX_END_CAP_ALIASES = {
    "rectangleends": BOX_END_CAP_RECTANGLE_ENDS,
    "rectangle_ends": BOX_END_CAP_RECTANGLE_ENDS,
    "nhlrectangleends": BOX_END_CAP_RECTANGLE_ENDS,
    "trianglelowend": BOX_END_CAP_TRIANGLE_LOW_END,
    "triangle_low_end": BOX_END_CAP_TRIANGLE_LOW_END,
    "nhltrianglelowend": BOX_END_CAP_TRIANGLE_LOW_END,
    "trianglehighend": BOX_END_CAP_TRIANGLE_HIGH_END,
    "triangle_high_end": BOX_END_CAP_TRIANGLE_HIGH_END,
    "nhltrianglehighend": BOX_END_CAP_TRIANGLE_HIGH_END,
    "trianglebothends": BOX_END_CAP_TRIANGLE_BOTH_ENDS,
    "triangle_both_ends": BOX_END_CAP_TRIANGLE_BOTH_ENDS,
    "nhltrianglebothends": BOX_END_CAP_TRIANGLE_BOTH_ENDS,
}


def _norm_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def normalize_box_end_cap_style(value: Any | None) -> str:
    if value is None:
        return BOX_END_CAP_RECTANGLE_ENDS

    key = _norm_key(value)
    if key not in _BOX_END_CAP_ALIASES:
        raise ValueError(f"Unsupported lbBoxEndCapStyle: {value!r}")

    return _BOX_END_CAP_ALIASES[key]


def _rect_from_view(obj: Any) -> NdcRect:
    rect = getattr(obj, "rect", None)

    if rect is not None:
        vp_x, vp_y, vp_w, vp_h = [float(item) for item in rect]
    else:
        vp_x = _num(_pick(obj, "vpXF", 0.1), 0.1)
        vp_y = _num(_pick(obj, "vpYF", 0.1), 0.1)
        vp_w = _num(_pick(obj, "vpWidthF", 0.8), 0.8)
        vp_h = _num(_pick(obj, "vpHeightF", 0.3), 0.3)

    return NdcRect(
        l=vp_x,
        r=vp_x + vp_w,
        b=vp_y - vp_h,
        t=vp_y,
    )


def _normalize_label_position(value: Any, orientation: str) -> str:
    raw = str(value if value is not None else "Right").strip().lower()

    if orientation == ORIENTATION_HORIZONTAL:
        if raw == "center":
            return "Center"
        if raw in {"bottom", "right"}:
            return "Bottom"
        return "Top"

    if raw == "center":
        return "Center"
    if raw in {"left", "top"}:
        return "Left"
    return "Right"


def _default_label(index: int) -> str:
    return f"Label_{index}"


def _visible_labels(obj: Any, count: int, indices: tuple[int, ...]) -> tuple[str, ...]:
    labels = getattr(obj, "visible_label_strings", None)
    if labels is not None and len(tuple(labels)) == len(indices):
        return tuple(str(item) for item in labels)

    label_strings = getattr(obj, "label_strings", None)
    if label_strings is None:
        label_strings = getattr(obj, "labels", None)

    values = tuple(str(item) for item in (label_strings or ()))

    out = []
    for index in indices:
        if 0 <= index < len(values):
            out.append(values[index])
        else:
            out.append(_default_label(index))

    return tuple(out)


def _build_base_geometry(obj: Any) -> tuple[NdcRect, NdcRect, NdcRect, NdcRect, NdcSize, str, str]:
    perim = _rect_from_view(obj)

    margin_l = _num(_pick(obj, "lbLeftMarginF", 0.05), 0.05)
    margin_r = _num(_pick(obj, "lbRightMarginF", 0.05), 0.05)
    margin_b = _num(_pick(obj, "lbBottomMarginF", 0.05), 0.05)
    margin_t = _num(_pick(obj, "lbTopMarginF", 0.05), 0.05)

    small_axis = min(perim.width, perim.height)

    adj_perim = NdcRect(
        l=perim.l + margin_l * small_axis,
        r=perim.r - margin_r * small_axis,
        b=perim.b + margin_b * small_axis,
        t=perim.t - margin_t * small_axis,
    )

    orientation = normalize_orientation(_pick(obj, "lbOrientation", None))
    label_position = _normalize_label_position(
        _pick(obj, "lbLabelPosition", None),
        orientation,
    )

    labels_on = _bool(_pick(obj, "lbLabelsOn", True), True)
    box_minor = _clamp_resource_fraction(_pick(obj, "lbBoxMinorExtentF", 0.33), 0.33)

    if orientation == ORIENTATION_HORIZONTAL:
        bar_room = adj_perim.height
        bar_ext = box_minor * bar_room

        bar_l = adj_perim.l
        bar_r = adj_perim.r
        labels_l = bar_l
        labels_r = bar_r

        if (not labels_on) or label_position == "Center":
            bar_b = adj_perim.b + (bar_room - bar_ext) / 2.0
            bar_t = bar_b + bar_ext
            labels_b = bar_b
            labels_t = bar_t
        elif label_position == "Top":
            bar_b = adj_perim.b
            bar_t = bar_b + bar_ext
            labels_b = bar_t
            labels_t = adj_perim.t
        else:
            bar_b = adj_perim.t - bar_ext
            bar_t = adj_perim.t
            labels_b = adj_perim.b
            labels_t = bar_b

        bar = NdcRect(bar_l, bar_r, bar_b, bar_t)
        labels_area = NdcRect(labels_l, labels_r, labels_b, labels_t)

    else:
        bar_room = adj_perim.width
        bar_ext = box_minor * bar_room

        bar_b = adj_perim.b
        bar_t = adj_perim.t
        labels_b = bar_b
        labels_t = bar_t

        if (not labels_on) or label_position == "Center":
            bar_l = adj_perim.l + (bar_room - bar_ext) / 2.0
            bar_r = bar_l + bar_ext
            labels_l = bar_l
            labels_r = bar_r
        elif label_position == "Right":
            bar_l = adj_perim.l
            bar_r = bar_l + bar_ext
            labels_l = bar_r
            labels_r = adj_perim.r
        else:
            bar_l = adj_perim.r - bar_ext
            bar_r = adj_perim.r
            labels_l = adj_perim.l
            labels_r = bar_l

        bar = NdcRect(bar_l, bar_r, bar_b, bar_t)
        labels_area = NdcRect(labels_l, labels_r, labels_b, labels_t)

    return perim, adj_perim, bar, labels_area, NdcSize(0.0, 0.0), orientation, label_position


def compute_labelbar_geometry(obj: Any) -> LabelBarGeometry:
    box_count = normalize_box_count(_pick(obj, "lbBoxCount", getattr(obj, "box_count", 16)))
    label_alignment = normalize_label_alignment(
        _pick(obj, "lbLabelAlignment", getattr(obj, "label_alignment", None))
    )
    label_stride = normalize_label_stride(
        _pick(obj, "lbLabelStride", getattr(obj, "label_stride", 1))
    )
    box_major_extent = _clamp_resource_fraction(
        _pick(obj, "lbBoxMajorExtentF", 1.0),
        1.0,
    )
    box_end_cap_style = normalize_box_end_cap_style(
        _pick(obj, "lbBoxEndCapStyle", "RectangleEnds"),
    )

    perim, adj_perim, bar, labels_area, _, orientation, label_position = _build_base_geometry(obj)

    if orientation == ORIENTATION_HORIZONTAL:
        box_size = NdcSize(
            x=bar.width / box_count,
            y=bar.height,
        )
    else:
        box_size = NdcSize(
            x=bar.width,
            y=bar.height / box_count,
        )

    adj_bar = bar
    adj_box_size = box_size

    if label_alignment == LABEL_ALIGNMENT_EXTERNAL_EDGES:
        if orientation == ORIENTATION_HORIZONTAL:
            adj_x = box_size.x * box_count / (box_count + 1.0)
            adj_box_size = NdcSize(adj_x, box_size.y)
            adj_bar = NdcRect(
                l=bar.l + adj_x / 2.0,
                r=bar.r - adj_x / 2.0,
                b=bar.b,
                t=bar.t,
            )
        else:
            adj_y = box_size.y * box_count / (box_count + 1.0)
            adj_box_size = NdcSize(box_size.x, adj_y)
            adj_bar = NdcRect(
                l=bar.l,
                r=bar.r,
                b=bar.b + adj_y / 2.0,
                t=bar.t - adj_y / 2.0,
            )

    elif label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES:
        if orientation == ORIENTATION_HORIZONTAL:
            labels_area = NdcRect(
                l=bar.l + box_size.x / 2.0,
                r=bar.r - box_size.x / 2.0,
                b=labels_area.b,
                t=labels_area.t,
            )
        else:
            labels_area = NdcRect(
                l=labels_area.l,
                r=labels_area.r,
                b=bar.b + box_size.y / 2.0,
                t=bar.t - box_size.y / 2.0,
            )

    if orientation == ORIENTATION_HORIZONTAL:
        box_locs = tuple(adj_bar.l + i * adj_box_size.x for i in range(box_count))
        box_locs = box_locs + (adj_bar.r,)
    else:
        box_locs = tuple(adj_bar.b + i * adj_box_size.y for i in range(box_count))
        box_locs = box_locs + (adj_bar.t,)

    label_off = _num(_pick(obj, "lbLabelOffsetF", 0.1), 0.1)

    if orientation == ORIENTATION_HORIZONTAL:
        label_off_ndc = label_off * adj_perim.height
        if label_position == "Bottom":
            label_const_pos = labels_area.t - label_off_ndc
        elif label_position == "Center":
            label_const_pos = adj_bar.b + adj_box_size.y / 2.0
        else:
            label_const_pos = labels_area.b + label_off_ndc

        base_pos = adj_bar.l
        if label_alignment == LABEL_ALIGNMENT_BOX_CENTERS:
            offset = adj_box_size.x / 2.0
        elif label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES:
            offset = adj_box_size.x
        else:
            offset = 0.0
        increment = adj_box_size.x * label_stride

    else:
        label_off_ndc = label_off * adj_perim.width
        if label_position == "Left":
            label_const_pos = labels_area.r - label_off_ndc
        elif label_position == "Center":
            label_const_pos = adj_bar.l + adj_box_size.x / 2.0
        else:
            label_const_pos = labels_area.l + label_off_ndc

        base_pos = adj_bar.b
        if label_alignment == LABEL_ALIGNMENT_BOX_CENTERS:
            offset = adj_box_size.y / 2.0
        elif label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES:
            offset = adj_box_size.y
        else:
            offset = 0.0
        increment = adj_box_size.y * label_stride

    labels_on = _bool(_pick(obj, "lbLabelsOn", True), True)

    if labels_on:
        label_count = label_count_for_alignment(box_count, label_alignment)
        label_indices = label_indices_for_stride(box_count, label_alignment, label_stride)
        label_draw_count = len(label_indices)
        visible_labels = _visible_labels(obj, label_count, label_indices)

        label_locs = tuple(
            base_pos + offset + i * increment
            for i in range(label_draw_count)
        )

        if orientation == ORIENTATION_HORIZONTAL:
            multi_text_orientation = "YConst"
            label_text_positions = tuple(
                NdcTextPlacement(x=loc, y=label_const_pos, text=label)
                for loc, label in zip(label_locs, visible_labels)
            )
        else:
            multi_text_orientation = "XConst"
            label_text_positions = tuple(
                NdcTextPlacement(x=label_const_pos, y=loc, text=label)
                for loc, label in zip(label_locs, visible_labels)
            )
    else:
        label_draw_count = 0
        visible_labels = ()
        label_locs = ()
        label_text_positions = ()
        multi_text_orientation = "YConst" if orientation == ORIENTATION_HORIZONTAL else "XConst"

    label_keep_end_items = labels_on and label_alignment == LABEL_ALIGNMENT_EXTERNAL_EDGES

    label_angle = _num(_pick(obj, "lbLabelAngleF", 0.0), 0.0)
    if label_angle < 0.0:
        label_angle = label_angle + 360.0

    return LabelBarGeometry(
        perim=perim,
        adj_perim=adj_perim,
        bar=bar,
        labels_area=labels_area,
        adj_bar=adj_bar,
        box_size=box_size,
        adj_box_size=adj_box_size,
        box_locs=box_locs,
        label_locs=label_locs,
        label_const_pos=label_const_pos,
        visible_label_strings=visible_labels,
        label_text_positions=label_text_positions,
        multi_text_orientation=multi_text_orientation,
        label_keep_end_items=label_keep_end_items,
        label_angle=label_angle,
        orientation=orientation,
        label_position=label_position,
        label_alignment=label_alignment,
        label_stride=label_stride,
        label_draw_count=label_draw_count,
        box_major_extent=box_major_extent,
        box_end_cap_style=box_end_cap_style,
    )


NdcPoint = tuple[float, float]
NdcPolygon = tuple[NdcPoint, ...]


def compute_labelbar_box_polygons(geometry: LabelBarGeometry) -> tuple[NdcPolygon, ...]:
    polygons: list[NdcPolygon] = []

    frac = (1.0 - geometry.box_major_extent) / 2.0
    box_count = len(geometry.box_locs) - 1

    for index in range(box_count):
        low = geometry.box_locs[index]
        high = geometry.box_locs[index + 1]
        dist = high - low

        if geometry.orientation == ORIENTATION_HORIZONTAL:
            x0 = low + dist * frac
            x1 = high - dist * frac

            if (
                index == 0
                and geometry.box_end_cap_style
                in {BOX_END_CAP_TRIANGLE_LOW_END, BOX_END_CAP_TRIANGLE_BOTH_ENDS}
            ):
                yc = (geometry.adj_bar.t + geometry.adj_bar.b) / 2.0
                points = (
                    (x0, yc),
                    (x1, geometry.adj_bar.b),
                    (x1, geometry.adj_bar.t),
                    (x0, yc),
                    (x0, yc),
                )
            elif (
                index == box_count - 1
                and geometry.box_end_cap_style
                in {BOX_END_CAP_TRIANGLE_HIGH_END, BOX_END_CAP_TRIANGLE_BOTH_ENDS}
            ):
                yc = (geometry.adj_bar.b + geometry.adj_bar.t) / 2.0
                points = (
                    (x0, geometry.adj_bar.b),
                    (x1, yc),
                    (x1, yc),
                    (x0, geometry.adj_bar.t),
                    (x0, geometry.adj_bar.b),
                )
            else:
                points = (
                    (x0, geometry.adj_bar.b),
                    (x1, geometry.adj_bar.b),
                    (x1, geometry.adj_bar.t),
                    (x0, geometry.adj_bar.t),
                    (x0, geometry.adj_bar.b),
                )

        else:
            y0 = low + dist * frac
            y1 = high - dist * frac

            if (
                index == 0
                and geometry.box_end_cap_style
                in {BOX_END_CAP_TRIANGLE_LOW_END, BOX_END_CAP_TRIANGLE_BOTH_ENDS}
            ):
                xc = (geometry.adj_bar.l + geometry.adj_bar.r) / 2.0
                points = (
                    (xc, y0),
                    (xc, y0),
                    (geometry.adj_bar.r, y1),
                    (geometry.adj_bar.l, y1),
                    (xc, y0),
                )
            elif (
                index == box_count - 1
                and geometry.box_end_cap_style
                in {BOX_END_CAP_TRIANGLE_HIGH_END, BOX_END_CAP_TRIANGLE_BOTH_ENDS}
            ):
                xc = (geometry.adj_bar.l + geometry.adj_bar.r) / 2.0
                points = (
                    (geometry.adj_bar.l, y0),
                    (geometry.adj_bar.r, y0),
                    (xc, y1),
                    (xc, y1),
                    (geometry.adj_bar.l, y0),
                )
            else:
                points = (
                    (geometry.adj_bar.l, y0),
                    (geometry.adj_bar.r, y0),
                    (geometry.adj_bar.r, y1),
                    (geometry.adj_bar.l, y1),
                    (geometry.adj_bar.l, y0),
                )

        polygons.append(points)

    return tuple(polygons)


__all__ = [
    "BOX_END_CAP_RECTANGLE_ENDS",
    "BOX_END_CAP_TRIANGLE_BOTH_ENDS",
    "BOX_END_CAP_TRIANGLE_HIGH_END",
    "BOX_END_CAP_TRIANGLE_LOW_END",
    "LabelBarGeometry",
    "NdcPoint",
    "NdcPolygon",
    "NdcRect",
    "NdcSize",
    "NdcTextPlacement",
    "compute_labelbar_box_polygons",
    "compute_labelbar_geometry",
    "normalize_box_end_cap_style",
]
