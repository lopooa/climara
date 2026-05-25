from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ._plotchar_metrics import PlotcharExtentMetrics, PlotcharMetricsRequest


class PlotcharMetricsProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class StaticPlotcharMetricsProvider:
    by_real_string: Mapping[str, PlotcharExtentMetrics]
    default: PlotcharExtentMetrics | None = None

    def metrics_for_request(
        self,
        request: PlotcharMetricsRequest,
    ) -> PlotcharExtentMetrics:
        real_string = request.semantics.real_string

        if real_string in self.by_real_string:
            return self.by_real_string[real_string]

        if self.default is not None:
            return self.default

        raise PlotcharMetricsProviderError(
            "No Plotchar metrics available for TextItem real_string: "
            f"{real_string!r}"
        )


def build_static_plotchar_metrics_provider(
    *,
    by_real_string: Mapping[str, PlotcharExtentMetrics] | None = None,
    default: PlotcharExtentMetrics | None = None,
) -> StaticPlotcharMetricsProvider:
    return StaticPlotcharMetricsProvider(
        by_real_string={} if by_real_string is None else dict(by_real_string),
        default=default,
    )


def resolve_plotchar_metrics_from_provider(
    provider: Any,
    request: PlotcharMetricsRequest,
) -> PlotcharExtentMetrics:
    if hasattr(provider, "metrics_for_request"):
        metrics = provider.metrics_for_request(request)
    elif callable(provider):
        metrics = provider(request)
    else:
        raise TypeError(
            "Plotchar metrics provider must define metrics_for_request(request) "
            "or be callable"
        )

    if not isinstance(metrics, PlotcharExtentMetrics):
        raise TypeError(
            "Plotchar metrics provider must return PlotcharExtentMetrics"
        )

    return metrics


__all__ = [
    "PlotcharMetricsProviderError",
    "StaticPlotcharMetricsProvider",
    "build_static_plotchar_metrics_provider",
    "resolve_plotchar_metrics_from_provider",
]
