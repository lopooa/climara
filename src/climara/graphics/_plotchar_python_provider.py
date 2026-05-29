from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._ncl_plotchar_textitem import build_ncl_plotchar_textitem_measurement_call
from ._plotchar_metrics import PlotcharExtentMetrics, PlotcharMetricsRequest
from ._plotchar_plchhq_extent import compute_textitem_call_fontcap_metrics


@dataclass(frozen=True)
class PythonPlotcharFontcapMetricsProvider:
    fontcap_dir: str | Path | None = None

    def metrics_for_request(self, request: PlotcharMetricsRequest) -> PlotcharExtentMetrics:
        call = build_ncl_plotchar_textitem_measurement_call(request)
        return compute_textitem_call_fontcap_metrics(call, fontcap_dir=self.fontcap_dir)


def build_python_plotchar_fontcap_metrics_provider(
    *,
    fontcap_dir: str | Path | None = None,
) -> PythonPlotcharFontcapMetricsProvider:
    return PythonPlotcharFontcapMetricsProvider(fontcap_dir=fontcap_dir)


__all__ = [
    "PythonPlotcharFontcapMetricsProvider",
    "build_python_plotchar_fontcap_metrics_provider",
]
