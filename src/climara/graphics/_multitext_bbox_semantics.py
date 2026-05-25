from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ._plotchar_metrics import PlotcharExtentMetrics
from ._text_bbox import (
    MultiTextBBoxRequest,
    TextBBox,
    aggregate_multitext_child_bboxes,
)
from ._text_bbox_semantics import (
    TextBBoxSemantics,
    compute_text_bbox_from_plotchar_metrics,
)


@dataclass(frozen=True)
class MultiTextBBoxSemantics:
    bbox: TextBBox
    child_text_bboxes: tuple[TextBBoxSemantics, ...]


def compute_multitext_bbox_from_plotchar_metrics(
    request: MultiTextBBoxRequest,
    metrics: Iterable[PlotcharExtentMetrics],
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> MultiTextBBoxSemantics:
    metric_values = tuple(metrics)

    if len(metric_values) != len(request.items):
        raise ValueError(
            "MultiText supplied Plotchar metrics require one metrics object for each TextItem request"
        )

    if not metric_values:
        raise ValueError(
            "MultiText supplied Plotchar metrics cannot be empty"
        )

    child_results = tuple(
        compute_text_bbox_from_plotchar_metrics(
            item,
            metric,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )
        for item, metric in zip(request.items, metric_values)
    )

    bbox = aggregate_multitext_child_bboxes(
        request,
        (child.bbox for child in child_results),
    )

    return MultiTextBBoxSemantics(
        bbox=bbox,
        child_text_bboxes=child_results,
    )


__all__ = [
    "MultiTextBBoxSemantics",
    "compute_multitext_bbox_from_plotchar_metrics",
]
