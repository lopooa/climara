from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from ._labelbar_adjust import LabelBarAdjustGeometryRequest
from ._labelbar_geometry import LabelBarGeometry, NdcRect
from ._text_bbox import TextBBox, build_text_bbox, union_text_bboxes


@dataclass(frozen=True)
class LabelBarAdjustBoxSemantics:
    labelbar_bbox: TextBBox
    bar_and_labels_bbox: TextBBox
    adjusted_bar_bbox: TextBBox
    adjusted_label_bbox: TextBBox | None
    adjusted_title_bbox: TextBBox | None
    label_pos_offset: float
    center_offset: float
    title_x: float | None
    title_y: float | None


def _rect_to_bbox(rect: NdcRect) -> TextBBox:
    return build_text_bbox(
        l=rect.l,
        r=rect.r,
        b=rect.b,
        t=rect.t,
    )


def _shift_bbox(box: TextBBox, *, dx: float = 0.0, dy: float = 0.0) -> TextBBox:
    return build_text_bbox(
        l=box.l + dx,
        r=box.r + dx,
        b=box.b + dy,
        t=box.t + dy,
        coordinate_space=box.coordinate_space,
    )


def _finite(value: float) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError("LabelBar AdjustGeometry semantics require finite coordinates")
    return out


def _box_union(*boxes: TextBBox) -> TextBBox:
    return union_text_bboxes(boxes)


def _key(value: Any) -> str:
    return str(value).strip().replace("_", "").replace("-", "").lower()


def _infer_label_offset_ndc(geometry: LabelBarGeometry) -> float:
    orientation = _key(geometry.orientation)
    label_pos = _key(geometry.label_position)

    if orientation == "horizontal":
        if label_pos == "top":
            return geometry.label_const_pos - geometry.labels_area.b
        if label_pos == "bottom":
            return geometry.labels_area.t - geometry.label_const_pos
        return 0.0

    if label_pos == "right":
        return geometry.label_const_pos - geometry.labels_area.l
    if label_pos == "left":
        return geometry.labels_area.r - geometry.label_const_pos
    return 0.0


def _bar_and_labels_bbox_before_labels(geometry: LabelBarGeometry) -> TextBBox:
    box = _rect_to_bbox(geometry.adj_perim)

    if not geometry.title_on:
        return box

    title_pos = _key(geometry.title_position)
    title_area = geometry.title_area
    off = geometry.title_offset_ndc

    if title_pos == "top":
        return build_text_bbox(l=box.l, r=box.r, b=box.b, t=title_area.b - off)
    if title_pos == "bottom":
        return build_text_bbox(l=box.l, r=box.r, b=title_area.t + off, t=box.t)
    if title_pos == "left":
        return build_text_bbox(l=title_area.r + off, r=box.r, b=box.b, t=box.t)
    if title_pos == "right":
        return build_text_bbox(l=box.l, r=title_area.l - off, b=box.b, t=box.t)

    return box


def _position_label_bbox_against_bar(
    geometry: LabelBarGeometry,
    label_bbox: TextBBox,
) -> tuple[TextBBox, float]:
    orientation = _key(geometry.orientation)
    label_pos = _key(geometry.label_position)
    off = _infer_label_offset_ndc(geometry)

    if orientation == "horizontal":
        if label_pos == "top":
            pos_offset = geometry.adj_bar.t + off - label_bbox.b
            return _shift_bbox(label_bbox, dy=pos_offset), pos_offset

        if label_pos == "bottom":
            pos_offset = geometry.adj_bar.b - off - label_bbox.t
            return _shift_bbox(label_bbox, dy=pos_offset), pos_offset

        return label_bbox, 0.0

    if label_pos == "right":
        pos_offset = geometry.adj_bar.r + off - label_bbox.l
        return _shift_bbox(label_bbox, dx=pos_offset), pos_offset

    if label_pos == "left":
        pos_offset = geometry.adj_bar.l - off - label_bbox.r
        return _shift_bbox(label_bbox, dx=pos_offset), pos_offset

    return label_bbox, 0.0


def _center_bar_and_labels(
    geometry: LabelBarGeometry,
    labelbar_bbox: TextBBox,
    tmp_bbox: TextBBox,
    adjusted_bar: TextBBox,
    adjusted_label: TextBBox | None,
    pos_offset: float,
) -> tuple[TextBBox, TextBBox | None, float, float]:
    orientation = _key(geometry.orientation)

    if orientation == "horizontal":
        center_offset = (
            labelbar_bbox.t - tmp_bbox.t
            + labelbar_bbox.b - tmp_bbox.b
        ) / 2.0
        adjusted_bar = _shift_bbox(adjusted_bar, dy=center_offset)
        adjusted_label = None if adjusted_label is None else _shift_bbox(adjusted_label, dy=center_offset)
        pos_offset += center_offset
        return adjusted_bar, adjusted_label, pos_offset, center_offset

    center_offset = (
        labelbar_bbox.r - tmp_bbox.r
        + labelbar_bbox.l - tmp_bbox.l
    ) / 2.0
    adjusted_bar = _shift_bbox(adjusted_bar, dx=center_offset)
    adjusted_label = None if adjusted_label is None else _shift_bbox(adjusted_label, dx=center_offset)
    pos_offset += center_offset
    return adjusted_bar, adjusted_label, pos_offset, center_offset


