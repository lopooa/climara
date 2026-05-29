from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ._plotchar_metrics import PlotcharExtentMetrics
from ._plotchar_state import PlotcharState, PlotcharUnsupportedError


@dataclass(frozen=True)
class GreekDrawPolyline:
    points: tuple[tuple[float, float], ...]
    fillable: bool = False


@dataclass(frozen=True)
class GreekDrawRequest:
    chrs: str
    state: PlotcharState
    xpos: float
    ypos: float
    size: float
    angle: float
    cntr: float
    fontcap_dir: str | Path | None = None


@dataclass(frozen=True)
class GreekDrawResult:
    polylines: tuple[GreekDrawPolyline, ...]
    metrics: PlotcharExtentMetrics
    text: str
    font_number: int
    glyph_count: int


class GreekDrawProvider(Protocol):
    source_mapped: bool
    source_map_reference: str

    def draw_for_request(self, request: GreekDrawRequest) -> GreekDrawResult:
        ...


def validate_greek_draw_provider(provider: GreekDrawProvider) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "G Greek SVG draw provider must declare source_mapped=True. "
            "Do not use ad-hoc output as NCL Greek/IFGR parity."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "G Greek SVG draw provider must declare a source_map_reference."
        )


__all__ = [
    "GreekDrawPolyline",
    "GreekDrawProvider",
    "GreekDrawRequest",
    "GreekDrawResult",
    "validate_greek_draw_provider",
]
