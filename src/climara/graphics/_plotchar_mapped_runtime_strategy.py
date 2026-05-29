from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class MappedCoordinateRuntimeStrategyBoundary:
    implemented: bool
    reason: str


def mapped_coordinate_runtime_strategy_boundary() -> MappedCoordinateRuntimeStrategyBoundary:
    return MappedCoordinateRuntimeStrategyBoundary(
        implemented=False,
        reason=(
            "Mapped-coordinate runtime strategy is structured but not implemented. "
            "A strategy may only compute metrics after the exact NCL PLCHHQ mapped-coordinate "
            "branch has been translated into Python state transitions, coordinate transforms, "
            "extent updates, and PCGETR-visible state."
        ),
    )


class MappedCoordinateRuntimeStrategy:
    """Runtime strategy boundary for future IMAP != 0 implementation.

    This class intentionally does not implement NCL mapped-coordinate metrics.
    Subclasses must set all of the following only after complete source mapping:

    - source_mapped = True
    - runtime_implemented = True
    - source_map_reference = a non-empty source-map document path
    """

    source_mapped = False
    runtime_implemented = False
    source_map_reference = ""

    def compute(self, request: Any):
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime strategy compute is not implemented. "
            "Do not approximate NCL PLCHHQ mapped-coordinate behavior."
        )


class GuardedMappedCoordinateRuntimeStrategy(MappedCoordinateRuntimeStrategy):
    pass


def default_mapped_coordinate_runtime_strategy() -> MappedCoordinateRuntimeStrategy:
    return GuardedMappedCoordinateRuntimeStrategy()


def require_mapped_coordinate_runtime_strategy(
    strategy: MappedCoordinateRuntimeStrategy | None,
) -> MappedCoordinateRuntimeStrategy:
    if strategy is None:
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime strategy is missing. "
            "NCL PLCHHQ mapped-coordinate branch is not implemented in Python yet."
        )

    return strategy


def validate_source_mapped_runtime_strategy(strategy: MappedCoordinateRuntimeStrategy) -> None:
    if not bool(getattr(strategy, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime strategy is not source-mapped. "
            "Do not use visual, SVG, browser, fixed-width, identity, or estimated "
            "coordinate transforms for NCL PLCHHQ mapped-coordinate behavior."
        )

    reference = str(getattr(strategy, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime strategy must declare source_map_reference."
        )

    if not bool(getattr(strategy, "runtime_implemented", False)):
        raise PlotcharUnsupportedError(
            "Mapped-coordinate runtime strategy declares a source map but has no "
            "implemented runtime. IMAP != 0 must remain guarded."
        )


def compute_mapped_coordinate_with_strategy(request, strategy=None):
    selected = strategy if strategy is not None else getattr(request, "runtime_strategy", None)
    selected = require_mapped_coordinate_runtime_strategy(selected)
    validate_source_mapped_runtime_strategy(selected)
    return selected.compute(request)


__all__ = [
    "GuardedMappedCoordinateRuntimeStrategy",
    "MappedCoordinateRuntimeStrategy",
    "MappedCoordinateRuntimeStrategyBoundary",
    "ProviderBackedMappedCoordinateRuntimeStrategy",
    "compute_mapped_coordinate_with_strategy",
    "default_mapped_coordinate_runtime_strategy",
    "mapped_coordinate_runtime_strategy_boundary",
    "require_mapped_coordinate_runtime_strategy",
    "validate_source_mapped_runtime_strategy",
]


class ProviderBackedMappedCoordinateRuntimeStrategy(MappedCoordinateRuntimeStrategy):
    """Provider-backed mapped-coordinate runtime strategy.

    This strategy does not invent coordinate transforms. It requires a
    source-mapped transform provider on the request. The provider owns the
    NCL-mapped coordinate semantics. This strategy only performs the runtime
    handoff:

    1. validate provider source-map contract
    2. convert the request origin into Plotchar's existing IMAP=0 core space
    3. run the existing high-quality fontcap core with MA forced to 0
    4. convert returned DL/DR/DB/DT through the provider boundary

    The strategy is intentionally opt-in and never used by default.
    """

    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"

    def compute(self, request):
        import copy

        from ._plotchar_mapped_coordinate import (
            MappedCoordinateExtent,
            MappedCoordinatePoint,
            MappedCoordinateResult,
            require_mapped_coordinate_transform_provider,
            validate_source_mapped_transform_provider,
        )
        from ._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent

        provider = require_mapped_coordinate_transform_provider(request.transform_provider)
        validate_source_mapped_transform_provider(provider)

        snapshot = request.snapshot
        user_origin = MappedCoordinatePoint(snapshot.xpos, snapshot.ypos)
        plotchar_origin = provider.user_to_plotchar(user_origin)

        try:
            core_state = copy.deepcopy(request.state)
        except Exception:
            try:
                core_state = copy.copy(request.state)
            except Exception:
                raise PlotcharUnsupportedError(
                    "Mapped-coordinate runtime could not isolate PlotcharState before "
                    "forcing MA=0 for the existing fontcap core."
                )

        pcseti = getattr(core_state, "pcseti", None)
        if not callable(pcseti):
            raise PlotcharUnsupportedError(
                "Mapped-coordinate runtime requires a PlotcharState-like object with pcseti."
            )

        pcseti("MA", 0)

        core_result = compute_plchhq_fontcap_text_extent(
            chrs=request.chrs,
            state=core_state,
            xpos=plotchar_origin.x,
            ypos=plotchar_origin.y,
            size=snapshot.size,
            angle=snapshot.angle,
            cntr=snapshot.cntr,
            fontcap_dir=request.fontcap_dir,
        )

        user_extent = provider.extent_to_user(
            origin=user_origin,
            extent=MappedCoordinateExtent(
                dl=core_result.metrics.dl,
                dr=core_result.metrics.dr,
                db=core_result.metrics.db,
                dt=core_result.metrics.dt,
            ),
        )

        metrics = type(core_result.metrics)(
            dl=user_extent.dl,
            dr=user_extent.dr,
            db=user_extent.db,
            dt=user_extent.dt,
        )

        return MappedCoordinateResult(
            metrics=metrics,
            state=core_result.state,
            text=core_result.text,
            font_number=core_result.font_number,
            glyph_count=core_result.glyph_count,
        )
