from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_pwritx_nonfontcap import (
    PwritxNonFontcapResult,
    raise_pwritx_nonfontcap_guard,
)
from ._plotchar_state import PlotcharUnsupportedError


PWRITX_PROVIDER_DOCS = (
    "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md",
    "docs/ncl_plotchar_pwritx_formula_audit.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
)


@dataclass(frozen=True)
class PwritxMetricsProviderBoundary:
    implemented: bool
    reason: str
    required_docs: tuple[str, ...]


def pwritx_metrics_provider_boundary() -> PwritxMetricsProviderBoundary:
    return PwritxMetricsProviderBoundary(
        implemented=False,
        reason=(
            "PWRITX/font0 metrics-provider boundary is available, but no default NCL "
            "PWRITX/font0 provider is implemented. This branch requires explicit source-mapped provider injection."
        ),
        required_docs=PWRITX_PROVIDER_DOCS,
    )


class PwritxMetricsProvider:
    source_mapped = False
    source_map_reference = ""

    def metrics_for_request(self, request) -> PwritxNonFontcapResult:
        raise_pwritx_nonfontcap_guard()


class GuardedPwritxMetricsProvider(PwritxMetricsProvider):
    pass


def default_pwritx_metrics_provider() -> PwritxMetricsProvider:
    return GuardedPwritxMetricsProvider()


def require_pwritx_metrics_provider(provider: PwritxMetricsProvider | None) -> PwritxMetricsProvider:
    if provider is None:
        raise PlotcharUnsupportedError(
            "PWRITX/font0 metrics provider is missing. PWRITX/font0 remains guarded."
        )
    return provider


def validate_source_mapped_pwritx_metrics_provider(provider: PwritxMetricsProvider) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "PWRITX/font0 metrics provider is not source-mapped. "
            "Do not use substitute text metrics for this branch."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "PWRITX/font0 metrics provider must declare source_map_reference."
        )


__all__ = [
    "GuardedPwritxMetricsProvider",
    "PWRITX_PROVIDER_DOCS",
    "PwritxMetricsProvider",
    "PwritxMetricsProviderBoundary",
    "default_pwritx_metrics_provider",
    "pwritx_metrics_provider_boundary",
    "require_pwritx_metrics_provider",
    "validate_source_mapped_pwritx_metrics_provider",
]