def _align_title_with_labelbar_bbox(
    geometry: LabelBarGeometry,
    labelbar_bbox: TextBBox,
    title_bbox: TextBBox,
) -> tuple[TextBBox, float, float]:
    title_item = geometry.title_text_item
    if title_item is None:
        return title_bbox, None, None  # type: ignore[return-value]

    original_x = float(title_item.x)
    original_y = float(title_item.y)
    title_x = original_x
    title_y = original_y

    title_pos = _key(geometry.title_position)
    title_just = _key(geometry.title_just)
    off = geometry.title_offset_ndc

    if title_pos == "bottom" and title_bbox.t > labelbar_bbox.b - off:
        title_y -= title_bbox.t + off - labelbar_bbox.b
    elif title_pos == "top" and title_bbox.b < labelbar_bbox.t + off:
        title_y += labelbar_bbox.t + off - title_bbox.b
    elif title_pos == "left" and title_bbox.r > labelbar_bbox.l - off:
        title_x -= title_bbox.r + off - labelbar_bbox.l
    elif title_pos == "right" and title_bbox.l < labelbar_bbox.r:
        title_x += labelbar_bbox.r + off - title_bbox.l

    if title_pos in {"top", "bottom"}:
        if title_just in {"bottomleft", "centerleft", "topleft"}:
            title_x = labelbar_bbox.l
        elif title_just in {"bottomright", "centerright", "topright"}:
            title_x = labelbar_bbox.r
        else:
            title_x = labelbar_bbox.l + (labelbar_bbox.r - labelbar_bbox.l) / 2.0

    elif title_pos in {"left", "right"}:
        if title_just in {"bottomleft", "bottomcenter", "bottomright"}:
            title_y = labelbar_bbox.b
        elif title_just in {"topleft", "topcenter", "topright"}:
            title_y = labelbar_bbox.t
        else:
            title_y = labelbar_bbox.b + (labelbar_bbox.t - labelbar_bbox.b) / 2.0

    shifted = _shift_bbox(
        title_bbox,
        dx=title_x - original_x,
        dy=title_y - original_y,
    )

    return shifted, title_x, title_y


def compute_labelbar_adjust_box_semantics(
    request: LabelBarAdjustGeometryRequest,
) -> LabelBarAdjustBoxSemantics:
    geometry = request.geometry

    if not isinstance(geometry, LabelBarGeometry):
        raise TypeError("Expected LabelBarGeometry in LabelBarAdjustGeometryRequest")

    bar_and_labels = _bar_and_labels_bbox_before_labels(geometry)
    adjusted_bar = _rect_to_bbox(geometry.adj_bar)

    if request.label_bbox is None:
        adjusted_label = None
        tmp_bbox = adjusted_bar
        pos_offset = 0.0
    else:
        adjusted_label, pos_offset = _position_label_bbox_against_bar(
            geometry,
            request.label_bbox,
        )
        tmp_bbox = _box_union(adjusted_label, adjusted_bar)

    labelbar_bbox = _box_union(tmp_bbox, bar_and_labels)

    adjusted_bar, adjusted_label, pos_offset, center_offset = _center_bar_and_labels(
        geometry,
        labelbar_bbox,
        tmp_bbox,
        adjusted_bar,
        adjusted_label,
        pos_offset,
    )

    adjusted_title = None
    title_x = None
    title_y = None

    if request.title_bbox is not None and geometry.title_on:
        adjusted_title, title_x, title_y = _align_title_with_labelbar_bbox(
            geometry,
            labelbar_bbox,
            request.title_bbox,
        )
        labelbar_bbox = _box_union(labelbar_bbox, adjusted_title)

    for value in (
        labelbar_bbox.l,
        labelbar_bbox.r,
        labelbar_bbox.b,
        labelbar_bbox.t,
        adjusted_bar.l,
        adjusted_bar.r,
        adjusted_bar.b,
        adjusted_bar.t,
        pos_offset,
        center_offset,
    ):
        _finite(value)

    return LabelBarAdjustBoxSemantics(
        labelbar_bbox=labelbar_bbox,
        bar_and_labels_bbox=bar_and_labels,
        adjusted_bar_bbox=adjusted_bar,
        adjusted_label_bbox=adjusted_label,
        adjusted_title_bbox=adjusted_title,
        label_pos_offset=pos_offset,
        center_offset=center_offset,
        title_x=title_x,
        title_y=title_y,
    )


__all__ = [
    "LabelBarAdjustBoxSemantics",
    "compute_labelbar_adjust_box_semantics",
]
