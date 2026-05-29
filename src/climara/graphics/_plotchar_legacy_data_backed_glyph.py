from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_legacy_data_provider import (
    LegacyDigitizationDataProvider,
    validate_legacy_digitization_data_provider,
)
from ._plotchar_legacy_glyph_contract import validate_legacy_glyph_result
from ._plotchar_legacy_glyph_provider import (
    LegacyGlyphRequest,
    LegacyGlyphResult,
)
from ._plotchar_legacy_idda_contract import validate_legacy_idda_raw_record
from ._plotchar_legacy_idda_decoder import (
    LegacyIddaDecodeRequest,
    LegacyIddaGlyphDecoder,
    validate_legacy_idda_decoder,
)
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyDataBackedGlyphProvider:
    data_provider: LegacyDigitizationDataProvider
    glyph_decoder: LegacyIddaGlyphDecoder | None = None
    source_mapped: bool = True
    source_map_reference: str = "docs/ncl_plotchar_legacy_indda_idda_decoder_source_map.md"

    def glyph_for_step(self, request: LegacyGlyphRequest) -> LegacyGlyphResult:
        validate_legacy_digitization_data_provider(self.data_provider)

        record = self.data_provider.record_for_inda_index(
            int(request.step.inda_index)
        )

        validate_legacy_idda_raw_record(
            record=record,
            step=request.step,
        )

        if self.glyph_decoder is None:
            raise PlotcharUnsupportedError(
                "Legacy INDA/IDDA glyph decoding remains guarded. "
                f"Located source-mapped record for INDA index {record.inda_index}, "
                "but no source-mapped IDDA glyph decoder was provided."
            )

        validate_legacy_idda_decoder(self.glyph_decoder)

        result = self.glyph_decoder.decode_record(
            LegacyIddaDecodeRequest(
                record=record,
                step=request.step,
                size=float(request.size),
                angle=float(request.angle),
                cntr=float(request.cntr),
            )
        )

        validate_legacy_glyph_result(result)
        return result


__all__ = [
    "LegacyDataBackedGlyphProvider",
]
