"""
GSN polymarker helpers.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._primitive import HluMarker, build_marker, merge_resources


def gsn_add_polymarker(
    plot: Any,
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluMarker:
    """Create a marker primitive and attach it to a plot-like object."""

    item = build_marker(x, y, resources, **kwargs)

    if hasattr(plot, "add_child"):
        plot.add_child(item)
    elif hasattr(plot, "children"):
        plot.children.append(item)

    return item


def gsn_polymarker_ndc(
    wks: Any,
    x: Any,
    y: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluMarker:
    """Draw NDC markers on a workstation."""

    res = merge_resources(resources, **kwargs)
    res.setdefault("coordinate_system", "ndc")
    return gsn_add_polymarker(wks, x, y, res)


__all__ = [
    "HluMarker",
    "gsn_add_polymarker",
    "gsn_polymarker_ndc",
]
