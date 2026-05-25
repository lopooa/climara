"""
NDC text helpers.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._primitive import merge_resources
from ._text_item import HluTextItem


def gsn_create_text_ndc(
    text: str,
    x: float,
    y: float,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    """Create an NDC text item."""

    res = merge_resources(resources, **kwargs)
    res.setdefault("coordinate_system", "ndc")

    return HluTextItem(
        text=str(text),
        x=float(x),
        y=float(y),
        resources=res,
    )


def gsn_text_ndc(
    wks: Any,
    text: str,
    x: float,
    y: float,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    """Create and attach an NDC text item to a workstation."""

    item = gsn_create_text_ndc(text, x, y, resources, **kwargs)

    if hasattr(wks, "add_child"):
        wks.add_child(item)
    elif hasattr(wks, "children"):
        wks.children.append(item)

    return item


__all__ = [
    "HluTextItem",
    "gsn_create_text_ndc",
    "gsn_text_ndc",
]
