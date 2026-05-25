from __future__ import annotations

from ._plotchar_metrics import (
    PlotcharMetricsRequest,
    build_plotchar_metrics_request,
)
from ._text_bbox import TextItemBBoxRequest


def build_plotchar_metrics_request_from_text_bbox_request(
    request: TextItemBBoxRequest,
) -> PlotcharMetricsRequest:
    return build_plotchar_metrics_request(
        request.semantics,
        x=request.x,
        y=request.y,
        size=request.semantics.font_height,
        angle=request.semantics.angle,
    )


__all__ = [
    "build_plotchar_metrics_request_from_text_bbox_request",
]
