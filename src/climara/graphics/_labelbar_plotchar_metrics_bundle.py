from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ._labelbar_adjust_pipeline import (
    LabelBarSuppliedMetricsAdjustPipeline,
    build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics,
    compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics,
)
from ._labelbar_adjusted_svg_export import (
    render_adjusted_labelbar_svg_from_supplied_plotchar_metrics,
    save_adjusted_labelbar_svg_from_supplied_plotchar_metrics,
)
from ._labelbar_geometry import LabelBarGeometry
from ._labelbar_text_bbox import build_labelbar_text_bbox_requests
from ._plotchar_metrics import PlotcharExtentMetrics


@dataclass(frozen=True)
class LabelBarPlotcharMetricsBundle:
    title: PlotcharExtentMetrics | None
    labels: tuple[PlotcharExtentMetrics, ...]


def build_labelbar_plotchar_metrics_bundle(
    *,
    title: PlotcharExtentMetrics | None = None,
    labels: Iterable[PlotcharExtentMetrics] = (),
) -> LabelBarPlotcharMetricsBundle:
    return LabelBarPlotcharMetricsBundle(
        title=title,
        labels=tuple(labels),
    )


def build_uniform_labelbar_plotchar_metrics_bundle(
    obj: Any,
    *,
    title: PlotcharExtentMetrics | None = None,
    label: PlotcharExtentMetrics,
) -> LabelBarPlotcharMetricsBundle:
    requests = build_labelbar_text_bbox_requests(obj)

    return LabelBarPlotcharMetricsBundle(
        title=title,
        labels=tuple(label for _ in requests.labels.items),
    )


def validate_labelbar_plotchar_metrics_bundle(
    obj: Any,
    bundle: LabelBarPlotcharMetricsBundle,
) -> LabelBarPlotcharMetricsBundle:
    requests = build_labelbar_text_bbox_requests(obj)

    if requests.title is None and bundle.title is not None:
        raise ValueError(
            "LabelBar Plotchar metrics bundle supplies title metrics, "
            "but this LabelBar has no title TextBBox request"
        )

    if requests.title is not None and bundle.title is None:
        raise ValueError(
            "LabelBar Plotchar metrics bundle is missing title metrics "
            "for an active LabelBar title TextBBox request"
        )

    if len(bundle.labels) != len(requests.labels.items):
        raise ValueError(
            "LabelBar Plotchar metrics bundle label count mismatch: "
            f"expected {len(requests.labels.items)}, got {len(bundle.labels)}"
        )

    return bundle


def build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(
    obj: Any,
    bundle: LabelBarPlotcharMetricsBundle,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarSuppliedMetricsAdjustPipeline:
    bundle = validate_labelbar_plotchar_metrics_bundle(obj, bundle)

    return build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics(
        obj,
        title_metrics=bundle.title,
        label_metrics=bundle.labels,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


def compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(
    obj: Any,
    bundle: LabelBarPlotcharMetricsBundle,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarGeometry:
    bundle = validate_labelbar_plotchar_metrics_bundle(obj, bundle)

    return compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics(
        obj,
        title_metrics=bundle.title,
        label_metrics=bundle.labels,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


def render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
    obj: Any,
    bundle: LabelBarPlotcharMetricsBundle,
    *,
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
    stroke: Any = "black",
    text_fill: Any | None = None,
    default_label_font_height: float = 0.012,
) -> str:
    bundle = validate_labelbar_plotchar_metrics_bundle(obj, bundle)

    return render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
        obj,
        title_metrics=bundle.title,
        label_metrics=bundle.labels,
        width=width,
        height=height,
        background=background,
        stroke=stroke,
        text_fill=text_fill,
        default_label_font_height=default_label_font_height,
    )


def save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
    obj: Any,
    bundle: LabelBarPlotcharMetricsBundle,
    path: str | Path,
    *,
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
    stroke: Any = "black",
    text_fill: Any | None = None,
    default_label_font_height: float = 0.012,
) -> Path:
    bundle = validate_labelbar_plotchar_metrics_bundle(obj, bundle)

    return save_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
        obj,
        path,
        title_metrics=bundle.title,
        label_metrics=bundle.labels,
        width=width,
        height=height,
        background=background,
        stroke=stroke,
        text_fill=text_fill,
        default_label_font_height=default_label_font_height,
    )


__all__ = [
    "LabelBarPlotcharMetricsBundle",
    "build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle",
    "build_labelbar_plotchar_metrics_bundle",
    "build_uniform_labelbar_plotchar_metrics_bundle",
    "compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle",
    "render_adjusted_labelbar_svg_from_plotchar_metrics_bundle",
    "save_adjusted_labelbar_svg_from_plotchar_metrics_bundle",
    "validate_labelbar_plotchar_metrics_bundle",
]
