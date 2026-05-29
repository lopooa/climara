from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ._plotchar_legacy_data_provider import LegacyDigitizationRecord
from ._plotchar_legacy_digitization_trace import LegacyDigitizationStep
from ._plotchar_legacy_glyph_provider import LegacyGlyphResult
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyIddaDecodeRequest:
    record: LegacyDigitizationRecord
    step: LegacyDigitizationStep
    size: float
    angle: float
    cntr: float


class LegacyIddaGlyphDecoder(Protocol):
    source_mapped: bool
    source_map_reference: str

    def decode_record(self, request: LegacyIddaDecodeRequest) -> LegacyGlyphResult:
        ...


def validate_legacy_idda_decoder(decoder: LegacyIddaGlyphDecoder) -> None:
    if not bool(getattr(decoder, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Legacy IDDA glyph decoder must declare source_mapped=True. "
            "Do not use ad-hoc raw parcel decoding as NCL digitization parity."
        )

    reference = str(getattr(decoder, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Legacy IDDA glyph decoder must declare a source_map_reference."
        )


__all__ = [
    "LegacyIddaDecodeRequest",
    "LegacyIddaGlyphDecoder",
    "validate_legacy_idda_decoder",
]
