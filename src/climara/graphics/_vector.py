"""
Vector helpers returning backend-neutral HLU-style objects.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._objects import HluVectorPlot, VectorField, as_resources


def build_vector_plot(
    u: Any,
    v: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluVectorPlot:
    res = as_resources(resources, **kwargs)
    return HluVectorPlot(
        name=str(res.get("name", "vector")),
        resources=res,
        u=u,
        v=v,
    )


def gsn_csm_vector(
    wks: Any,
    u: Any,
    v: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluVectorPlot:
    plot = build_vector_plot(u, v, resources, **kwargs)
    if hasattr(wks, "add_child"):
        wks.add_child(plot)
    return plot


def gsn_csm_vector_map(
    wks: Any,
    u: Any,
    v: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluVectorPlot:
    res = as_resources(resources, **kwargs)
    res.setdefault("mpProjection", res.get("mpProjection", "CylindricalEquidistant"))
    return gsn_csm_vector(wks, u, v, res)


def vector_plot(
    u: Any,
    v: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluVectorPlot:
    return build_vector_plot(u, v, resources, **kwargs)


__all__ = [
    "HluVectorPlot",
    "VectorField",
    "build_vector_plot",
    "gsn_csm_vector",
    "gsn_csm_vector_map",
    "vector_plot",
]
