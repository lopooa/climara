from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ._plotchar_metrics import PlotcharExtentMetrics
from ._plotchar_state import PlotcharState, PlotcharUnsupportedError


@dataclass(frozen=True)
class MappedDrawPolyline:
    points: tuple[tuple[float, float], ...]
    fillable: bool = False


@dataclass(frozen=True)
class MappedDrawRequest:
    chrs: str
    state: PlotcharState
    xpos: float
    ypos: float
    size: float
    angle: float
    cntr: float
    fontcap_dir: str | Path | None = None


@dataclass(frozen=True)
class MappedDrawResult:
    polylines: tuple[MappedDrawPolyline, ...]
    metrics: PlotcharExtentMetrics
    text: str
    font_number: int
    glyph_count: int


class MappedDrawProvider(Protocol):
    source_mapped: bool
    source_map_reference: str

    def draw_for_request(self, request: MappedDrawRequest) -> MappedDrawResult:
        ...


def validate_mapped_draw_provider(provider: MappedDrawProvider) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Mapped Plotchar draw provider must declare source_mapped=True. "
            "Do not use ad-hoc mapped output as NCL IMAP parity."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Mapped Plotchar draw provider must declare a source_map_reference."
        )


__all__ = [
    "MappedDrawPolyline",
    "MappedDrawProvider",
    "MappedDrawRequest",
    "MappedDrawResult",
    "validate_mapped_draw_provider",
]
