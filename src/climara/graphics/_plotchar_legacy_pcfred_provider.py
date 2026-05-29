from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ._plotchar_legacy_data_provider import LegacyDigitizationRecord
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyPcfredReadRequest:
    inda_index: int


class LegacyPcfredBackend(Protocol):
    source_mapped: bool
    source_map_reference: str

    def read_record(self, request: LegacyPcfredReadRequest) -> LegacyDigitizationRecord:
        ...


def validate_legacy_pcfred_backend(backend: LegacyPcfredBackend) -> None:
    if not bool(getattr(backend, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Legacy PCFRED backend must declare source_mapped=True. "
            "Do not use ad-hoc INDA/IDDA records as NCL digitization parity."
        )

    reference = str(getattr(backend, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Legacy PCFRED backend must declare a source_map_reference."
        )


@dataclass(frozen=True)
class LegacyPcfredDataProvider:
    backend: LegacyPcfredBackend | None = None
    source_mapped: bool = True
    source_map_reference: str = "docs/ncl_plotchar_legacy_pcfred_source_map.md"

    def record_for_inda_index(self, inda_index: int) -> LegacyDigitizationRecord:
        if self.backend is None:
            raise PlotcharUnsupportedError(
                "Legacy PCFRED INDA/IDDA data reading remains guarded. "
                "Provide a source-mapped LegacyPcfredBackend before enabling real legacy glyph records."
            )

        validate_legacy_pcfred_backend(self.backend)

        record = self.backend.read_record(
            LegacyPcfredReadRequest(
                inda_index=int(inda_index),
            )
        )

        if int(record.inda_index) != int(inda_index):
            raise PlotcharUnsupportedError(
                "Legacy PCFRED backend returned a record for the wrong INDA index: "
                f"requested {int(inda_index)}, got {int(record.inda_index)}."
            )

        return record


__all__ = [
    "LegacyPcfredBackend",
    "LegacyPcfredDataProvider",
    "LegacyPcfredReadRequest",
    "validate_legacy_pcfred_backend",
]
