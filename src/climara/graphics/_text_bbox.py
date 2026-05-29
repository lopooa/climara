from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ._multitext_semantics import MultiTextSemantics
from ._text_semantics import TextItemSemantics


TEXT_BBOX_COORD_NDC = "NDC"


class TextBBoxNotImplementedError(NotImplementedError):
    pass


@dataclass(frozen=True)
class TextBBox:
    l: float
    r: float
    b: float
    t: float
    coordinate_space: str = TEXT_BBOX_COORD_NDC

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
    coordinate_space: str = TEXT_BBOX_COORD_NDC


@dataclass(frozen=True)
class MultiTextBBoxRequest:
    items: tuple[TextItemBBoxRequest, ...]
    coordinate_space: str = TEXT_BBOX_COORD_NDC


def has_text_bbox_engine() -> bool:
    from ._plotchar_python_live_engine import has_python_plotchar_mainline_engine

    return has_python_plotchar_mainline_engine()

def _normalize_coordinate_space(value: str | None) -> str:
    if value is None:
        return TEXT_BBOX_COORD_NDC

    out = str(value).strip().upper()
    if out != TEXT_BBOX_COORD_NDC:
        raise ValueError(
            "TextItem / MultiText bbox requests currently support only NDC coordinate space"
        )

    return out


def build_text_item_bbox_request(
    semantics: TextItemSemantics,
    *,
    x: float,
    y: float,
    coordinate_space: str | None = TEXT_BBOX_COORD_NDC,
) -> TextItemBBoxRequest:
    return TextItemBBoxRequest(
        semantics=semantics,
        x=float(x),
        y=float(y),
        coordinate_space=_normalize_coordinate_space(coordinate_space),
    )


def build_multitext_bbox_request(
    items: Iterable[TextItemBBoxRequest],
    *,
    coordinate_space: str | None = TEXT_BBOX_COORD_NDC,
) -> MultiTextBBoxRequest:
    normalized = _normalize_coordinate_space(coordinate_space)
    item_values = tuple(items)

    for item in item_values:
        if _normalize_coordinate_space(item.coordinate_space) != normalized:
            raise ValueError(
                "All TextItem bbox requests in a MultiText bbox request must use the same coordinate space"
            )

    return MultiTextBBoxRequest(
        items=item_values,
        coordinate_space=normalized,
    )


def build_multitext_bbox_request_from_semantics(
    semantics: MultiTextSemantics,
    positions: Iterable[tuple[float, float]],
    *,
    coordinate_space: str | None = TEXT_BBOX_COORD_NDC,
) -> MultiTextBBoxRequest:
    normalized = _normalize_coordinate_space(coordinate_space)
    position_values = tuple(positions)

    if len(position_values) != len(semantics.items):
        raise ValueError(
            "MultiText bbox request requires one position for each TextItem semantic item"
        )

    return MultiTextBBoxRequest(
        items=tuple(
            build_text_item_bbox_request(
                item,
                x=position_values[index][0],
                y=position_values[index][1],
                coordinate_space=normalized,
            )
            for index, item in enumerate(semantics.items)
        ),
        coordinate_space=normalized,
    )


def compute_text_item_bbox(request: TextItemBBoxRequest) -> TextBBox:
    _normalize_coordinate_space(request.coordinate_space)

    from ._plotchar_python_live_engine import compute_text_item_bbox_with_python_mainline

    return compute_text_item_bbox_with_python_mainline(request)

def compute_multitext_bbox(request: MultiTextBBoxRequest) -> TextBBox:
    _normalize_coordinate_space(request.coordinate_space)

    from ._plotchar_python_live_engine import compute_multitext_bbox_with_python_mainline

    return compute_multitext_bbox_with_python_mainline(request)

def build_text_bbox(
    *,
    l: float,
    r: float,
    b: float,
    t: float,
    coordinate_space: str | None = TEXT_BBOX_COORD_NDC,
) -> TextBBox:
    normalized = _normalize_coordinate_space(coordinate_space)

    left = float(l)
    right = float(r)
    bottom = float(b)
    top = float(t)

    if right < left:
        raise ValueError("TextBBox requires r >= l")
    if top < bottom:
        raise ValueError("TextBBox requires t >= b")

    return TextBBox(
        l=left,
        r=right,
        b=bottom,
        t=top,
        coordinate_space=normalized,
    )


def union_text_bboxes(
    boxes: Iterable[TextBBox],
    *,
    coordinate_space: str | None = None,
) -> TextBBox:
    box_values = tuple(boxes)

    if not box_values:
        raise ValueError("Cannot union an empty TextBBox sequence")

    if coordinate_space is None:
        normalized = _normalize_coordinate_space(box_values[0].coordinate_space)
    else:
        normalized = _normalize_coordinate_space(coordinate_space)

    for box in box_values:
        if _normalize_coordinate_space(box.coordinate_space) != normalized:
            raise ValueError("All TextBBox objects must use the same coordinate space")

    return TextBBox(
        l=min(box.l for box in box_values),
        r=max(box.r for box in box_values),
        b=min(box.b for box in box_values),
        t=max(box.t for box in box_values),
        coordinate_space=normalized,
    )


def aggregate_multitext_child_bboxes(
    request: MultiTextBBoxRequest,
    child_bboxes: Iterable[TextBBox],
) -> TextBBox:
    _normalize_coordinate_space(request.coordinate_space)
    box_values = tuple(child_bboxes)

    if len(box_values) != len(request.items):
        raise ValueError(
            "MultiText child bbox aggregation requires one child bbox for each TextItem request"
        )

    if not box_values:
        raise ValueError("Cannot aggregate MultiText bbox from an empty child bbox sequence")

    return union_text_bboxes(
        box_values,
        coordinate_space=request.coordinate_space,
    )


__all__ = [
    "aggregate_multitext_child_bboxes",
    "TEXT_BBOX_COORD_NDC",
    "MultiTextBBoxRequest",
    "TextBBox",
    "TextBBoxNotImplementedError",
    "TextItemBBoxRequest",
    "build_multitext_bbox_request",
    "build_multitext_bbox_request_from_semantics",
    "build_text_bbox",
    "build_text_item_bbox_request",
    "compute_multitext_bbox",
    "compute_text_item_bbox",
    "has_text_bbox_engine",
    "union_text_bboxes",
]
