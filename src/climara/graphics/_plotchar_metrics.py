from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from ._text_semantics import TextItemSemantics


class PlotcharMetricsNotImplementedError(NotImplementedError):
    pass


@dataclass(frozen=True)
class PlotcharExtentMetrics:
    dl: float
    dr: float
    db: float
    dt: float

    @property
    def width(self) -> float:
        return self.dl + self.dr

    @property
    def height(self) -> float:
        return self.db + self.dt


@dataclass(frozen=True)
class PlotcharMetricsRequest:
    semantics: TextItemSemantics
    x: float
    y: float
    size: float
    angle: float
    cntr: float = -1.0


def has_plotchar_metrics_engine() -> bool:
    from ._plotchar_python_live_engine import has_python_plotchar_mainline_engine

    return has_python_plotchar_mainline_engine()


def build_plotchar_metrics_request(
    semantics: TextItemSemantics,
    *,
    x: float,
    y: float,
    size: Any | None = None,
    angle: Any | None = None,
    cntr: Any | None = None,
) -> PlotcharMetricsRequest:
    resolved_size = semantics.font_height if size is None else float(size)
    resolved_angle = semantics.angle if angle is None else float(angle)
    resolved_cntr = -1.0 if cntr is None else float(cntr)

    return PlotcharMetricsRequest(
        semantics=semantics,
        x=float(x),
        y=float(y),
        size=float(resolved_size),
        angle=float(resolved_angle),
        cntr=resolved_cntr,
    )


def build_plotchar_extent_metrics(
    *,
    dl: float,
    dr: float,
    db: float,
    dt: float,
) -> PlotcharExtentMetrics:
    values = {
        "dl": float(dl),
        "dr": float(dr),
        "db": float(db),
        "dt": float(dt),
    }

    for name, value in values.items():
        if not isfinite(value):
            raise ValueError(f"Plotchar extent metric {name} must be finite")

    return PlotcharExtentMetrics(**values)


def compute_plotchar_extent_metrics(
    request: PlotcharMetricsRequest,
) -> PlotcharExtentMetrics:
    from ._plotchar_python_live_engine import (
        compute_plotchar_extent_metrics_with_python_mainline,
        python_plotchar_mainline_status,
    )

    status = python_plotchar_mainline_status()
    if not status.available:
        raise PlotcharMetricsNotImplementedError(
            status.report
            + " TextItem bbox requires audited PLCHHQ / PCGETR DL, DR, DB, DT semantics; "
            + "climara must not replace this with fixed-width, character-count, SVG, "
            + "browser, or visual-estimation text metrics."
        )

    return compute_plotchar_extent_metrics_with_python_mainline(request)


__all__ = [
    "PlotcharExtentMetrics",
    "PlotcharMetricsNotImplementedError",
    "PlotcharMetricsRequest",
    "build_plotchar_extent_metrics",
    "build_plotchar_metrics_request",
    "compute_plotchar_extent_metrics",
    "has_plotchar_metrics_engine",
]
