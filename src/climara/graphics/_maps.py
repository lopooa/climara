"""
Map helpers returning HLU-style map objects.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._contour import build_contour_plot
from ._objects import HluMapPlot, as_resources
from ._strings import add_plot_strings


_PROJECTION_ALIASES = {
    "cylindrical": "CylindricalEquidistant",
    "platecarree": "CylindricalEquidistant",
    "robinson": "Robinson",
    "orthographic": "Orthographic",
    "stereographic": "Stereographic",
    "northpolarstereo": "Stereographic",
    "southpolarstereo": "Stereographic",
}


def normalize_projection(name: str | None) -> str:
    if name is None:
        return "CylindricalEquidistant"
    key = str(name).replace("_", "").replace("-", "").lower()
    return _PROJECTION_ALIASES.get(key, str(name))


def build_map_plot(
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluMapPlot:
    res = as_resources(resources, **kwargs)
    projection = normalize_projection(res.get("mpProjection", res.get("projection")))
    plot = HluMapPlot(
        name=str(res.get("name", "map")),
        resources=res,
        projection=projection,
    )
    add_plot_strings(plot, res)
    return plot


def gsn_csm_map(
    wks: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluMapPlot:
    plot = build_map_plot(resources, **kwargs)
    if hasattr(wks, "add_child"):
        wks.add_child(plot)
    return plot


def gsn_csm_contour_map(
    wks: Any,
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
):
    res = as_resources(resources, **kwargs)
    res.setdefault("mpProjection", normalize_projection(res.get("mpProjection", res.get("projection"))))
    plot = build_contour_plot(data, res)
    if hasattr(wks, "add_child"):
        wks.add_child(plot)
    return plot


def gsn_panel_maps(wks: Any, plots: list[Any], resources: Mapping[str, Any] | None = None, **kwargs: Any):
    from ._panel import gsn_panel
    return gsn_panel(wks, plots, resources, **kwargs)


def ncl_panel_maps(wks: Any, plots: list[Any], resources: Mapping[str, Any] | None = None, **kwargs: Any):
    return gsn_panel_maps(wks, plots, resources, **kwargs)


create_map = build_map_plot
map_plot = build_map_plot


__all__ = [
    "HluMapPlot",
    "build_map_plot",
    "create_map",
    "gsn_csm_contour_map",
    "gsn_csm_map",
    "gsn_panel_maps",
    "map_plot",
    "ncl_panel_maps",
    "normalize_projection",
]
