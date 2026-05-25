"""
HLU-style primitive objects.

All coordinates are backend-neutral. NDC primitives use normalized device
coordinates in the 0..1 range.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def merge_resources(
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if resources:
        out.update(dict(resources))
    out.update(kwargs)
    return out


@dataclass
class HluPrimitive:
    """Base primitive object."""

    x: list[float] = field(default_factory=list)
    y: list[float] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)
    coordinate_system: str = "ndc"

    def set_values(
        self,
        resources: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ):
        self.resources.update(merge_resources(resources, **kwargs))
        return self

    def add_child(self, child: Any):
        self.children.append(child)
        return child


@dataclass
class HluPolyline(HluPrimitive):
    """Polyline primitive."""


@dataclass
class HluPolygon(HluPrimitive):
    """Polygon primitive."""


@dataclass
class HluMarker(HluPrimitive):
    """Marker primitive."""

    marker: str = "circle"


def normalize_xy(x: Any, y: Any) -> tuple[list[float], list[float]]:
    xs = _as_list(x)
    ys = _as_list(y)

    if len(xs) != len(ys):
        raise ValueError("x and y need the same length.")

    return [float(item) for item in xs], [float(item) for item in ys]


def build_polyline(
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPolyline:
    xs, ys = normalize_xy(x, y)
    return HluPolyline(x=xs, y=ys, resources=merge_resources(resources, **kwargs))


def build_polygon(
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPolygon:
    xs, ys = normalize_xy(x, y)
    return HluPolygon(x=xs, y=ys, resources=merge_resources(resources, **kwargs))


def build_marker(
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluMarker:
    xs, ys = normalize_xy(x, y)
    res = merge_resources(resources, **kwargs)
    marker = str(res.get("gsMarkerIndex", res.get("marker", "circle")))
    return HluMarker(x=xs, y=ys, resources=res, marker=marker)


__all__ = [
    "HluMarker",
    "HluPolygon",
    "HluPolyline",
    "HluPrimitive",
    "build_marker",
    "build_polygon",
    "build_polyline",
    "merge_resources",
    "normalize_xy",
]
