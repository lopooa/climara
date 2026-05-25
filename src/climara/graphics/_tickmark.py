"""
Tickmark resources represented without a drawing dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass
class HluTickMark:
    """Tickmark description."""

    side: str
    values: list[Any] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)


def _list_value(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def build_tickmark(
    side: str,
    values: Any = None,
    labels: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTickMark:
    res: dict[str, Any] = {}
    if resources:
        res.update(dict(resources))
    res.update(kwargs)

    vals = _list_value(values)
    labs = [str(item) for item in _list_value(labels)]
    if not labs and vals:
        labs = [str(item) for item in vals]

    return HluTickMark(side=side, values=vals, labels=labs, resources=res)


def build_tickmarks(resources: Mapping[str, Any] | None = None, **kwargs: Any) -> list[HluTickMark]:
    res: dict[str, Any] = {}
    if resources:
        res.update(dict(resources))
    res.update(kwargs)

    items: list[HluTickMark] = []
    for side, prefix in [
        ("bottom", "tmXB"),
        ("top", "tmXT"),
        ("left", "tmYL"),
        ("right", "tmYR"),
    ]:
        values = res.get(f"{prefix}Values")
        labels = res.get(f"{prefix}Labels")
        if values is not None or labels is not None:
            items.append(build_tickmark(side, values, labels, res))
    return items


def add_tickmarks(target: Any, resources: Mapping[str, Any] | None = None, **kwargs: Any) -> list[HluTickMark]:
    items = build_tickmarks(resources, **kwargs)
    for item in items:
        if hasattr(target, "add_child"):
            target.add_child(item)
        elif hasattr(target, "children"):
            target.children.append(item)
    return items


__all__ = [
    "HluTickMark",
    "add_tickmarks",
    "build_tickmark",
    "build_tickmarks",
]
