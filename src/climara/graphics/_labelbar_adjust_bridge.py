from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ._labelbar_adjust import (
    LabelBarAdjustGeometryRequest,
    build_labelbar_adjust_geometry_request,
)
from ._labelbar_bbox_semantics import (
    LabelBarTextBBoxSemantics,
    compute_labelbar_text_bbox_from_plotchar_metrics,
)
from ._plotchar_metrics import PlotcharExtentMetrics


@dataclass(frozen=True)
class LabelBarSuppliedMetricsAdjustRequest:
    text_bboxes: LabelBarTextBBoxSemantics
    adjust_request: LabelBarAdjustGeometryRequest


def build_labelbar_adjust_request_from_supplied_plotchar_metrics(
    obj: Any,
    *,
    title_metrics: PlotcharExtentMetrics | None = None,
    label_metrics: Iterable[PlotcharExtentMetrics] = (),
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarSuppliedMetricsAdjustRequest:
    if not hasattr(obj, "compute_geometry"):
        raise TypeError("Expected a LabelBar-like object with compute_geometry()")

    geometry = obj.compute_geometry()

    text_bboxes = compute_labelbar_text_bbox_from_plotchar_metrics(
        obj,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )

    title_bbox = None if text_bboxes.title is None else text_bboxes.title.bbox
    label_bbox = None if text_bboxes.labels is None else text_bboxes.labels.bbox

    return LabelBarSuppliedMetricsAdjustRequest(
        text_bboxes=text_bboxes,
        adjust_request=build_labelbar_adjust_geometry_request(
            geometry,
            title_bbox=title_bbox,
            label_bbox=label_bbox,
        ),
    )


__all__ = [
    "LabelBarSuppliedMetricsAdjustRequest",
    "build_labelbar_adjust_request_from_supplied_plotchar_metrics",
]
