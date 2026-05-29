from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ._plotchar_legacy_digitization_trace import LegacyDigitizationStep
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyGlyphPolyline:
    points: tuple[tuple[float, float], ...]
    fillable: bool = False


@dataclass(frozen=True)
class LegacyGlyphRequest:
    step: LegacyDigitizationStep
    size: float
    angle: float
    cntr: float


@dataclass(frozen=True)
class LegacyGlyphResult:
    polylines: tuple[LegacyGlyphPolyline, ...]
    advance: float
    dl: float
    dr: float
    db: float
    dt: float


class LegacyGlyphProvider(Protocol):
    source_mapped: bool
    source_map_reference: str

    def glyph_for_step(self, request: LegacyGlyphRequest) -> LegacyGlyphResult:
        ...


def validate_legacy_glyph_provider(provider: LegacyGlyphProvider) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Legacy INDA/IDDA glyph provider must declare source_mapped=True. "
            "Do not use ad-hoc glyph output as NCL legacy digitization parity."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Legacy INDA/IDDA glyph provider must declare a source_map_reference."
        )


__all__ = [
    "LegacyGlyphPolyline",
    "LegacyGlyphProvider",
    "LegacyGlyphRequest",
    "LegacyGlyphResult",
    "validate_legacy_glyph_provider",
]
