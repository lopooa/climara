from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from ._labelbar_adjust import LabelBarAdjustGeometryRequest
from ._labelbar_adjust_semantics import (
    LabelBarAdjustBoxSemantics,
    compute_labelbar_adjust_box_semantics,
)
from ._labelbar_geometry import LabelBarGeometry, NdcRect
from ._text_bbox import TextBBox, build_text_bbox


@dataclass(frozen=True)
class LabelBarAdjustPerimeterSemantics:
    box_semantics: LabelBarAdjustBoxSemantics
    shifted_labelbar_bbox: TextBBox
    external_perim_bbox: TextBBox
    nominal_perim_bbox: TextBBox
    final_adjusted_bar_bbox: TextBBox
    final_adjusted_label_bbox: TextBBox | None
    final_adjusted_title_bbox: TextBBox | None
    final_labelbar_view_bbox: TextBBox
    x_offset: float
    y_offset: float
    major_offset: float
    minor_offset: float


def _key(value: Any) -> str:
    return str(value).strip().replace("_", "").replace("-", "").lower()


def _bbox(
    *,
    l: float,
    r: float,
    b: float,
    t: float,
    coordinate_space: str = "ndc",
) -> TextBBox:
    return build_text_bbox(
        l=float(l),
        r=float(r),
        b=float(b),
        t=float(t),
        coordinate_space=coordinate_space,
    )


def _shift_bbox(box: TextBBox, *, dx: float = 0.0, dy: float = 0.0) -> TextBBox:
    return _bbox(
        l=box.l + dx,
        r=box.r + dx,
        b=box.b + dy,
        t=box.t + dy,
        coordinate_space=box.coordinate_space,
    )


def _rect_width(rect: NdcRect) -> float:
    return rect.r - rect.l


def _rect_height(rect: NdcRect) -> float:
    return rect.t - rect.b


def _perim_margin_offsets(geometry: LabelBarGeometry) -> tuple[float, float, float, float]:
    left = geometry.adj_perim.l - geometry.perim.l
    right = geometry.perim.r - geometry.adj_perim.r
    bottom = geometry.adj_perim.b - geometry.perim.b
    top = geometry.perim.t - geometry.adj_perim.t
    return left, right, bottom, top


def _external_perim_from_labelbar_bbox(
    geometry: LabelBarGeometry,
    labelbar_bbox: TextBBox,
) -> TextBBox:
    margin_l, margin_r, margin_b, margin_t = _perim_margin_offsets(geometry)

    return _bbox(
        l=labelbar_bbox.l - margin_l,
        r=labelbar_bbox.r + margin_r,
        b=labelbar_bbox.b - margin_b,
        t=labelbar_bbox.t + margin_t,
        coordinate_space=labelbar_bbox.coordinate_space,
    )


def _justification_offsets(
    geometry: LabelBarGeometry,
    external_perim: TextBBox,
    justification: Any,
) -> tuple[float, float]:
    just = _key(justification)

    perim = geometry.perim
    perim_center_x = perim.l + _rect_width(perim) / 2.0
    perim_center_y = perim.b + _rect_height(perim) / 2.0

    external_center_x = external_perim.l + external_perim.width / 2.0
    external_center_y = external_perim.b + external_perim.height / 2.0

    if just == "bottomleft":
        return external_perim.l - perim.l, external_perim.b - perim.b
    if just == "centerleft":
        return external_perim.l - perim.l, external_center_y - perim_center_y
    if just == "topleft":
        return external_perim.l - perim.l, external_perim.t - perim.t

    if just == "bottomcenter":
        return external_center_x - perim_center_x, external_perim.b - perim.b
    if just == "topcenter":
        return external_center_x - perim_center_x, external_perim.t - perim.t

    if just == "bottomright":
        return external_perim.r - perim.r, external_perim.b - perim.b
    if just == "centerright":
        return external_perim.r - perim.r, external_center_y - perim_center_y
    if just == "topright":
        return external_perim.r - perim.r, external_perim.t - perim.t

    return external_center_x - perim_center_x, external_center_y - perim_center_y


