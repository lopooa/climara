from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class PwritxRuntimeStrategyBoundary:
    implemented: bool
    reason: str


def pwritx_runtime_strategy_boundary() -> PwritxRuntimeStrategyBoundary:
    return PwritxRuntimeStrategyBoundary(
        implemented=False,
        reason=(
            "PWRITX/font0/non-fontcap runtime strategy is structured but not implemented. "
            "A strategy may only compute metrics after the exact NCL PWRITX/font0/non-fontcap "
            "branch has been translated into Python state transitions, text extents, "
            "font database access, and PCGETR-visible state."
        ),
    )


class PwritxRuntimeStrategy:
    source_mapped = False
    runtime_implemented = False
    source_map_reference = ""

    def compute(self, request: Any):
        raise PlotcharUnsupportedError(
            "PWRITX/font0/non-fontcap runtime strategy compute is not implemented. "
            "Do not approximate NCL PWRITX/font0/non-fontcap behavior."
        )


class GuardedPwritxRuntimeStrategy(PwritxRuntimeStrategy):
    pass


def default_pwritx_runtime_strategy() -> PwritxRuntimeStrategy:
    return GuardedPwritxRuntimeStrategy()


def require_pwritx_runtime_strategy(strategy: PwritxRuntimeStrategy | None) -> PwritxRuntimeStrategy:
    if strategy is None:
        raise PlotcharUnsupportedError(
            "PWRITX/font0/non-fontcap runtime strategy is missing. "
            "NCL PWRITX/font0/non-fontcap branch is not implemented in Python yet."
        )
    return strategy


def validate_source_mapped_pwritx_runtime_strategy(strategy: PwritxRuntimeStrategy) -> None:
    if not bool(getattr(strategy, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "PWRITX/font0/non-fontcap runtime strategy is not source-mapped. "
            "Do not use substitute text metrics for this NCL branch."
        )

    reference = str(getattr(strategy, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "PWRITX/font0/non-fontcap runtime strategy must declare source_map_reference."
        )

    if not bool(getattr(strategy, "runtime_implemented", False)):
        raise PlotcharUnsupportedError(
            "PWRITX/font0/non-fontcap runtime strategy declares a source map but has no "
            "implemented runtime. PWRITX/font0/non-fontcap remains guarded."
        )


def compute_pwritx_with_strategy(request, strategy=None):
    selected = strategy if strategy is not None else getattr(request, "runtime_strategy", None)
    selected = require_pwritx_runtime_strategy(selected)
    validate_source_mapped_pwritx_runtime_strategy(selected)
    return selected.compute(request)




class ProviderBackedPwritxRuntimeStrategy(PwritxRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"

    def compute(self, request):
        from ._plotchar_pwritx_provider import (
            require_pwritx_metrics_provider,
            validate_source_mapped_pwritx_metrics_provider,
        )

        provider = require_pwritx_metrics_provider(request.metrics_provider)
        validate_source_mapped_pwritx_metrics_provider(provider)
        return provider.metrics_for_request(request)

__all__ = [
    "GuardedPwritxRuntimeStrategy",
    "ProviderBackedPwritxRuntimeStrategy",
    "PwritxRuntimeStrategy",
    "PwritxRuntimeStrategyBoundary",
    "compute_pwritx_with_strategy",
    "default_pwritx_runtime_strategy",
    "pwritx_runtime_strategy_boundary",
    "require_pwritx_runtime_strategy",
    "validate_source_mapped_pwritx_runtime_strategy",
]
