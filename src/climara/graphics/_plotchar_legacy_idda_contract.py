from __future__ import annotations

from ._plotchar_legacy_data_provider import LegacyDigitizationRecord
from ._plotchar_legacy_digitization_trace import LegacyDigitizationStep
from ._plotchar_state import PlotcharUnsupportedError


def validate_legacy_idda_raw_record(
    *,
    record: LegacyDigitizationRecord,
    step: LegacyDigitizationStep,
) -> None:
    if int(record.inda_index) != int(step.inda_index):
        raise PlotcharUnsupportedError(
            "Legacy IDDA record/step mismatch: "
            f"record INDA={int(record.inda_index)}, step INDA={int(step.inda_index)}."
        )

    if record.raw_inda_value is None:
        raise PlotcharUnsupportedError(
            f"Legacy IDDA record for INDA index {record.inda_index} has no raw_inda_value."
        )

    if not isinstance(record.raw_inda_value, int):
        raise PlotcharUnsupportedError(
            f"Legacy IDDA record raw_inda_value must be int, got {type(record.raw_inda_value).__name__}."
        )

    if not record.raw_idda_values:
        raise PlotcharUnsupportedError(
            f"Legacy IDDA record for INDA index {record.inda_index} has empty raw_idda_values."
        )

    for i, value in enumerate(record.raw_idda_values):
        if not isinstance(value, int):
            raise PlotcharUnsupportedError(
                "Legacy IDDA raw_idda_values must contain only int values. "
                f"At position {i}, got {type(value).__name__}."
            )


__all__ = [
    "validate_legacy_idda_raw_record",
]
