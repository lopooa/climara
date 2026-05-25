from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from ._labelbar_adjust import LabelBarAdjustGeometryRequest
from ._labelbar_adjust_perim_semantics import (
    LabelBarAdjustPerimeterSemantics,
    compute_labelbar_adjust_perimeter_semantics,
)
from ._labelbar_geometry import LabelBarGeometry
from ._text_bbox import TextBBox


@dataclass(frozen=True)
class LabelBarAdjustWritebackSemantics:
    perimeter_semantics: LabelBarAdjustPerimeterSemantics
    final_box_locs: tuple[float, ...]
    final_label_locs: tuple[float, ...]
    final_label_const_pos: float | None
    final_title_x: float | None
    final_title_y: float | None
    final_view_bbox: TextBBox


def _finite(value: float) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError("LabelBar AdjustGeometry write-back semantics require finite values")
    return out


def compute_labelbar_adjust_writeback_semantics(
    request: LabelBarAdjustGeometryRequest,
    *,
    justification: Any = "CenterCenter",
) -> LabelBarAdjustWritebackSemantics:
    geometry = request.geometry

    if not isinstance(geometry, LabelBarGeometry):
        raise TypeError("Expected LabelBarGeometry in LabelBarAdjustGeometryRequest")

    perim = compute_labelbar_adjust_perimeter_semantics(
        request,
        justification=justification,
    )

    final_box_locs = tuple(
        _finite(loc - perim.major_offset)
        for loc in geometry.box_locs
    )

    final_label_locs = tuple(
        _finite(loc - perim.major_offset)
        for loc in geometry.label_locs
    )

    if request.label_bbox is None or not geometry.label_locs:
        final_label_const_pos = None
    else:
        final_label_const_pos = _finite(
            geometry.label_const_pos
            + perim.box_semantics.label_pos_offset
            - perim.minor_offset
        )

    if (
        request.title_bbox is None
        or not geometry.title_on
        or perim.box_semantics.title_x is None
        or perim.box_semantics.title_y is None
    ):
        final_title_x = None
        final_title_y = None
    else:
        final_title_x = _finite(perim.box_semantics.title_x - perim.x_offset)
        final_title_y = _finite(perim.box_semantics.title_y - perim.y_offset)

    return LabelBarAdjustWritebackSemantics(
        perimeter_semantics=perim,
        final_box_locs=final_box_locs,
        final_label_locs=final_label_locs,
        final_label_const_pos=final_label_const_pos,
        final_title_x=final_title_x,
        final_title_y=final_title_y,
        final_view_bbox=perim.final_labelbar_view_bbox,
    )


__all__ = [
    "LabelBarAdjustWritebackSemantics",
    "compute_labelbar_adjust_writeback_semantics",
]
