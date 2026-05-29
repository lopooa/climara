from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class SizeAddressRuntimeStrategyBoundary:
    implemented: bool
    reason: str


def size_address_runtime_strategy_boundary() -> SizeAddressRuntimeStrategyBoundary:
    return SizeAddressRuntimeStrategyBoundary(
        implemented=False,
        reason=(
            "SIZE/address-unit runtime strategy is structured but not implemented. "
            "A strategy may only compute address-unit SIZE metrics after the exact "
            "NCL PLCHHQ SIZE/address branch has been translated into Python state "
            "transitions, geometry updates, extent updates, and PCGETR-visible state."
        ),
    )


class SizeAddressRuntimeStrategy:
    """Runtime strategy boundary for future address-unit SIZE implementation.

    This class intentionally does not implement NCL address-unit SIZE metrics.
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
            "SIZE/address-unit runtime strategy compute is not implemented. "
            "Do not approximate NCL PLCHHQ address-unit SIZE behavior."
        )


class GuardedSizeAddressRuntimeStrategy(SizeAddressRuntimeStrategy):
    pass


def default_size_address_runtime_strategy() -> SizeAddressRuntimeStrategy:
    return GuardedSizeAddressRuntimeStrategy()


def require_size_address_runtime_strategy(
    strategy: SizeAddressRuntimeStrategy | None,
) -> SizeAddressRuntimeStrategy:
    if strategy is None:
        raise PlotcharUnsupportedError(
            "SIZE/address-unit runtime strategy is missing. "
            "NCL PLCHHQ address-unit SIZE branch is not implemented in Python yet."
        )

    return strategy


def validate_source_mapped_size_address_runtime_strategy(
    strategy: SizeAddressRuntimeStrategy,
) -> None:
    if not bool(getattr(strategy, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "SIZE/address-unit runtime strategy is not source-mapped. "
            "Do not use visual, external vector, external text, fixed advance, count-based, or estimated "
            "metrics for NCL PLCHHQ address-unit SIZE behavior."
        )

    reference = str(getattr(strategy, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "SIZE/address-unit runtime strategy must declare source_map_reference."
        )

    if not bool(getattr(strategy, "runtime_implemented", False)):
        raise PlotcharUnsupportedError(
            "SIZE/address-unit runtime strategy declares a source map but has no "
            "implemented runtime. SIZE/address-unit remains guarded."
        )


def compute_size_address_with_strategy(request, strategy=None):
    selected = strategy if strategy is not None else getattr(request, "runtime_strategy", None)
    selected = require_size_address_runtime_strategy(selected)
    validate_source_mapped_size_address_runtime_strategy(selected)
    return selected.compute(request)




class ProviderBackedSizeAddressRuntimeStrategy(SizeAddressRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_size_address_exact_branch_packet.md"

    def compute(self, request):
        import copy

        from ._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
        from ._plotchar_size_address_provider import (
            require_size_address_scale_provider,
            validate_fractional_core_size,
            validate_source_mapped_size_address_scale_provider,
        )

        provider = require_size_address_scale_provider(request.scale_provider)
        validate_source_mapped_size_address_scale_provider(provider)

        core_size = float(provider.fractional_core_size(request))
        validate_fractional_core_size(core_size)

        try:
            core_state = copy.deepcopy(request.state)
        except Exception:
            try:
                core_state = copy.copy(request.state)
            except Exception:
                raise PlotcharUnsupportedError(
                    "SIZE/address runtime could not isolate PlotcharState before running the existing fractional fontcap core."
                )

        core_result = compute_plchhq_fontcap_text_extent(
            chrs=request.chrs,
            state=core_state,
            xpos=request.xpos,
            ypos=request.ypos,
            size=core_size,
            angle=request.angle,
            cntr=request.cntr,
            fontcap_dir=request.fontcap_dir,
        )

        return provider.result_from_core(request=request, core_result=core_result)

__all__ = [
    "GuardedSizeAddressRuntimeStrategy",
    "SizeAddressRuntimeStrategy",
    "ProviderBackedSizeAddressRuntimeStrategy",
    "SizeAddressRuntimeStrategyBoundary",
    "compute_size_address_with_strategy",
    "default_size_address_runtime_strategy",
    "require_size_address_runtime_strategy",
    "size_address_runtime_strategy_boundary",
    "validate_source_mapped_size_address_runtime_strategy",
]
