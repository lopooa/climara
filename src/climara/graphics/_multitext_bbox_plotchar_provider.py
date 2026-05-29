from __future__ import annotations

from typing import Any

from ._multitext_bbox_semantics import MultiTextBBoxSemantics
from ._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider
from ._text_bbox import MultiTextBBoxRequest, aggregate_multitext_child_bboxes
from ._text_bbox_plotchar_provider import compute_text_item_bbox_from_plotchar_provider


class MultiTextBBoxPlotcharProviderError(RuntimeError):
    pass


def compute_multitext_bbox_from_plotchar_provider(
    request: MultiTextBBoxRequest,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> MultiTextBBoxSemantics:
    """Compute MultiText bbox through an explicit Plotchar metrics provider.

    This is an explicit opt-in aggregation bridge, not the default MultiText bbox
    engine.

    Source boundary:

    MultiTextBBoxRequest
      -> each child TextItemBBoxRequest
      -> TextItem.c measurement request boundary
      -> provider.metrics_for_request(...)
      -> Plotchar DL / DR / DB / DT
      -> TextItem.c post-metric justification and rotation semantics
      -> MultiText.c child bbox aggregation semantics

    Do not replace child metrics with fixed-width, SVG/browser text-size, or
    character-count estimates. The provider must supply source-mapped metrics or
    raise.
    """
    if not request.items:
        raise ValueError(
            "MultiText provider bbox computation requires at least one TextItem request"
        )

    child_results = tuple(
        compute_text_item_bbox_from_plotchar_provider(
            item,
            provider,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )
        for item in request.items
    )

    bbox = aggregate_multitext_child_bboxes(
        request,
        (child.bbox for child in child_results),
    )

    return MultiTextBBoxSemantics(
        bbox=bbox,
        child_text_bboxes=child_results,
    )


def compute_multitext_bbox_from_ncl_plotchar_backend(
    request: MultiTextBBoxRequest,
    backend: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> MultiTextBBoxSemantics:
    """Compute MultiText bbox through an explicit NCL Plotchar backend.

    This wraps the source-mapped NCL Plotchar provider boundary. It still does
    not enable the global MultiText bbox engine.
    """
    provider = build_ncl_plotchar_metrics_provider(backend=backend)
    return compute_multitext_bbox_from_plotchar_provider(
        request,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


__all__ = [
    "MultiTextBBoxPlotcharProviderError",
    "compute_multitext_bbox_from_ncl_plotchar_backend",
    "compute_multitext_bbox_from_plotchar_provider",
]
