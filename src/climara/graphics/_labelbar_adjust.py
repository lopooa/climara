from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._text_bbox import TextBBox


class LabelBarAdjustGeometryNotImplementedError(NotImplementedError):
    pass


@dataclass(frozen=True)
class LabelBarAdjustGeometryRequest:
    geometry: Any
    title_bbox: TextBBox | None = None
    label_bbox: TextBBox | None = None


def has_labelbar_adjust_geometry_engine() -> bool:
    return False


def build_labelbar_adjust_geometry_request(
    geometry: Any,
    *,
    title_bbox: TextBBox | None = None,
    label_bbox: TextBBox | None = None,
) -> LabelBarAdjustGeometryRequest:
    return LabelBarAdjustGeometryRequest(
        geometry=geometry,
        title_bbox=title_bbox,
        label_bbox=label_bbox,
    )


def adjust_labelbar_geometry_for_text(
    request: LabelBarAdjustGeometryRequest,
):
    raise LabelBarAdjustGeometryNotImplementedError(
        "NCL LabelBar AdjustGeometry / AutoManage is not implemented in climara yet. "
        "It requires audited LabelBar.c text-bbox feedback semantics and must not be "
        "approximated from visual spacing."
    )


__all__ = [
    "LabelBarAdjustGeometryNotImplementedError",
    "LabelBarAdjustGeometryRequest",
    "adjust_labelbar_geometry_for_text",
    "build_labelbar_adjust_geometry_request",
    "has_labelbar_adjust_geometry_engine",
]
