from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._plotchar_legacy_data_provider import LegacyDigitizationRecord
from ._plotchar_legacy_pcfred_provider import LegacyPcfredReadRequest
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyPcfredFileResource:
    path: Path
    role: str

    def validate(self) -> None:
        if not self.path.exists():
            raise PlotcharUnsupportedError(
                f"Legacy PCFRED {self.role} resource does not exist: {self.path}"
            )

        if not self.path.is_file():
            raise PlotcharUnsupportedError(
                f"Legacy PCFRED {self.role} resource is not a file: {self.path}"
            )


@dataclass(frozen=True)
class LegacyPcfredFileBackend:
    """Guarded file-backed PCFRED backend skeleton.

    This class only fixes the future resource boundary. It must not decode
    INDA/IDDA until the NCL PCFRED record layout is fully source-mapped.
    """

    inda_resource: LegacyPcfredFileResource
    idda_resource: LegacyPcfredFileResource
    source_mapped: bool = True
    source_map_reference: str = "docs/ncl_plotchar_legacy_pcfred_file_backend_source_map.md"

    @classmethod
    def from_paths(
        cls,
        *,
        inda_path: str | Path,
        idda_path: str | Path,
    ) -> "LegacyPcfredFileBackend":
        return cls(
            inda_resource=LegacyPcfredFileResource(
                path=Path(inda_path).expanduser().resolve(),
                role="INDA",
            ),
            idda_resource=LegacyPcfredFileResource(
                path=Path(idda_path).expanduser().resolve(),
                role="IDDA",
            ),
        )

    def validate_resources(self) -> None:
        self.inda_resource.validate()
        self.idda_resource.validate()

    def read_record(self, request: LegacyPcfredReadRequest) -> LegacyDigitizationRecord:
        self.validate_resources()

        raise PlotcharUnsupportedError(
            "Legacy PCFRED file-backed INDA/IDDA reading remains guarded. "
            f"Resources exist, but the PCFRED record layout is not decoded yet. "
            f"Requested INDA index {int(request.inda_index)}."
        )


__all__ = [
    "LegacyPcfredFileBackend",
    "LegacyPcfredFileResource",
]
