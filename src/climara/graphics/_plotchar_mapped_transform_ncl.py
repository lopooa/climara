from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateTransformProvider,
)
from ._plotchar_state import PlotcharUnsupportedError


NCL_COORDINATE_TRANSFORM_DOCS = (
    "docs/ncl_plotchar_coordinate_transform_source_map.md",
    "docs/ncl_plotchar_mapped_coordinate_branch_source_map.md",
    "docs/ncl_plotchar_mapped_exact_branch_packet.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
)



@dataclass(frozen=True)
class NclCoordinateTransformDirectionContract:
    cfux: str
    cfuy: str
    cufx: str
    cufy: str
    getset: str
    set_call: str
    source_map_reference: str
    manually_verified: bool = False


def guarded_ncl_coordinate_transform_direction_contract() -> NclCoordinateTransformDirectionContract:
    return NclCoordinateTransformDirectionContract(
        cfux="unverified",
        cfuy="unverified",
        cufx="unverified",
        cufy="unverified",
        getset="unverified",
        set_call="unverified",
        source_map_reference="docs/ncl_coordinate_transform_direction_readiness.md",
        manually_verified=False,
    )


def validate_ncl_coordinate_transform_direction_contract(
    contract: NclCoordinateTransformDirectionContract,
) -> None:
    if not contract.manually_verified:
        raise PlotcharUnsupportedError(
            "NCL coordinate-transform direction contract is not manually verified. "
            "CFUX/CFUY/CUFX/CUFY/GETSET/SET direction semantics must be verified from "
            "local NCL source before implementing mapped-coordinate runtime."
        )

    fields = (
        contract.cfux,
        contract.cfuy,
        contract.cufx,
        contract.cufy,
        contract.getset,
        contract.set_call,
    )

    if any(value.strip().lower() in {"", "unverified", "unknown"} for value in fields):
        raise PlotcharUnsupportedError(
            "NCL coordinate-transform direction contract contains unverified fields."
        )

    if not contract.source_map_reference.strip():
        raise PlotcharUnsupportedError(
            "NCL coordinate-transform direction contract requires source_map_reference."
        )

@dataclass(frozen=True)
class NclMappedCoordinateTransformBoundary:
    implemented: bool
    reason: str
    required_docs: tuple[str, ...]


def ncl_mapped_coordinate_transform_boundary() -> NclMappedCoordinateTransformBoundary:
    return NclMappedCoordinateTransformBoundary(
        implemented=False,
        reason=(
            "NCL coordinate transform provider is not implemented yet. "
            "CFUX/CFUY/CUFX/CUFY/GETSET/SET semantics must be mapped from the local "
            "NCL source before any mapped-coordinate runtime can use this provider."
        ),
        required_docs=NCL_COORDINATE_TRANSFORM_DOCS,
    )


