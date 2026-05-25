from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._labelbar_svg_adapter import _text_values
from ._multitext_semantics import build_multitext_semantics
from ._text_bbox import (
    MultiTextBBoxRequest,
    TextItemBBoxRequest,
    build_multitext_bbox_request_from_semantics,
    build_text_item_bbox_request,
)
from ._text_semantics import build_text_item_semantics


@dataclass(frozen=True)
class LabelBarTextBBoxRequests:
    title: TextItemBBoxRequest | None
    labels: MultiTextBBoxRequest


def _resources(obj: Any) -> dict[str, Any]:
    values = getattr(obj, "resources", None)
    if isinstance(values, dict):
        return values
    return {}


def _resource_float(resources: dict[str, Any], name: str, default: float) -> float:
    value = resources.get(name, default)
    if value is None:
        return default
    return float(value)


def _title_bbox_request_from_geometry(geometry: Any) -> TextItemBBoxRequest | None:
    title_item = getattr(geometry, "title_text_item", None)

    if title_item is None:
        return None

    semantics = build_text_item_semantics(
        title_item.text,
        direction=title_item.direction,
        func_code=title_item.func_code,
        just=title_item.just,
        angle=title_item.angle,
        font=title_item.font,
        font_color=title_item.font_color,
        font_height=title_item.font_height,
        font_aspect=title_item.font_aspect,
        font_thickness=title_item.font_thickness,
        font_quality=title_item.font_quality,
        constant_spacing=title_item.constant_spacing,
    )

    return build_text_item_bbox_request(
        semantics,
        x=title_item.x,
        y=title_item.y,
    )


def _label_bbox_request_from_geometry(obj: Any, geometry: Any) -> MultiTextBBoxRequest:
    resources = _resources(obj)
    label_count = len(geometry.label_text_positions)
    label_strings = _text_values(obj, label_count)

    multitext = build_multitext_semantics(
        label_strings,
        direction=resources.get("lbLabelDirection", "Across"),
        func_code=resources.get("lbLabelFuncCode", "~"),
        just=resources.get("lbLabelJust", "CenterCenter"),
        angle=geometry.label_angle,
        font=resources.get("lbLabelFont", 21),
        font_color=resources.get("lbLabelFontColor", "Foreground"),
        font_height=_resource_float(resources, "lbLabelFontHeightF", 0.02),
        font_aspect=_resource_float(resources, "lbLabelFontAspectF", 1.3125),
        font_thickness=_resource_float(resources, "lbLabelFontThicknessF", 1.0),
        font_quality=resources.get("lbLabelFontQuality", "High"),
        constant_spacing=_resource_float(resources, "lbLabelConstantSpacingF", 0.0),
    )

    positions = tuple(
        (item.x, item.y)
        for item in geometry.label_text_positions
    )

    return build_multitext_bbox_request_from_semantics(
        multitext,
        positions,
    )


def build_labelbar_text_bbox_requests(obj: Any) -> LabelBarTextBBoxRequests:
    if hasattr(obj, "compute_geometry"):
        geometry = obj.compute_geometry()
    else:
        raise TypeError("Expected a LabelBar-like object with compute_geometry()")

    return LabelBarTextBBoxRequests(
        title=_title_bbox_request_from_geometry(geometry),
        labels=_label_bbox_request_from_geometry(obj, geometry),
    )


__all__ = [
    "LabelBarTextBBoxRequests",
    "build_labelbar_text_bbox_requests",
]
