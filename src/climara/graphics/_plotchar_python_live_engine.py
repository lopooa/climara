from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._plotchar_fontcap import candidate_fontcap_dirs, resolve_fontcap_path
from ._plotchar_metrics import (
    PlotcharExtentMetrics,
    PlotcharMetricsNotImplementedError,
    PlotcharMetricsRequest,
)
from ._plotchar_python_provider import build_python_plotchar_fontcap_metrics_provider
from ._plotchar_state import PlotcharStateError, PlotcharUnsupportedError
from ._text_bbox import (
    MultiTextBBoxRequest,
    TextBBox,
    TextBBoxNotImplementedError,
    TextItemBBoxRequest,
    aggregate_multitext_child_bboxes,
)
from ._text_bbox_plotchar_provider import compute_text_item_bbox_from_plotchar_provider


class PythonPlotcharMainlineNotAvailableError(PlotcharMetricsNotImplementedError):
    pass


@dataclass(frozen=True)
class PythonPlotcharMainlineStatus:
    available: bool
    report: str
    fontcap_dir: Path | None = None
    reference_fontcap: Path | None = None


def python_plotchar_mainline_status() -> PythonPlotcharMainlineStatus:
    try:
        reference = resolve_fontcap_path(1)
    except Exception as exc:  # noqa: BLE001 - report the exact guarded availability reason.
        searched = "\n".join(f"- {path}" for path in candidate_fontcap_dirs())
        return PythonPlotcharMainlineStatus(
            available=False,
            report=(
                "Python Plotchar fontcap mainline is unavailable because no NCL fontcap "
                "source data could be resolved. Set CLIMARA_PLOTCHAR_FONTCAP_DIR or "
                "NCL_SRC_ROOT. No fixed-width, SVG, browser, or character-count fallback "
                f"is allowed. Original error: {exc}. Searched:\n{searched}"
            ),
        )

    return PythonPlotcharMainlineStatus(
        available=True,
        report=(
            "Python Plotchar fontcap mainline is available for the audited source-mapped "
            "subset: TextItem.c measurement calls, high-quality fontcap glyphs, Across "
            "text, printable ASCII, IMAP=0, SIZE in (0, 1), and no inline function-code "
            "body commands. Unsupported PLCHHQ branches remain guarded."
        ),
        fontcap_dir=reference.parent,
        reference_fontcap=reference,
    )


def has_python_plotchar_mainline_engine() -> bool:
    return python_plotchar_mainline_status().available


def build_python_plotchar_mainline_metrics_provider():
    status = python_plotchar_mainline_status()
    if not status.available:
        raise PythonPlotcharMainlineNotAvailableError(status.report)

    return build_python_plotchar_fontcap_metrics_provider(fontcap_dir=status.fontcap_dir)


def compute_plotchar_extent_metrics_with_python_mainline(
    request: PlotcharMetricsRequest,
) -> PlotcharExtentMetrics:
    provider = build_python_plotchar_mainline_metrics_provider()
    return provider.metrics_for_request(request)


def compute_text_item_bbox_with_python_mainline(
    request: TextItemBBoxRequest,
) -> TextBBox:
    try:
        provider = build_python_plotchar_mainline_metrics_provider()
    except PythonPlotcharMainlineNotAvailableError as exc:
        raise TextBBoxNotImplementedError(str(exc)) from exc

    result = compute_text_item_bbox_from_plotchar_provider(request, provider)
    return result.bbox


def compute_multitext_bbox_with_python_mainline(
    request: MultiTextBBoxRequest,
) -> TextBBox:
    try:
        children = tuple(
            compute_text_item_bbox_with_python_mainline(item)
            for item in request.items
        )
    except PythonPlotcharMainlineNotAvailableError as exc:
        raise TextBBoxNotImplementedError(str(exc)) from exc

    return aggregate_multitext_child_bboxes(request, children)


__all__ = [
    "PythonPlotcharMainlineNotAvailableError",
    "PythonPlotcharMainlineStatus",
    "build_python_plotchar_mainline_metrics_provider",
    "compute_multitext_bbox_with_python_mainline",
    "compute_plotchar_extent_metrics_with_python_mainline",
    "compute_text_item_bbox_with_python_mainline",
    "has_python_plotchar_mainline_engine",
    "python_plotchar_mainline_status",
]
