from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ._labelbar_text_bbox import build_labelbar_text_bbox_requests
from ._multitext_bbox_semantics import (
    MultiTextBBoxSemantics,
    compute_multitext_bbox_from_plotchar_metrics,
)
from ._plotchar_metrics import PlotcharExtentMetrics
from ._text_bbox_semantics import (
    TextBBoxSemantics,
    compute_text_bbox_from_plotchar_metrics,
)


@dataclass(frozen=True)
class LabelBarTextBBoxSemantics:
    title: TextBBoxSemantics | None
    labels: MultiTextBBoxSemantics | None


def compute_labelbar_text_bbox_from_plotchar_metrics(
    obj: Any,
    *,
    title_metrics: PlotcharExtentMetrics | None = None,
    label_metrics: Iterable[PlotcharExtentMetrics] = (),
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarTextBBoxSemantics:
    requests = build_labelbar_text_bbox_requests(obj)
    label_metric_values = tuple(label_metrics)

    if requests.title is None:
        if title_metrics is not None:
            raise ValueError(
                "LabelBar title Plotchar metrics were supplied but this LabelBar has no title request"
            )
        title_result = None
    else:
        if title_metrics is None:
            raise ValueError(
                "LabelBar title Plotchar metrics are required when this LabelBar has a title request"
            )
        title_result = compute_text_bbox_from_plotchar_metrics(
            requests.title,
            title_metrics,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    if len(requests.labels.items) == 0:
        if label_metric_values:
            raise ValueError(
                "LabelBar label Plotchar metrics were supplied but this LabelBar has no label requests"
            )
        labels_result = None
    else:
        labels_result = compute_multitext_bbox_from_plotchar_metrics(
            requests.labels,
            label_metric_values,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    return LabelBarTextBBoxSemantics(
        title=title_result,
        labels=labels_result,
    )


__all__ = [
    "LabelBarTextBBoxSemantics",
    "compute_labelbar_text_bbox_from_plotchar_metrics",
]
