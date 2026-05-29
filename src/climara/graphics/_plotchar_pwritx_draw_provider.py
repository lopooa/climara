from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ._plotchar_metrics import PlotcharExtentMetrics
from ._plotchar_state import PlotcharState, PlotcharUnsupportedError


@dataclass(frozen=True)
class PwritxDrawPolyline:
    points: tuple[tuple[float, float], ...]
    fillable: bool = False


@dataclass(frozen=True)
class PwritxDrawRequest:
    chrs: str
    state: PlotcharState
    xpos: float
    ypos: float
    size: float
    angle: float
    cntr: float
    fontcap_dir: str | Path | None = None


@dataclass(frozen=True)
class PwritxDrawResult:
    polylines: tuple[PwritxDrawPolyline, ...]
    metrics: PlotcharExtentMetrics
    text: str
    font_number: int
    glyph_count: int


class PwritxDrawProvider(Protocol):
    source_mapped: bool
    source_map_reference: str

    def draw_for_request(self, request: PwritxDrawRequest) -> PwritxDrawResult:
        ...


def validate_pwritx_draw_provider(provider: PwritxDrawProvider) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "PWRITX/font0 SVG draw provider must declare source_mapped=True. "
            "Do not use ad-hoc provider output as NCL PWRITX parity."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "PWRITX/font0 SVG draw provider must declare a source_map_reference."
        )


__all__ = [
    "PwritxDrawPolyline",
    "PwritxDrawProvider",
    "PwritxDrawRequest",
    "PwritxDrawResult",
    "validate_pwritx_draw_provider",
]
