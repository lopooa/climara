"""
Contour helpers returning backend-neutral HLU-style objects.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._objects import HluContourPlot, ScalarField, as_resources
from ._strings import add_plot_strings


def _manual_levels(resources: Mapping[str, Any]) -> list[float] | None:
    mode = resources.get("cnLevelSelectionMode")
    if mode != "ManualLevels":
        return None

    if "cnMinLevelValF" not in resources or "cnMaxLevelValF" not in resources:
        return None

    start = float(resources["cnMinLevelValF"])
    stop = float(resources["cnMaxLevelValF"])
    step = float(resources.get("cnLevelSpacingF", 1.0))

    if step <= 0:
        raise ValueError("cnLevelSpacingF must be positive.")

    values: list[float] = []
    current = start
    guard = 0
    while current <= stop + step * 1e-8:
        values.append(round(current, 10))
        current += step
        guard += 1
        if guard > 10000:
            raise ValueError("Too many contour levels.")
    return values


def build_contour_plot(
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    res = as_resources(resources, **kwargs)
    levels = res.get("cnLevels")
    if levels is None:
        levels = _manual_levels(res)

    plot = HluContourPlot(
        name=str(res.get("name", "contour")),
        resources=res,
        data=data,
        levels=list(levels) if levels is not None else None,
        colors=res.get("cnFillPalette"),
    )

    add_plot_strings(plot, res)
    return plot


def gsn_csm_contour(
    wks: Any,
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    plot = build_contour_plot(data, resources, **kwargs)
    if hasattr(wks, "add_child"):
        wks.add_child(plot)
    return plot


def gsn_csm_contour_map(
    wks: Any,
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    res = as_resources(resources, **kwargs)
    res.setdefault("mpProjection", res.get("mpProjection", "CylindricalEquidistant"))
    return gsn_csm_contour(wks, data, res)


def contour(
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    return build_contour_plot(data, resources, **kwargs)


def contourf(
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    res = as_resources(resources, **kwargs)
    res.setdefault("cnFillOn", True)
    return build_contour_plot(data, res)


def pcolormesh(
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    res = as_resources(resources, **kwargs)
    res.setdefault("cnFillOn", True)
    res.setdefault("cnFillMode", "RasterFill")
    return build_contour_plot(data, res)


def ncl_contourf(
    data: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluContourPlot:
    return contourf(data, resources, **kwargs)


__all__ = [
    "HluContourPlot",
    "ScalarField",
    "build_contour_plot",
    "contour",
    "contourf",
    "gsn_csm_contour",
    "gsn_csm_contour_map",
    "ncl_contourf",
    "pcolormesh",
]
