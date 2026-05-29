from __future__ import annotations

from typing import Any

from ._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider
from ._plotchar_metrics_provider import resolve_plotchar_metrics_from_provider
from ._text_bbox import TextItemBBoxRequest
from ._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from ._text_bbox_semantics import TextBBoxSemantics, compute_text_bbox_from_plotchar_metrics


class TextBBoxPlotcharProviderError(RuntimeError):
    pass


def compute_text_item_bbox_from_plotchar_provider(
    request: TextItemBBoxRequest,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> TextBBoxSemantics:
    """Compute TextItem bbox from an explicit Plotchar metrics provider.

    This is an explicit opt-in bridge, not the default TextItem bbox engine.

    The call chain is intentionally narrow and source-mapped:

    TextItemBBoxRequest
      -> TextItem.c measurement request boundary
      -> provider.metrics_for_request(...)
      -> Plotchar DL / DR / DB / DT
      -> TextItem.c post-metric justification and rotation semantics

    Do not replace provider metrics with fixed-width, SVG text-size, browser, or
    character-count heuristics. A provider without a real backend must raise.
    """
    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(request)
    metrics = resolve_plotchar_metrics_from_provider(provider, plotchar_request)

    return compute_text_bbox_from_plotchar_metrics(
        request,
        metrics,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


def compute_text_item_bbox_from_ncl_plotchar_backend(
    request: TextItemBBoxRequest,
    backend: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> TextBBoxSemantics:
    """Compute TextItem bbox through an explicit NCL Plotchar backend.

    The backend must implement the real source-mapped Plotchar route. The
    wrapper still does not enable the global TextItem bbox engine.
    """
    provider = build_ncl_plotchar_metrics_provider(backend=backend)
    return compute_text_item_bbox_from_plotchar_provider(
        request,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


__all__ = [
    "TextBBoxPlotcharProviderError",
    "compute_text_item_bbox_from_ncl_plotchar_backend",
    "compute_text_item_bbox_from_plotchar_provider",
]
