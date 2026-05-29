from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyDigitizationRecord:
    inda_index: int
    raw_inda_value: int | None = None
    raw_idda_values: tuple[int, ...] = ()
    source_note: str = ""


class LegacyDigitizationDataProvider(Protocol):
    source_mapped: bool
    source_map_reference: str

    def record_for_inda_index(self, inda_index: int) -> LegacyDigitizationRecord:
        ...


def validate_legacy_digitization_data_provider(
    provider: LegacyDigitizationDataProvider,
) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Legacy INDA/IDDA data provider must declare source_mapped=True. "
            "Do not use ad-hoc data as NCL legacy digitization parity."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Legacy INDA/IDDA data provider must declare a source_map_reference."
        )


__all__ = [
    "LegacyDigitizationDataProvider",
    "LegacyDigitizationRecord",
    "validate_legacy_digitization_data_provider",
]
