from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HluPrimitive:
    """NCL/HLU-style primitive object.

    This mirrors the idea of HLU primitive objects.

    coord_system:
        data  : attached to a plot data coordinate system
        ndc   : workstation normalized device coordinates
    """

    coord_system: str = "data"
    draw_order: str = "draw"
    resources: dict = field(default_factory=dict)
    name: str | None = None


@dataclass
class HluPolyline(HluPrimitive):
    """NCL/HLU-style polyline primitive."""

    x: list = field(default_factory=list)
    y: list = field(default_factory=list)


@dataclass
class HluPolygon(HluPrimitive):
    """NCL/HLU-style polygon primitive."""

    x: list = field(default_factory=list)
    y: list = field(default_factory=list)


@dataclass
class HluMarker(HluPrimitive):
    """NCL/HLU-style marker primitive."""

    x: list = field(default_factory=list)
    y: list = field(default_factory=list)
