
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._plotchar_state import PlotcharUnsupportedError


PWRITX_NONFONTCAP_DOCS = (
    "docs/ncl_plotchar_pwritx_nonfontcap_branch_source_map.md",
    "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
)


@dataclass(frozen=True)
class PwritxNonFontcapBoundary:
    implemented: bool
    reason: str
    required_docs: tuple[str, ...]




@dataclass(frozen=True)
class PwritxNonFontcapResult:
    metrics: Any
    state: Any
    text: str = ""
    font_number: int = -1
    glyph_count: int = 0

@dataclass(frozen=True)
class PwritxNonFontcapRequest:
    chrs: str
    state: Any
    xpos: float
    ypos: float
    size: float
    angle: float
    cntr: float
    fontcap_dir: str | Path | None = None
    runtime_strategy: Any | None = None
    metrics_provider: Any | None = None


def pwritx_nonfontcap_boundary() -> PwritxNonFontcapBoundary:
    return PwritxNonFontcapBoundary(
        implemented=False,
        reason=(
            "NCL PWRITX/font0/non-fontcap behavior is source-mapped but not implemented. "
            "The current Python Plotchar engine supports the audited high-quality fontcap subset only."
        ),
        required_docs=PWRITX_NONFONTCAP_DOCS,
    )


def pwritx_nonfontcap_report_paths(project_root: str | Path = ".") -> tuple[Path, ...]:
    root = Path(project_root)
    return tuple(root / doc for doc in PWRITX_NONFONTCAP_DOCS)


def build_pwritx_nonfontcap_guard_message() -> str:
    boundary = pwritx_nonfontcap_boundary()
    docs = ", ".join(boundary.required_docs)
    return (
        "NCL PWRITX/font0/non-fontcap branch is not implemented in Python yet. "
        f"{boundary.reason} Required source-map documents: {docs}."
    )


def raise_pwritx_nonfontcap_guard() -> None:
    raise PlotcharUnsupportedError(build_pwritx_nonfontcap_guard_message())


def build_pwritx_nonfontcap_request(
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
    metrics_provider: Any | None = None,
) -> PwritxNonFontcapRequest:
    return PwritxNonFontcapRequest(
        chrs=chrs,
        state=state,
        xpos=float(xpos),
        ypos=float(ypos),
        size=float(size),
        angle=float(angle),
        cntr=float(cntr),
        fontcap_dir=fontcap_dir,
        runtime_strategy=runtime_strategy,
        metrics_provider=metrics_provider,
    )


def compute_pwritx_nonfontcap_extent(request: PwritxNonFontcapRequest):
    if request.runtime_strategy is None:
        raise_pwritx_nonfontcap_guard()

    from ._plotchar_pwritx_runtime_strategy import compute_pwritx_with_strategy

    return compute_pwritx_with_strategy(request)


__all__ = [
    "PWRITX_NONFONTCAP_DOCS",
    "PwritxNonFontcapBoundary",
    "PwritxNonFontcapRequest",
    "PwritxNonFontcapResult",
    "build_pwritx_nonfontcap_guard_message",
    "build_pwritx_nonfontcap_request",
    "compute_pwritx_nonfontcap_extent",
    "pwritx_nonfontcap_boundary",
    "pwritx_nonfontcap_report_paths",
    "raise_pwritx_nonfontcap_guard",
]
