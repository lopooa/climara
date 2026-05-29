from __future__ import annotations

from typing import Any

from ._labelbar_bbox_semantics import LabelBarTextBBoxSemantics
from ._labelbar_text_bbox import build_labelbar_text_bbox_requests
from ._multitext_bbox_plotchar_provider import (
    compute_multitext_bbox_from_plotchar_provider,
)
from ._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider
from ._text_bbox_plotchar_provider import compute_text_item_bbox_from_plotchar_provider


class LabelBarBBoxPlotcharProviderError(RuntimeError):
    pass


def compute_labelbar_text_bbox_from_plotchar_provider(
    obj: Any,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarTextBBoxSemantics:
    """Compute LabelBar title/label text bboxes from a Plotchar provider.

    This is an explicit opt-in bridge, not the default LabelBar / TextItem /
    MultiText bbox engine.

    Source boundary:

    LabelBar
      -> LabelBar.c title and labels TextItem/MultiText bbox requests
      -> TextItem.c measurement request boundary for every text item
      -> provider.metrics_for_request(...)
      -> PLCHHQ / PCGETR DL, DR, DB, DT metrics
      -> TextItem.c post-metric justification and rotation semantics
      -> MultiText.c child bbox aggregation semantics for labels

    Do not replace the provider with fixed-width, SVG/browser text metrics, or
    character-count approximations. A provider without a real backend must
    raise through the child TextItem/MultiText provider path.
    """
    requests = build_labelbar_text_bbox_requests(obj)

    if requests.title is None:
        title_result = None
    else:
        title_result = compute_text_item_bbox_from_plotchar_provider(
            requests.title,
            provider,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    if len(requests.labels.items) == 0:
        labels_result = None
    else:
        labels_result = compute_multitext_bbox_from_plotchar_provider(
            requests.labels,
            provider,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    return LabelBarTextBBoxSemantics(
        title=title_result,
        labels=labels_result,
    )


def compute_labelbar_text_bbox_from_ncl_plotchar_backend(
    obj: Any,
    backend: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarTextBBoxSemantics:
    """Compute LabelBar text bboxes through an explicit NCL Plotchar backend.

    The backend must implement the source-mapped NCAR/NCL Plotchar route. This
    wrapper does not enable any global default bbox engine.
    """
    provider = build_ncl_plotchar_metrics_provider(backend=backend)
    return compute_labelbar_text_bbox_from_plotchar_provider(
        obj,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


__all__ = [
    "LabelBarBBoxPlotcharProviderError",
    "compute_labelbar_text_bbox_from_ncl_plotchar_backend",
    "compute_labelbar_text_bbox_from_plotchar_provider",
]
