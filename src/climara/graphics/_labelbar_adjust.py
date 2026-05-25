from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._text_bbox import TextBBox


class LabelBarAdjustGeometryNotImplementedError(NotImplementedError):
    pass


@dataclass(frozen=True)
class LabelBarAdjustGeometryRequest:
    geometry: Any
    title_bbox: TextBBox | None = None
    label_bbox: TextBBox | None = None
    justification: Any = "CenterCenter"


@dataclass(frozen=True)
class LabelBarAdjustGeometryResult:
    request: LabelBarAdjustGeometryRequest
    writeback_semantics: Any
    final_view_bbox: TextBBox
    final_adjusted_bar_bbox: TextBBox
    final_adjusted_label_bbox: TextBBox | None
    final_adjusted_title_bbox: TextBBox | None
    final_box_locs: tuple[float, ...]
    final_label_locs: tuple[float, ...]
    final_label_const_pos: float | None
    final_title_x: float | None
    final_title_y: float | None
    x_offset: float
    y_offset: float
    major_offset: float
    minor_offset: float


def has_labelbar_adjust_geometry_engine() -> bool:
    return False


def build_labelbar_adjust_geometry_request(
    geometry: Any,
    *,
    title_bbox: TextBBox | None = None,
    label_bbox: TextBBox | None = None,
    justification: Any = "CenterCenter",
) -> LabelBarAdjustGeometryRequest:
    return LabelBarAdjustGeometryRequest(
        geometry=geometry,
        title_bbox=title_bbox,
        label_bbox=label_bbox,
        justification=justification,
    )


def adjust_labelbar_geometry_for_text(
    request: LabelBarAdjustGeometryRequest,
) -> LabelBarAdjustGeometryResult:
    from ._labelbar_adjust_writeback_semantics import (
        compute_labelbar_adjust_writeback_semantics,
    )

    writeback = compute_labelbar_adjust_writeback_semantics(
        request,
        justification=request.justification,
    )
    perimeter = writeback.perimeter_semantics

    return LabelBarAdjustGeometryResult(
        request=request,
        writeback_semantics=writeback,
        final_view_bbox=writeback.final_view_bbox,
        final_adjusted_bar_bbox=perimeter.final_adjusted_bar_bbox,
        final_adjusted_label_bbox=perimeter.final_adjusted_label_bbox,
        final_adjusted_title_bbox=perimeter.final_adjusted_title_bbox,
        final_box_locs=writeback.final_box_locs,
        final_label_locs=writeback.final_label_locs,
        final_label_const_pos=writeback.final_label_const_pos,
        final_title_x=writeback.final_title_x,
        final_title_y=writeback.final_title_y,
        x_offset=perimeter.x_offset,
        y_offset=perimeter.y_offset,
        major_offset=perimeter.major_offset,
        minor_offset=perimeter.minor_offset,
    )


__all__ = [
    "LabelBarAdjustGeometryNotImplementedError",
    "LabelBarAdjustGeometryRequest",
    "LabelBarAdjustGeometryResult",
    "adjust_labelbar_geometry_for_text",
    "build_labelbar_adjust_geometry_request",
    "has_labelbar_adjust_geometry_engine",
]
