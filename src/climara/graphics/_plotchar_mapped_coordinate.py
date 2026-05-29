from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._plotchar_metrics import PlotcharExtentMetrics
from ._plotchar_state import PlotcharUnsupportedError


MAPPED_BRANCH_DOCS = (
    "docs/ncl_plotchar_mapped_coordinate_branch_source_map.md",
    "docs/ncl_plotchar_mapped_branch_labels.md",
    "docs/ncl_plotchar_mapped_label_resolution.md",
    "docs/ncl_plotchar_mapped_branch_readiness.md",
    "docs/ncl_plotchar_mapped_exact_branch_packet.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
)


@dataclass(frozen=True)
class MappedCoordinateImplementationBoundary:
    implemented: bool
    reason: str
    required_docs: tuple[str, ...]


@dataclass(frozen=True)
class MappedCoordinateStateSnapshot:
    imap: int
    xpos: float
    ypos: float
    size: float
    angle: float
    cntr: float
    textitem_mode: int
    quality_index: int
    font_number: int


@dataclass(frozen=True)
class MappedCoordinateRequest:
    chrs: str
    state: Any
    snapshot: MappedCoordinateStateSnapshot
    fontcap_dir: str | Path | None = None
    transform_provider: MappedCoordinateTransformProvider | None = None
    runtime_strategy: Any | None = None


@dataclass(frozen=True)
class MappedCoordinateResult:
    metrics: PlotcharExtentMetrics
    state: Any
    text: str = ""
    font_number: int = -1
    glyph_count: int = 0



@dataclass(frozen=True)
class MappedCoordinatePoint:
    x: float
    y: float


@dataclass(frozen=True)
class MappedCoordinateExtent:
    dl: float
    dr: float
    db: float
    dt: float


