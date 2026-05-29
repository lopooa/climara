from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._plotchar_state import PlotcharUnsupportedError


SIZE_ADDRESS_UNIT_DOCS = (
    "docs/ncl_plotchar_size_address_unit_branch_source_map.md",
    "docs/ncl_plotchar_size_address_exact_branch_packet.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
)


@dataclass(frozen=True)
class SizeAddressUnitBoundary:
    implemented: bool
    reason: str
    required_docs: tuple[str, ...]




@dataclass(frozen=True)
class SizeAddressUnitResult:
    metrics: Any
    state: Any
    text: str = ""
    font_number: int = -1
    glyph_count: int = 0

@dataclass(frozen=True)
class SizeAddressUnitRequest:
    chrs: str
    state: Any
    xpos: float
    ypos: float
    size: float
    angle: float
    cntr: float
    fontcap_dir: str | Path | None = None
    runtime_strategy: Any | None = None
    scale_provider: Any | None = None


def size_address_unit_boundary() -> SizeAddressUnitBoundary:
    return SizeAddressUnitBoundary(
        implemented=False,
        reason=(
            "NCL PLCHHQ address-unit SIZE semantics are source-mapped but not implemented. "
            "Current Python Plotchar mainline supports only fractional TextItem SIZE with "
            "0 < SIZE < 1."
        ),
        required_docs=SIZE_ADDRESS_UNIT_DOCS,
    )


def size_address_unit_report_paths(project_root: str | Path = ".") -> tuple[Path, ...]:
    root = Path(project_root)
    return tuple(root / doc for doc in SIZE_ADDRESS_UNIT_DOCS)


def size_address_unit_requested(size: float) -> bool:
    value = float(size)
    return not (0.0 < value < 1.0)


def build_size_address_unit_guard_message(size: float) -> str:
    value = float(size)
    boundary = size_address_unit_boundary()
    docs = ", ".join(boundary.required_docs)

    if value <= 0.0:
        contract_phrase = "SIZE <= 0.0"
    elif value >= 1.0:
        contract_phrase = "fractional SIZE < 1.0; SIZE >= 1.0"
    else:
        contract_phrase = "SIZE outside fractional TextItem subset"

    return (
        f"NCL Plotchar address-unit SIZE is not implemented in Python yet. "
        f"{contract_phrase}. Got SIZE={value!r}. "
        "Current Python Plotchar mainline requires 0 < SIZE < 1. "
        f"{boundary.reason} Required source-map documents: {docs}."
    )


def raise_size_address_unit_guard(size: float) -> None:
    raise PlotcharUnsupportedError(build_size_address_unit_guard_message(size))


def validate_fractional_textitem_size(size: float) -> None:
    if size_address_unit_requested(size):
        raise_size_address_unit_guard(size)


def build_size_address_unit_request(
    *,
    chrs: str,
    state: Any,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    fontcap_dir: str | Path | None = None,
    runtime_strategy: Any | None = None,
    scale_provider: Any | None = None,
) -> SizeAddressUnitRequest:
    return SizeAddressUnitRequest(
        chrs=chrs,
        state=state,
        xpos=float(xpos),
        ypos=float(ypos),
        size=float(size),
        angle=float(angle),
        cntr=float(cntr),
        fontcap_dir=fontcap_dir,
        runtime_strategy=runtime_strategy,
        scale_provider=scale_provider,
    )


def compute_size_address_unit_extent(request: SizeAddressUnitRequest):
    if request.runtime_strategy is None:
        raise_size_address_unit_guard(request.size)

    from ._plotchar_size_runtime_strategy import compute_size_address_with_strategy

    return compute_size_address_with_strategy(request)


__all__ = [
    "SIZE_ADDRESS_UNIT_DOCS",
    "SizeAddressUnitBoundary",
    "SizeAddressUnitRequest",
    "SizeAddressUnitResult",
    "build_size_address_unit_guard_message",
    "build_size_address_unit_request",
    "compute_size_address_unit_extent",
    "raise_size_address_unit_guard",
    "size_address_unit_boundary",
    "size_address_unit_report_paths",
    "size_address_unit_requested",
    "validate_fractional_textitem_size",
]
