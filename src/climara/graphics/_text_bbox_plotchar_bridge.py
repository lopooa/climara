from __future__ import annotations

from ._plotchar_metrics import (
    PlotcharMetricsRequest,
    build_plotchar_metrics_request,
)
from ._text_bbox import TextItemBBoxRequest
from ._text_semantics import plotchar_real_size_from_text_semantics


def build_plotchar_metrics_request_from_text_bbox_request(
    request: TextItemBBoxRequest,
) -> PlotcharMetricsRequest:
    return build_plotchar_metrics_request(
        request.semantics,
        x=0.5,
        y=0.5,
        size=plotchar_real_size_from_text_semantics(request.semantics),
        angle=360.0,
        cntr=-1.0,
    )


__all__ = [
    "build_plotchar_metrics_request_from_text_bbox_request",
]
