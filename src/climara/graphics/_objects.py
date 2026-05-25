"""
Backend-neutral HLU-style graphics objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class HluObject:
    """Base object with NCL/HLU-style resources."""

    name: str = ""
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)

    def set_values(self, resources: Mapping[str, Any] | None = None, **kwargs: Any):
        if resources:
            self.resources.update(dict(resources))
        if kwargs:
            self.resources.update(kwargs)
        return self

    def add_child(self, child: Any):
        self.children.append(child)
        return child

    def draw(self):
        self.resources["drawn"] = True
        return self


@dataclass
class ScalarField:
    """Scalar data with coordinates and metadata."""

    data: Any
    lon: Any = None
    lat: Any = None
    name: str = ""
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorField:
    """Vector data with coordinates and metadata."""

    u: Any
    v: Any
    lon: Any = None
    lat: Any = None
    name: str = ""
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class HluPlot(HluObject):
    """Base plot object."""

    data: Any = None

    def overlay(self, child: Any):
        return self.add_child(child)


@dataclass
class HluMapPlot(HluPlot):
    """Map plot object."""

    projection: str = "cylindrical"


@dataclass
class HluContourPlot(HluPlot):
    """Contour plot object."""

    levels: list[float] | None = None
    colors: Any = None


@dataclass
class HluVectorPlot(HluPlot):
    """Vector plot object."""

    u: Any = None
    v: Any = None


@dataclass
class HluPanel(HluObject):
    """Panel container object."""

    plots: list[Any] = field(default_factory=list)

    def add_plot(self, plot: Any):
        self.plots.append(plot)
        return plot


ContourPlot = HluContourPlot
ContourMapPlot = HluContourPlot
MapPlot = HluMapPlot
PanelPlot = HluPanel


def as_resources(resources: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if resources:
        out.update(dict(resources))
    out.update(kwargs)
    return out


__all__ = [
    "ContourMapPlot",
    "ContourPlot",
    "HluContourPlot",
    "HluMapPlot",
    "HluObject",
    "HluPanel",
    "HluPlot",
    "HluVectorPlot",
    "MapPlot",
    "PanelPlot",
    "ScalarField",
    "VectorField",
    "as_resources",
]
