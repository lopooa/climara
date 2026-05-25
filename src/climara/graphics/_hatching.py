"""
Pattern and hatch helpers represented as backend-neutral resources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class HluPatternOverlay:
    """Pattern overlay object."""

    mask: Any = None
    pattern: str = "parallel"
    resources: dict[str, Any] = field(default_factory=dict)


def build_hatch_overlay(
    mask: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPatternOverlay:
    res: dict[str, Any] = {}
    if resources:
        res.update(dict(resources))
    res.update(kwargs)

    pattern = str(res.get("cnFillPattern", res.get("pattern", "parallel")))
    return HluPatternOverlay(mask=mask, pattern=pattern, resources=res)


def add_hatching(
    target: Any,
    mask: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPatternOverlay:
    overlay = build_hatch_overlay(mask, resources, **kwargs)
    if hasattr(target, "add_child"):
        target.add_child(overlay)
    elif hasattr(target, "children"):
        target.children.append(overlay)
    return overlay


def add_significance_hatching(
    target: Any,
    mask: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPatternOverlay:
    res: dict[str, Any] = {"pattern": "parallel"}
    if resources:
        res.update(dict(resources))
    res.update(kwargs)
    return add_hatching(target, mask, res)


def add_agreement_hatching(
    target: Any,
    mask: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPatternOverlay:
    res: dict[str, Any] = {"pattern": "cross"}
    if resources:
        res.update(dict(resources))
    res.update(kwargs)
    return add_hatching(target, mask, res)


__all__ = [
    "HluPatternOverlay",
    "add_agreement_hatching",
    "add_hatching",
    "add_significance_hatching",
    "build_hatch_overlay",
]