class MappedCoordinateTransformProvider:
    """Boundary for future NCL mapped-coordinate conversion.

    This provider intentionally has no default mathematical implementation.
    NCL mapped-coordinate behavior must be filled from the complete PLCHHQ /
    coordinate-transform source branch, not from visual approximation.

    Subclasses must set source_mapped=True only after the implementation is
    mapped against the local NCL source reports listed in MAPPED_BRANCH_DOCS.
    """

    source_mapped = False
    source_map_reference = ""

    def user_to_plotchar(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        raise_mapped_coordinate_guard()

    def plotchar_to_user(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        raise_mapped_coordinate_guard()

    def extent_to_user(
        self,
        *,
        origin: MappedCoordinatePoint,
        extent: MappedCoordinateExtent,
    ) -> MappedCoordinateExtent:
        raise_mapped_coordinate_guard()


class GuardedMappedCoordinateTransformProvider(MappedCoordinateTransformProvider):
    pass


def default_mapped_coordinate_transform_provider() -> MappedCoordinateTransformProvider:
    return GuardedMappedCoordinateTransformProvider()


def require_mapped_coordinate_transform_provider(
    provider: MappedCoordinateTransformProvider | None,
) -> MappedCoordinateTransformProvider:
    if provider is None:
        raise_mapped_coordinate_guard()

    return provider

def mapped_coordinate_boundary() -> MappedCoordinateImplementationBoundary:
    return MappedCoordinateImplementationBoundary(
        implemented=False,
        reason=(
            "NCL PLCHHQ mapped-coordinate semantics are source-mapped and readiness-gated, "
            "but runtime behavior is not implemented yet. IMAP != 0 must remain guarded "
            "until coordinate conversions, geometry state, DL/DR/DB/DT, and PCGETR-visible "
            "state are implemented from the complete NCL branch."
        ),
        required_docs=MAPPED_BRANCH_DOCS,
    )


def mapped_coordinate_report_paths(project_root: str | Path = ".") -> tuple[Path, ...]:
    root = Path(project_root)
    return tuple(root / doc for doc in MAPPED_BRANCH_DOCS)


def build_mapped_coordinate_guard_message() -> str:
    boundary = mapped_coordinate_boundary()
    docs = ", ".join(boundary.required_docs)

    return (
        "NCL Plotchar mapped-coordinate branch is not implemented in Python yet. "
        "Current Python Plotchar mainline requires IMAP == 0. "
        f"{boundary.reason} "
        f"Required source-map documents: {docs}."
    )


def raise_mapped_coordinate_guard() -> None:
    raise PlotcharUnsupportedError(build_mapped_coordinate_guard_message())


def _state_int(state: Any, resource: str, fallback: int) -> int:
    pcgeti = getattr(state, "pcgeti", None)
    if callable(pcgeti):
        try:
            return int(pcgeti(resource))
        except Exception:
            pass

    name_map = {
        "MA": ("imap", "ma", "mapped", "map"),
        "TE": ("textitem_mode", "te"),
        "QU": ("quality_index", "qu", "iquf"),
        "FN": ("font_number", "font", "nodf"),
    }

    for name in name_map.get(resource, (resource.lower(),)):
        if hasattr(state, name):
            try:
                return int(getattr(state, name))
            except Exception:
                continue

    return fallback


def mapped_coordinate_requested(state: Any) -> bool:
    return _state_int(state, "MA", 0) != 0


def dispatch_mapped_coordinate_or_continue(state: Any) -> None:
    if mapped_coordinate_requested(state):
        raise_mapped_coordinate_guard()


def build_mapped_coordinate_state_snapshot(
    *,
    state: Any,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
) -> MappedCoordinateStateSnapshot:
    return MappedCoordinateStateSnapshot(
        imap=_state_int(state, "MA", 0),
        xpos=float(xpos),
        ypos=float(ypos),
        size=float(size),
        angle=float(angle),
        cntr=float(cntr),
        # This runtime API is currently entered only from TextItem measurement
        # planning. Some PlotcharState versions do not expose TE through pcgeti,
        # so default to the TextItem boundary while still validating explicit
        # readable non-TextItem states when they exist.
        textitem_mode=_state_int(state, "TE", 1),
        quality_index=_state_int(state, "QU", -1),
        font_number=_state_int(state, "FN", -1),
    )


def build_mapped_coordinate_request(
    *,
    chrs: str,
    state: Any,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    fontcap_dir: str | Path | None = None,
    transform_provider: MappedCoordinateTransformProvider | None = None,
    runtime_strategy: Any | None = None,
) -> MappedCoordinateRequest:
    snapshot = build_mapped_coordinate_state_snapshot(
        state=state,
        xpos=xpos,
        ypos=ypos,
        size=size,
        angle=angle,
        cntr=cntr,
    )

    return MappedCoordinateRequest(
        chrs=chrs,
        state=state,
        snapshot=snapshot,
        fontcap_dir=fontcap_dir,
        transform_provider=transform_provider,
        runtime_strategy=runtime_strategy,
    )



def validate_source_mapped_transform_provider(
    provider: MappedCoordinateTransformProvider,
) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Mapped-coordinate transform provider is not source-mapped. "
            "Do not use identity, visual, browser, SVG, fixed-width, or estimated "
            "coordinate transforms for NCL PLCHHQ mapped-coordinate behavior."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Mapped-coordinate transform provider must declare a source_map_reference "
            "before runtime use."
        )

def validate_mapped_coordinate_request(request: MappedCoordinateRequest) -> None:
    snapshot = request.snapshot

    if snapshot.imap == 0:
        raise PlotcharUnsupportedError(
            "Mapped-coordinate implementation boundary received IMAP == 0. "
            "This request belongs to the existing unmapped fontcap mainline."
        )

    if snapshot.textitem_mode != 1:
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime is only planned for TextItem measurement first. "
            "Non-TextItem PLCHHQ mapped calls remain guarded."
        )

    if snapshot.quality_index != 0:
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime is only planned for the high-quality fontcap path first. "
            "Medium, Low, Workstation, PWRITX, and non-fontcap mapped paths remain guarded."
        )

    if not (0.0 < snapshot.size < 1.0):
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime is only planned for the current fractional SIZE TextItem subset first. "
            "Address-unit SIZE semantics remain guarded."
        )


def compute_mapped_coordinate_extent(request: MappedCoordinateRequest) -> MappedCoordinateResult:
    validate_mapped_coordinate_request(request)
    provider = require_mapped_coordinate_transform_provider(request.transform_provider)
    validate_source_mapped_transform_provider(provider)

    from ._plotchar_mapped_runtime_strategy import compute_mapped_coordinate_with_strategy

    return compute_mapped_coordinate_with_strategy(request)


__all__ = [
    "MAPPED_BRANCH_DOCS",
    "GuardedMappedCoordinateTransformProvider",
    "MappedCoordinateExtent",
    "MappedCoordinateImplementationBoundary",
    "MappedCoordinatePoint",
    "MappedCoordinateTransformProvider",
    "MappedCoordinateRequest",
    "MappedCoordinateResult",
    "MappedCoordinateStateSnapshot",
    "build_mapped_coordinate_guard_message",
    "build_mapped_coordinate_request",
    "build_mapped_coordinate_state_snapshot",
    "compute_mapped_coordinate_extent",
    "default_mapped_coordinate_transform_provider",
    "dispatch_mapped_coordinate_or_continue",
    "mapped_coordinate_boundary",
    "mapped_coordinate_report_paths",
    "mapped_coordinate_requested",
    "raise_mapped_coordinate_guard",
    "require_mapped_coordinate_transform_provider",
    "validate_mapped_coordinate_request",
    "validate_source_mapped_transform_provider",
]
