from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._labelbar_semantics import (
    LABEL_ALIGNMENT_BOX_CENTERS,
    LABEL_ALIGNMENT_EXTERNAL_EDGES,
    LABEL_ALIGNMENT_INTERIOR_EDGES,
    ORIENTATION_HORIZONTAL,
    ORIENTATION_VERTICAL,
    NCL_LABELBAR_DEFAULT_TITLE,
    TITLE_DIRECTION_DOWN,
    TITLE_POSITION_BOTTOM,
    TITLE_POSITION_LEFT,
    TITLE_POSITION_RIGHT,
    TITLE_POSITION_TOP,
    label_count_for_alignment,
    label_indices_for_stride,
    normalize_box_count,
    normalize_label_alignment,
    normalize_label_stride,
    normalize_orientation,
    normalize_title_direction,
    normalize_title_position,
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
class NdcTextItemSpec:
    x: float
    y: float
    text: str
    real_string: str
    direction: str
    angle: float
    just: str
    font: Any
    font_color: Any
    font_height: float
    font_aspect: float
    font_thickness: float
    font_quality: Any
    quality_index: int
    constant_spacing: float
    func_code: str


@dataclass(frozen=True)
class LabelBarGeometry:
    perim: NdcRect
    adj_perim: NdcRect
    title_area: NdcRect
    title_on: bool
    title_position: str
    title_offset_ndc: float
    title_text_position: NdcTextPlacement | None
    title_angle: float
    title_just: str
    title_direction: str
    title_text_item: NdcTextItemSpec | None
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


TITLE_LOCATION_NONE = "NoTitle"
TITLE_LOCATION_MAJOR_AXIS = "MajorAxis"
TITLE_LOCATION_MINOR_AXIS = "MinorAxis"


def _title_location(orientation: str, title_position: str, title_on: bool) -> str:
    if not title_on:
        return TITLE_LOCATION_NONE

    if orientation == ORIENTATION_HORIZONTAL:
        if title_position in {TITLE_POSITION_LEFT, TITLE_POSITION_RIGHT}:
            return TITLE_LOCATION_MAJOR_AXIS
        return TITLE_LOCATION_MINOR_AXIS

    if title_position in {TITLE_POSITION_LEFT, TITLE_POSITION_RIGHT}:
        return TITLE_LOCATION_MINOR_AXIS
    return TITLE_LOCATION_MAJOR_AXIS


def _title_rect(
    adj_perim: NdcRect,
    orientation: str,
    title_position: str,
    title_location: str,
    title_ext_ndc: float,
) -> NdcRect:
    if title_location == TITLE_LOCATION_NONE:
        return adj_perim

    if orientation == ORIENTATION_HORIZONTAL:
        if title_location == TITLE_LOCATION_MAJOR_AXIS:
            if title_position == TITLE_POSITION_LEFT:
                return NdcRect(adj_perim.l, adj_perim.l + title_ext_ndc, adj_perim.b, adj_perim.t)
            return NdcRect(adj_perim.r - title_ext_ndc, adj_perim.r, adj_perim.b, adj_perim.t)

        if title_position == TITLE_POSITION_BOTTOM:
            return NdcRect(adj_perim.l, adj_perim.r, adj_perim.b, adj_perim.b + title_ext_ndc)
        return NdcRect(adj_perim.l, adj_perim.r, adj_perim.t - title_ext_ndc, adj_perim.t)

    if title_location == TITLE_LOCATION_MAJOR_AXIS:
        if title_position == TITLE_POSITION_BOTTOM:
            return NdcRect(adj_perim.l, adj_perim.r, adj_perim.b, adj_perim.b + title_ext_ndc)
        return NdcRect(adj_perim.l, adj_perim.r, adj_perim.t - title_ext_ndc, adj_perim.t)

    if title_position == TITLE_POSITION_LEFT:
        return NdcRect(adj_perim.l, adj_perim.l + title_ext_ndc, adj_perim.b, adj_perim.t)
    return NdcRect(adj_perim.r - title_ext_ndc, adj_perim.r, adj_perim.b, adj_perim.t)



_TITLE_JUST_ALIASES = {
    "bottomleft": "BottomLeft",
    "bottomcenter": "BottomCenter",
    "bottomright": "BottomRight",
    "centerleft": "CenterLeft",
    "centercenter": "CenterCenter",
    "centerright": "CenterRight",
    "topleft": "TopLeft",
    "topcenter": "TopCenter",
    "topright": "TopRight",
    "nhlbottomleft": "BottomLeft",
    "nhlbottomcenter": "BottomCenter",
    "nhlbottomright": "BottomRight",
    "nhlcenterleft": "CenterLeft",
    "nhlcentercenter": "CenterCenter",
    "nhlcenterright": "CenterRight",
    "nhltopleft": "TopLeft",
    "nhltopcenter": "TopCenter",
    "nhltopright": "TopRight",
}


def _normalize_title_just(value: Any | None) -> str:
    if value is None:
        return "CenterCenter"

    key = _norm_key(value).replace("_", "")
    if key not in _TITLE_JUST_ALIASES:
        raise ValueError(f"Unsupported lbTitleJust: {value!r}")

    return _TITLE_JUST_ALIASES[key]


def _title_text_xy(area: NdcRect, just: str) -> tuple[float, float]:
    if just.endswith("Left"):
        x = area.l
    elif just.endswith("Right"):
        x = area.r
    else:
        x = area.l + area.width / 2.0

    if just.startswith("Bottom"):
        y = area.b
    elif just.startswith("Top"):
        y = area.t
    else:
        y = area.b + area.height / 2.0

    return x, y


def _resolve_title_string(obj: Any, title_on: bool) -> str:
    value = _pick(
        obj,
        "lbTitleString",
        getattr(obj, "title_string", NCL_LABELBAR_DEFAULT_TITLE),
    )

    if value is None:
        value = NCL_LABELBAR_DEFAULT_TITLE

    value = str(value)

    if title_on and value == NCL_LABELBAR_DEFAULT_TITLE:
        return str(getattr(obj, "name", "labelbar"))

    return value


def _non_negative_num(value: Any, default: float) -> float:
    out = _num(value, default)
    if out < 0.0:
        return 0.0
    return out


def _func_code(value: Any) -> str:
    if value is None:
        return "~"
    out = str(value)
    if not out:
        return "~"
    return out[0]


def _text_item_real_string(text: str, direction: str, func_code: str) -> str:
    dir_code = "D" if direction == TITLE_DIRECTION_DOWN else "A"
    return f"{func_code}{dir_code}{func_code}{text}"


_TEXT_QUALITY_INDEX = {
    "high": 0,
    "nhlhigh": 0,
    "medium": 1,
    "nhlmedium": 1,
    "low": 2,
    "nhllow": 2,
    "workstation": 3,
    "nhlworkstation": 3,
}


def _text_quality_index(value: Any) -> int:
    key = _norm_key(value)
    if key not in _TEXT_QUALITY_INDEX:
        raise ValueError(f"Unsupported TextItem font quality: {value!r}")
    return _TEXT_QUALITY_INDEX[key]


def _title_text_item_spec(
    obj: Any,
    placement: NdcTextPlacement,
    *,
    direction: str,
    angle: float,
    just: str,
) -> NdcTextItemSpec:
    font_height = _num(_pick(obj, "lbTitleFontHeightF", 0.025), 0.025)
    if font_height <= 0.0:
        font_height = 0.025

    func_code = _func_code(_pick(obj, "lbTitleFuncCode", "~"))
    font_quality = _pick(obj, "lbTitleFontQuality", "High")

    return NdcTextItemSpec(
        x=placement.x,
        y=placement.y,
        text=placement.text,
        real_string=_text_item_real_string(placement.text, direction, func_code),
        direction=direction,
        angle=angle,
        just=just,
        font=_pick(obj, "lbTitleFont", 21),
        font_color=_pick(obj, "lbTitleFontColor", "Foreground"),
        font_height=font_height,
        font_aspect=_num(_pick(obj, "lbTitleFontAspectF", 1.3125), 1.3125),
        font_thickness=_num(_pick(obj, "lbTitleFontThicknessF", 1.0), 1.0),
        font_quality=font_quality,
        quality_index=_text_quality_index(font_quality),
        constant_spacing=_non_negative_num(_pick(obj, "lbTitleConstantSpacingF", 0.0), 0.0),
        func_code=func_code,
    )



def _build_base_geometry(
    obj: Any,
) -> tuple[NdcRect, NdcRect, NdcRect, bool, str, float, NdcRect, NdcRect, NdcSize, str, str]:
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

    auto_manage = _bool(_pick(obj, "lbAutoManage", True), True)
    title_on = _bool(_pick(obj, "lbTitleOn", False), False)
    title_position = normalize_title_position(_pick(obj, "lbTitlePosition", None))
    title_extent = _num(_pick(obj, "lbTitleExtentF", 0.15), 0.15)
    title_offset = _num(_pick(obj, "lbTitleOffsetF", 0.03), 0.03)

    if auto_manage and title_extent + title_offset > 0.5:
        title_extent = 0.15
        title_offset = 0.03

    title_location = _title_location(orientation, title_position, title_on and title_extent > 0.0)

    if title_location == TITLE_LOCATION_NONE:
        title_ext_ndc = 0.0
        title_offset_ndc = 0.0
    elif orientation == ORIENTATION_HORIZONTAL:
        if title_location == TITLE_LOCATION_MAJOR_AXIS:
            title_ext_ndc = title_extent * adj_perim.width
            title_offset_ndc = title_offset * adj_perim.width
        else:
            title_ext_ndc = title_extent * adj_perim.height
            title_offset_ndc = title_offset * adj_perim.height
    else:
        if title_location == TITLE_LOCATION_MINOR_AXIS:
            title_ext_ndc = title_extent * adj_perim.width
            title_offset_ndc = title_offset * adj_perim.width
        else:
            title_ext_ndc = title_extent * adj_perim.height
            title_offset_ndc = title_offset * adj_perim.height

    title_area = _title_rect(
        adj_perim,
        orientation,
        title_position,
        title_location,
        title_ext_ndc,
    )

    labels_on = _bool(_pick(obj, "lbLabelsOn", True), True)
    box_minor = _clamp_resource_fraction(_pick(obj, "lbBoxMinorExtentF", 0.33), 0.33)

    if orientation == ORIENTATION_HORIZONTAL:
        bar_room = max(title_area.height, adj_perim.height)
        bar_ext = box_minor * bar_room

        if title_location == TITLE_LOCATION_MINOR_AXIS and title_ext_ndc + title_offset_ndc + bar_ext > bar_room:
            bar_ext = bar_room - title_ext_ndc - title_offset_ndc

        if title_location == TITLE_LOCATION_MAJOR_AXIS:
            if title_position == TITLE_POSITION_LEFT:
                bar_l = adj_perim.l + title_ext_ndc + title_offset_ndc
                bar_r = adj_perim.r
            else:
                bar_l = adj_perim.l
                bar_r = adj_perim.r - title_ext_ndc - title_offset_ndc
        else:
            bar_l = adj_perim.l
            bar_r = adj_perim.r

        labels_l = bar_l if title_location == TITLE_LOCATION_MAJOR_AXIS else adj_perim.l
        labels_r = bar_r if title_location == TITLE_LOCATION_MAJOR_AXIS else adj_perim.r

        if title_location == TITLE_LOCATION_MINOR_AXIS:
            if title_position == TITLE_POSITION_BOTTOM:
                bar_b = title_area.t + title_offset_ndc
                bar_t = adj_perim.t
            else:
                bar_b = adj_perim.b
                bar_t = adj_perim.t - title_ext_ndc - title_offset_ndc
        else:
            bar_b = adj_perim.b
            bar_t = adj_perim.t

        if (not labels_on) or label_position == "Center":
            bar_b = bar_b + (bar_t - bar_b - bar_ext) / 2.0
            bar_t = bar_b + bar_ext
            labels_b = bar_b
            labels_t = bar_t
        elif label_position == "Top":
            labels_t = bar_t
            bar_t = bar_b + bar_ext
            labels_b = bar_t
        else:
            labels_b = bar_b
            bar_b = bar_t - bar_ext
            labels_t = bar_b

        bar = NdcRect(bar_l, bar_r, bar_b, bar_t)
        labels_area = NdcRect(labels_l, labels_r, labels_b, labels_t)

    else:
        bar_room = max(title_area.width, adj_perim.width)
        bar_ext = box_minor * bar_room

        if title_location == TITLE_LOCATION_MINOR_AXIS and title_ext_ndc + title_offset_ndc + bar_ext > bar_room:
            bar_ext = bar_room - title_ext_ndc - title_offset_ndc

        if title_location == TITLE_LOCATION_MAJOR_AXIS:
            if title_position == TITLE_POSITION_BOTTOM:
                bar_b = adj_perim.b + title_ext_ndc + title_offset_ndc
                bar_t = adj_perim.t
            else:
                bar_b = adj_perim.b
                bar_t = adj_perim.t - title_ext_ndc - title_offset_ndc
        else:
            bar_b = adj_perim.b
            bar_t = adj_perim.t

        labels_b = bar_b if title_location == TITLE_LOCATION_MAJOR_AXIS else adj_perim.b
        labels_t = bar_t if title_location == TITLE_LOCATION_MAJOR_AXIS else adj_perim.t

        if title_location == TITLE_LOCATION_MINOR_AXIS:
            if title_position == TITLE_POSITION_LEFT:
                bar_l = title_area.r + title_offset_ndc
                bar_r = adj_perim.r
            else:
                bar_l = adj_perim.l
                bar_r = adj_perim.r - title_ext_ndc - title_offset_ndc
        else:
            bar_l = adj_perim.l
            bar_r = adj_perim.r

        if (not labels_on) or label_position == "Center":
            bar_l = bar_l + (bar_r - bar_l - bar_ext) / 2.0
            bar_r = bar_l + bar_ext
            labels_l = bar_l
            labels_r = bar_r
        elif label_position == "Right":
            labels_r = bar_r
            bar_r = bar_l + bar_ext
            labels_l = bar_r
        else:
            labels_l = bar_l
            bar_l = bar_r - bar_ext
            labels_r = bar_l

        bar = NdcRect(bar_l, bar_r, bar_b, bar_t)
        labels_area = NdcRect(labels_l, labels_r, labels_b, labels_t)

    return (
        perim,
        adj_perim,
        title_area,
        title_on and title_extent > 0.0,
        title_position,
        title_offset_ndc,
        bar,
        labels_area,
        NdcSize(0.0, 0.0),
        orientation,
        label_position,
    )


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

    (
        perim,
        adj_perim,
        title_area,
        title_on,
        title_position,
        title_offset_ndc,
        bar,
        labels_area,
        _,
        orientation,
        label_position,
    ) = _build_base_geometry(obj)

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

    title_angle = _num(_pick(obj, "lbTitleAngleF", getattr(obj, "title_angle", 0.0)), 0.0)
    if title_angle < 0.0:
        title_angle = title_angle + 360.0

    title_just = _normalize_title_just(_pick(obj, "lbTitleJust", "CenterCenter"))
    title_direction = normalize_title_direction(
        _pick(obj, "lbTitleDirection", getattr(obj, "title_direction", None)),
        title_position,
    )

    if title_on:
        title_x, title_y = _title_text_xy(title_area, title_just)
        title_text_position = NdcTextPlacement(
            x=title_x,
            y=title_y,
            text=_resolve_title_string(obj, title_on),
        )
        title_text_item = _title_text_item_spec(
            obj,
            title_text_position,
            direction=title_direction,
            angle=title_angle,
            just=title_just,
        )
    else:
        title_text_position = None
        title_text_item = None

    return LabelBarGeometry(
        perim=perim,
        adj_perim=adj_perim,
        title_area=title_area,
        title_on=title_on,
        title_position=title_position,
        title_offset_ndc=title_offset_ndc,
        title_text_position=title_text_position,
        title_angle=title_angle,
        title_just=title_just,
        title_direction=title_direction,
        title_text_item=title_text_item,
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
