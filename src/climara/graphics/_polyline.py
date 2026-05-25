"""
GSN polyline helpers.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._primitive import HluPolyline, build_polyline, merge_resources


def gsn_add_polyline(
    plot: Any,
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPolyline:
    """Create a polyline primitive and attach it to a plot-like object."""

    item = build_polyline(x, y, resources, **kwargs)

    if hasattr(plot, "add_child"):
        plot.add_child(item)
    elif hasattr(plot, "children"):
        plot.children.append(item)

    return item


def gsn_polyline_ndc(
    wks: Any,
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPolyline:
    """Draw an NDC polyline on a workstation."""

    res = merge_resources(resources, **kwargs)
    res.setdefault("coordinate_system", "ndc")
    return gsn_add_polyline(wks, x, y, res)


__all__ = [
    "HluPolyline",
    "gsn_add_polyline",
    "gsn_polyline_ndc",
]
