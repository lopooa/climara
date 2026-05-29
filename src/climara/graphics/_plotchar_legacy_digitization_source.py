from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyDigitizationSourceHit:
    path: Path
    matched_terms: tuple[str, ...]


@dataclass(frozen=True)
class LegacyDigitizationSourceReport:
    ncl_src_root: Path
    hits: tuple[LegacyDigitizationSourceHit, ...]


_SEARCH_TERMS = (
    "PCBDFF",
    "PCBLDA",
    "INDA",
    "IDDA",
    "ICND",
    "ICDD",
    "CDPC",
    "IASC",
    "IFRO",
    "IFGR",
    "ISZP",
    "ISZI",
    "ISZC",
    "ICSU",
    "ICSL",
)


def find_legacy_digitization_sources(
    ncl_src_root: str | Path,
    *,
    max_file_size: int = 2_000_000,
) -> LegacyDigitizationSourceReport:
    root = Path(ncl_src_root).expanduser().resolve()

    if not root.exists():
        raise PlotcharUnsupportedError(
            f"NCL source root does not exist: {root}"
        )

    hits: list[LegacyDigitizationSourceHit] = []

    suffixes = {
        ".f",
        ".F",
        ".f90",
        ".F90",
        ".c",
        ".h",
        ".inc",
        ".txt",
        ".dat",
    }

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix not in suffixes:
            continue

        try:
            if path.stat().st_size > max_file_size:
                continue
        except OSError:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        upper = text.upper()
        matched = tuple(term for term in _SEARCH_TERMS if term in upper)

        if matched:
            hits.append(
                LegacyDigitizationSourceHit(
                    path=path,
                    matched_terms=matched,
                )
            )

    return LegacyDigitizationSourceReport(
        ncl_src_root=root,
        hits=tuple(hits),
    )


def require_legacy_digitization_sources(
    ncl_src_root: str | Path,
) -> LegacyDigitizationSourceReport:
    report = find_legacy_digitization_sources(ncl_src_root)

    if not report.hits:
        raise PlotcharUnsupportedError(
            "No NCL legacy digitization source candidates found. "
            "Cannot implement INDA/IDDA reader without locating PCBDFF/PCBLDA data source."
        )

    return report


__all__ = [
    "LegacyDigitizationSourceHit",
    "LegacyDigitizationSourceReport",
    "find_legacy_digitization_sources",
    "require_legacy_digitization_sources",
]
