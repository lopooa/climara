from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._labelbar_text_bbox import build_labelbar_text_bbox_requests
from ._plotchar_metrics import PlotcharMetricsRequest
from ._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)


@dataclass(frozen=True)
class LabelBarPlotcharMetricsRequests:
    title: PlotcharMetricsRequest | None
    labels: tuple[PlotcharMetricsRequest, ...]


def build_labelbar_plotchar_metrics_requests(
    obj: Any,
) -> LabelBarPlotcharMetricsRequests:
    text_bbox_requests = build_labelbar_text_bbox_requests(obj)

    if text_bbox_requests.title is None:
        title_request = None
    else:
        title_request = build_plotchar_metrics_request_from_text_bbox_request(
            text_bbox_requests.title
        )

    label_requests = tuple(
        build_plotchar_metrics_request_from_text_bbox_request(item)
        for item in text_bbox_requests.labels.items
    )

    return LabelBarPlotcharMetricsRequests(
        title=title_request,
        labels=label_requests,
    )


__all__ = [
    "LabelBarPlotcharMetricsRequests",
    "build_labelbar_plotchar_metrics_requests",
]