class NclMappedCoordinateTransformProvider(MappedCoordinateTransformProvider):
    """Future source-mapped NCL coordinate transform provider.

    This class is intentionally guarded. It must not use identity transforms,
    browser metrics, SVG coordinate tricks, fixed-width estimates, or visual
    approximation. When implemented, it must map the local NCL source semantics
    for CFUX/CFUY/CUFX/CUFY/GETSET/SET.
    """

    source_mapped = False
    source_map_reference = ""

    def user_to_plotchar(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        raise_ncl_mapped_transform_guard()

    def plotchar_to_user(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        raise_ncl_mapped_transform_guard()

    def extent_to_user(
        self,
        *,
        origin: MappedCoordinatePoint,
        extent: MappedCoordinateExtent,
    ) -> MappedCoordinateExtent:
        raise_ncl_mapped_transform_guard()


def ncl_coordinate_transform_report_paths(project_root: str | Path = ".") -> tuple[Path, ...]:
    root = Path(project_root)
    return tuple(root / doc for doc in NCL_COORDINATE_TRANSFORM_DOCS)


def build_ncl_mapped_transform_guard_message() -> str:
    boundary = ncl_mapped_coordinate_transform_boundary()
    docs = ", ".join(boundary.required_docs)

    return (
        "NCL mapped-coordinate transform provider is not implemented. "
        f"{boundary.reason} Required source-map documents: {docs}."
    )


def raise_ncl_mapped_transform_guard() -> None:
    raise PlotcharUnsupportedError(build_ncl_mapped_transform_guard_message())



@dataclass(frozen=True)
class NclWindowViewportState:
    """Explicit GETSET/SET-like window and viewport state.

    Naming follows the common NCAR Graphics GETSET ordering:
    viewport left/right/bottom/top and window left/right/bottom/top.
    This object is explicit so Python does not rely on hidden global GKS state.
    """

    viewport_left: float
    viewport_right: float
    viewport_bottom: float
    viewport_top: float
    window_left: float
    window_right: float
    window_bottom: float
    window_top: float
    log_scaling_flag: int = 1


def _require_nonzero_span(name: str, left: float, right: float) -> None:
    if float(right) == float(left):
        raise PlotcharUnsupportedError(f"NCL coordinate transform has zero {name} span.")


def _linear_map(value: float, src0: float, src1: float, dst0: float, dst1: float) -> float:
    _require_nonzero_span("source", src0, src1)
    return float(dst0) + (float(value) - float(src0)) * (float(dst1) - float(dst0)) / (float(src1) - float(src0))


def _validate_linear_contract(contract: NclCoordinateTransformDirectionContract) -> None:
    validate_ncl_coordinate_transform_direction_contract(contract)

    expected = {
        "cfux": "user-to-fractional-x",
        "cfuy": "user-to-fractional-y",
        "cufx": "fractional-to-user-x",
        "cufy": "fractional-to-user-y",
        "getset": "viewport-window-read",
        "set_call": "viewport-window-write",
    }

    actual = {
        "cfux": contract.cfux,
        "cfuy": contract.cfuy,
        "cufx": contract.cufx,
        "cufy": contract.cufy,
        "getset": contract.getset,
        "set_call": contract.set_call,
    }

    for key, expected_value in expected.items():
        if actual[key] != expected_value:
            raise PlotcharUnsupportedError(
                f"NCL coordinate-transform contract field {key}={actual[key]!r} "
                f"does not match expected {expected_value!r} for the linear window/viewport provider."
            )


class NclLinearWindowViewportTransformProvider(NclMappedCoordinateTransformProvider):
    """Source-contract-gated linear window/viewport transform provider.

    This provider is not default. It requires an explicit manually verified
    direction contract and explicit GETSET/SET-like window/viewport state.

    It implements only linear window/viewport transforms. Log scaling, map
    projections, and non-linear transforms remain guarded.
    """

    source_mapped = True

    def __init__(
        self,
        *,
        state: NclWindowViewportState,
        direction_contract: NclCoordinateTransformDirectionContract,
    ) -> None:
        _validate_linear_contract(direction_contract)

        if int(state.log_scaling_flag) != 1:
            raise PlotcharUnsupportedError(
                "NCL linear window/viewport provider currently supports only linear GETSET flag 1."
            )

        _require_nonzero_span("window-x", state.window_left, state.window_right)
        _require_nonzero_span("window-y", state.window_bottom, state.window_top)
        _require_nonzero_span("viewport-x", state.viewport_left, state.viewport_right)
        _require_nonzero_span("viewport-y", state.viewport_bottom, state.viewport_top)

        self.state = state
        self.direction_contract = direction_contract
        self.source_map_reference = direction_contract.source_map_reference

    def user_to_plotchar(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        s = self.state
        return MappedCoordinatePoint(
            x=_linear_map(point.x, s.window_left, s.window_right, s.viewport_left, s.viewport_right),
            y=_linear_map(point.y, s.window_bottom, s.window_top, s.viewport_bottom, s.viewport_top),
        )

    def plotchar_to_user(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        s = self.state
        return MappedCoordinatePoint(
            x=_linear_map(point.x, s.viewport_left, s.viewport_right, s.window_left, s.window_right),
            y=_linear_map(point.y, s.viewport_bottom, s.viewport_top, s.window_bottom, s.window_top),
        )

    def extent_to_user(
        self,
        *,
        origin: MappedCoordinatePoint,
        extent: MappedCoordinateExtent,
    ) -> MappedCoordinateExtent:
        plot_origin = self.user_to_plotchar(origin)

        left_user = self.plotchar_to_user(
            MappedCoordinatePoint(plot_origin.x - extent.dl, plot_origin.y)
        )
        right_user = self.plotchar_to_user(
            MappedCoordinatePoint(plot_origin.x + extent.dr, plot_origin.y)
        )
        bottom_user = self.plotchar_to_user(
            MappedCoordinatePoint(plot_origin.x, plot_origin.y - extent.db)
        )
        top_user = self.plotchar_to_user(
            MappedCoordinatePoint(plot_origin.x, plot_origin.y + extent.dt)
        )

        return MappedCoordinateExtent(
            dl=origin.x - left_user.x,
            dr=right_user.x - origin.x,
            db=origin.y - bottom_user.y,
            dt=top_user.y - origin.y,
        )

__all__ = [
    "NCL_COORDINATE_TRANSFORM_DOCS",
    "NclCoordinateTransformDirectionContract",
    "NclMappedCoordinateTransformBoundary",
    "NclWindowViewportState",
    "NclLinearWindowViewportTransformProvider",
    "NclMappedCoordinateTransformProvider",
    "build_ncl_mapped_transform_guard_message",
    "ncl_coordinate_transform_report_paths",
    "ncl_mapped_coordinate_transform_boundary",
    "guarded_ncl_coordinate_transform_direction_contract",
    "validate_ncl_coordinate_transform_direction_contract",
    "raise_ncl_mapped_transform_guard",
]
