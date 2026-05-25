"""
Label bar compatibility helpers.

The implementation delegates to the backend-neutral HLU label bar object.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._labelbar_object import (
    HluLabelBar,
    _merge_labelbar_resources,
    build_hlu_labelbar,
    create_hlu_labelbar,
)


def build_labelbar(
    levels: Any = None,
    colors: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluLabelBar:
    """Build an HLU label bar object."""

    res = _merge_labelbar_resources(resources, **kwargs)

    if levels is not None:
        res.setdefault("levels", levels)
    if colors is not None:
        res.setdefault("colors", colors)

    return build_hlu_labelbar(resources=res)


def create_labelbar(*args: Any, **kwargs: Any) -> HluLabelBar:
    """Compatibility alias for build_labelbar."""

    return build_labelbar(*args, **kwargs)


def draw_labelbar(*args: Any, **kwargs: Any) -> HluLabelBar:
    """Compatibility alias for build_labelbar."""

    return build_labelbar(*args, **kwargs)


def add_labelbar(target: Any, *args: Any, **kwargs: Any) -> HluLabelBar:
    """Create a label bar and attach it to a target when supported."""

    item = build_labelbar(*args, **kwargs)

    if hasattr(target, "add_child"):
        target.add_child(item)
    elif hasattr(target, "children"):
        target.children.append(item)

    return item


__all__ = [
    "HluLabelBar",
    "_merge_labelbar_resources",
    "add_labelbar",
    "build_hlu_labelbar",
    "build_labelbar",
    "create_hlu_labelbar",
    "create_labelbar",
    "draw_labelbar",
]
