from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ._text_semantics import TextItemSemantics


class TextBBoxNotImplementedError(NotImplementedError):
    pass


@dataclass(frozen=True)
class TextBBox:
    l: float
    r: float
    b: float
    t: float

    @property
    def width(self) -> float:
        return self.r - self.l

    @property
    def height(self) -> float:
        return self.t - self.b


@dataclass(frozen=True)
class TextItemBBoxRequest:
    semantics: TextItemSemantics
    x: float
    y: float


@dataclass(frozen=True)
class MultiTextBBoxRequest:
    items: tuple[TextItemBBoxRequest, ...]


def has_text_bbox_engine() -> bool:
    return False


def compute_text_item_bbox(request: TextItemBBoxRequest) -> TextBBox:
    raise TextBBoxNotImplementedError(
        "NCL TextItem bbox computation is not implemented in climara yet. "
        "This requires audited TextItem.c / Plotchar / font metric semantics; "
        "do not replace this with heuristic visual extents."
    )


def compute_multitext_bbox(request: MultiTextBBoxRequest) -> TextBBox:
    raise TextBBoxNotImplementedError(
        "NCL MultiText bbox computation is not implemented in climara yet. "
        "This requires audited MultiText.c child TextItem bbox aggregation; "
        "do not replace this with heuristic visual extents."
    )


def build_multitext_bbox_request(
    items: Iterable[TextItemBBoxRequest],
) -> MultiTextBBoxRequest:
    return MultiTextBBoxRequest(items=tuple(items))


__all__ = [
    "MultiTextBBoxRequest",
    "TextBBox",
    "TextBBoxNotImplementedError",
    "TextItemBBoxRequest",
    "build_multitext_bbox_request",
    "compute_multitext_bbox",
    "compute_text_item_bbox",
    "has_text_bbox_engine",
]
