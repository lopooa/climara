from __future__ import annotations

from dataclasses import replace

from ._labelbar_adjust import LabelBarAdjustGeometryResult
from ._labelbar_adjust_materialize import (
    LabelBarAdjustedGeometry,
    materialize_labelbar_adjusted_geometry,
)
from ._labelbar_geometry import LabelBarGeometry, NdcRect
from ._text_bbox import TextBBox


def _bbox_to_rect(box: TextBBox) -> NdcRect:
    return NdcRect(
        l=box.l,
        r=box.r,
        b=box.b,
        t=box.t,
    )


def apply_labelbar_adjusted_geometry(
    adjusted: LabelBarAdjustedGeometry,
) -> LabelBarGeometry:
    geometry = adjusted.source_geometry

    return replace(
        geometry,
        perim=_bbox_to_rect(adjusted.nominal_perim_bbox),
        adj_bar=_bbox_to_rect(adjusted.adjusted_bar_bbox),
        box_locs=adjusted.final_box_locs,
        label_locs=adjusted.final_label_locs,
        label_const_pos=(
            geometry.label_const_pos
            if adjusted.final_label_const_pos is None
            else adjusted.final_label_const_pos
        ),
        label_text_positions=adjusted.final_label_text_positions,
        title_text_position=adjusted.final_title_text_position,
        title_text_item=adjusted.final_title_text_item,
    )


def adjusted_geometry_from_result(
    result: LabelBarAdjustGeometryResult,
) -> LabelBarGeometry:
    return apply_labelbar_adjusted_geometry(
        materialize_labelbar_adjusted_geometry(result)
    )


__all__ = [
    "adjusted_geometry_from_result",
    "apply_labelbar_adjusted_geometry",
]
