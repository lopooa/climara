"""
GSN polygon helpers.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._primitive import HluPolygon, build_polygon, merge_resources


def gsn_add_polygon(
    plot: Any,
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPolygon:
    """Create a polygon primitive and attach it to a plot-like object."""

    item = build_polygon(x, y, resources, **kwargs)

    if hasattr(plot, "add_child"):
        plot.add_child(item)
    elif hasattr(plot, "children"):
        plot.children.append(item)

    return item


def gsn_polygon_ndc(
    wks: Any,
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPolygon:
    """Draw an NDC polygon on a workstation."""

    res = merge_resources(resources, **kwargs)
    res.setdefault("coordinate_system", "ndc")
    return gsn_add_polygon(wks, x, y, res)


__all__ = [
    "HluPolygon",
    "gsn_add_polygon",
    "gsn_polygon_ndc",
]