def _nominal_perim_from_external(
    geometry: LabelBarGeometry,
    external_perim: TextBBox,
    justification: Any,
) -> TextBBox:
    just = _key(justification)

    p_width = _rect_width(geometry.perim)
    p_height = _rect_height(geometry.perim)

    ex_width = max(0.0, external_perim.width - p_width)
    ex_height = max(0.0, external_perim.height - p_height)

    if just == "bottomleft":
        l = external_perim.l
        b = external_perim.b
    elif just == "centerleft":
        l = external_perim.l
        b = external_perim.b + ex_height / 2.0
    elif just == "topleft":
        l = external_perim.l
        b = external_perim.b + ex_height

    elif just == "bottomcenter":
        l = external_perim.l + ex_width / 2.0
        b = external_perim.b
    elif just == "topcenter":
        l = external_perim.l + ex_width / 2.0
        b = external_perim.b + ex_height

    elif just == "bottomright":
        l = external_perim.l + ex_width
        b = external_perim.b
    elif just == "centerright":
        l = external_perim.l + ex_width
        # Mirrors LabelBar.c::AdjustGeometry as written in the NCL source.
        b = external_perim.b + ex_width / 2.0
    elif just == "topright":
        l = external_perim.l + ex_width
        b = external_perim.b + ex_height

    else:
        l = external_perim.l + ex_width / 2.0
        b = external_perim.b + ex_height / 2.0

    return _bbox(
        l=l,
        r=l + p_width,
        b=b,
        t=b + p_height,
        coordinate_space=external_perim.coordinate_space,
    )


def _assert_finite_bbox(box: TextBBox) -> None:
    for value in (box.l, box.r, box.b, box.t, box.width, box.height):
        if not isfinite(value):
            raise ValueError("LabelBar AdjustGeometry perimeter semantics require finite bbox values")


def compute_labelbar_adjust_perimeter_semantics(
    request: LabelBarAdjustGeometryRequest,
    *,
    justification: Any = "CenterCenter",
) -> LabelBarAdjustPerimeterSemantics:
    geometry = request.geometry

    if not isinstance(geometry, LabelBarGeometry):
        raise TypeError("Expected LabelBarGeometry in LabelBarAdjustGeometryRequest")

    box_semantics = compute_labelbar_adjust_box_semantics(request)

    external_before_shift = _external_perim_from_labelbar_bbox(
        geometry,
        box_semantics.labelbar_bbox,
    )

    x_offset, y_offset = _justification_offsets(
        geometry,
        external_before_shift,
        justification,
    )

    external_perim = _shift_bbox(
        external_before_shift,
        dx=-x_offset,
        dy=-y_offset,
    )

    shifted_labelbar = _shift_bbox(
        box_semantics.labelbar_bbox,
        dx=-x_offset,
        dy=-y_offset,
    )

    nominal_perim = _nominal_perim_from_external(
        geometry,
        external_perim,
        justification,
    )

    final_bar = _shift_bbox(
        box_semantics.adjusted_bar_bbox,
        dx=-x_offset,
        dy=-y_offset,
    )

    final_label = (
        None
        if box_semantics.adjusted_label_bbox is None
        else _shift_bbox(
            box_semantics.adjusted_label_bbox,
            dx=-x_offset,
            dy=-y_offset,
        )
    )

    final_title = (
        None
        if box_semantics.adjusted_title_bbox is None
        else _shift_bbox(
            box_semantics.adjusted_title_bbox,
            dx=-x_offset,
            dy=-y_offset,
        )
    )

    orientation = _key(geometry.orientation)
    if orientation == "horizontal":
        major_offset = x_offset
        minor_offset = y_offset
    else:
        major_offset = y_offset
        minor_offset = x_offset

    final_labelbar_view = external_perim

    for box in (
        shifted_labelbar,
        external_perim,
        nominal_perim,
        final_bar,
        final_label,
        final_title,
        final_labelbar_view,
    ):
        if box is not None:
            _assert_finite_bbox(box)

    return LabelBarAdjustPerimeterSemantics(
        box_semantics=box_semantics,
        shifted_labelbar_bbox=shifted_labelbar,
        external_perim_bbox=external_perim,
        nominal_perim_bbox=nominal_perim,
        final_adjusted_bar_bbox=final_bar,
        final_adjusted_label_bbox=final_label,
        final_adjusted_title_bbox=final_title,
        final_labelbar_view_bbox=final_labelbar_view,
        x_offset=x_offset,
        y_offset=y_offset,
        major_offset=major_offset,
        minor_offset=minor_offset,
    )


__all__ = [
    "LabelBarAdjustPerimeterSemantics",
    "compute_labelbar_adjust_perimeter_semantics",
]
