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
    return False


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
    raise TextBBoxNotImplementedError(
        "NCL TextItem bbox computation is not implemented in climara yet. "
        "This requires audited TextItem.c / Plotchar / font metric semantics; "
        "do not replace this with heuristic visual extents."
    )


def compute_multitext_bbox(request: MultiTextBBoxRequest) -> TextBBox:
    _normalize_coordinate_space(request.coordinate_space)
    raise TextBBoxNotImplementedError(
        "NCL MultiText bbox computation is not implemented in climara yet. "
        "This requires audited MultiText.c child TextItem bbox aggregation; "
        "do not replace this with heuristic visual extents."
    )


__all__ = [
    "TEXT_BBOX_COORD_NDC",
    "MultiTextBBoxRequest",
    "TextBBox",
    "TextBBoxNotImplementedError",
    "TextItemBBoxRequest",
    "build_multitext_bbox_request",
    "build_multitext_bbox_request_from_semantics",
    "build_text_item_bbox_request",
    "compute_multitext_bbox",
    "compute_text_item_bbox",
    "has_text_bbox_engine",
]
