from __future__ import annotations

from dataclasses import dataclass

from ._ncl_plotchar_real_library import (
    build_validated_ncl_plotchar_ctypes_backend,
    configured_ncl_plotchar_library_status_report,
    explicit_ncl_plotchar_library_paths,
    validate_configured_ncl_plotchar_library,
)
from ._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider
from ._plotchar_metrics import PlotcharExtentMetrics, PlotcharMetricsRequest
from ._text_bbox import MultiTextBBoxRequest, TextBBox, TextItemBBoxRequest
from ._text_bbox_plotchar_provider import compute_text_item_bbox_from_plotchar_provider
from ._multitext_bbox_plotchar_provider import compute_multitext_bbox_from_plotchar_provider


@dataclass(frozen=True)
class NclPlotcharLiveEngineStatus:
    requested: bool
    available: bool
    report: str


def configured_ncl_plotchar_backend_is_requested() -> bool:
    return bool(explicit_ncl_plotchar_library_paths())


def has_configured_ncl_plotchar_live_engine() -> bool:
    return validate_configured_ncl_plotchar_library().ok


def ncl_plotchar_live_engine_status() -> NclPlotcharLiveEngineStatus:
    validation = validate_configured_ncl_plotchar_library()
    return NclPlotcharLiveEngineStatus(
        requested=bool(validation.requested_paths),
        available=validation.ok,
        report=configured_ncl_plotchar_library_status_report(),
    )


def build_configured_ncl_plotchar_metrics_provider():
    backend = build_validated_ncl_plotchar_ctypes_backend()
    return build_ncl_plotchar_metrics_provider(backend=backend)


def compute_plotchar_extent_metrics_with_configured_backend(
    request: PlotcharMetricsRequest,
) -> PlotcharExtentMetrics:
    provider = build_configured_ncl_plotchar_metrics_provider()
    return provider.metrics_for_request(request)


def compute_text_item_bbox_with_configured_backend(
    request: TextItemBBoxRequest,
) -> TextBBox:
    provider = build_configured_ncl_plotchar_metrics_provider()
    result = compute_text_item_bbox_from_plotchar_provider(request, provider)
    return result.bbox


def compute_multitext_bbox_with_configured_backend(
    request: MultiTextBBoxRequest,
) -> TextBBox:
    provider = build_configured_ncl_plotchar_metrics_provider()
    result = compute_multitext_bbox_from_plotchar_provider(request, provider)
    return result.bbox


__all__ = [
    "NclPlotcharLiveEngineStatus",
    "build_configured_ncl_plotchar_metrics_provider",
    "compute_multitext_bbox_with_configured_backend",
    "compute_plotchar_extent_metrics_with_configured_backend",
    "compute_text_item_bbox_with_configured_backend",
    "configured_ncl_plotchar_backend_is_requested",
    "has_configured_ncl_plotchar_live_engine",
    "ncl_plotchar_live_engine_status",
]
