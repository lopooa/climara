from __future__ import annotations

from pathlib import Path
from typing import Any

from ._labelbar_adjust_pipeline import LabelBarSuppliedMetricsAdjustPipeline
from ._labelbar_geometry import LabelBarGeometry
from ._labelbar_plotchar_metrics import build_labelbar_plotchar_metrics_requests
from ._labelbar_plotchar_metrics_bundle import (
    LabelBarPlotcharMetricsBundle,
    build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle,
    build_labelbar_plotchar_metrics_bundle,
    compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle,
    render_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
    save_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
    validate_labelbar_plotchar_metrics_bundle,
)
from ._plotchar_metrics_provider import resolve_plotchar_metrics_from_provider


def build_labelbar_plotchar_metrics_bundle_from_provider(
    obj: Any,
    provider: Any,
) -> LabelBarPlotcharMetricsBundle:
    requests = build_labelbar_plotchar_metrics_requests(obj)

    if requests.title is None:
        title_metrics = None
    else:
        title_metrics = resolve_plotchar_metrics_from_provider(
            provider,
            requests.title,
        )

    label_metrics = tuple(
        resolve_plotchar_metrics_from_provider(provider, request)
        for request in requests.labels
    )

    bundle = build_labelbar_plotchar_metrics_bundle(
        title=title_metrics,
        labels=label_metrics,
    )

    return validate_labelbar_plotchar_metrics_bundle(obj, bundle)


def build_labelbar_adjust_pipeline_from_plotchar_metrics_provider(
    obj: Any,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarSuppliedMetricsAdjustPipeline:
    bundle = build_labelbar_plotchar_metrics_bundle_from_provider(
        obj,
        provider,
    )

    return build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(
        obj,
        bundle,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


def compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider(
    obj: Any,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarGeometry:
    bundle = build_labelbar_plotchar_metrics_bundle_from_provider(
        obj,
        provider,
    )

    return compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(
        obj,
        bundle,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


def render_adjusted_labelbar_svg_from_plotchar_metrics_provider(
    obj: Any,
    provider: Any,
    *,
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
    stroke: Any = "black",
    text_fill: Any | None = None,
    default_label_font_height: float = 0.012,
) -> str:
    bundle = build_labelbar_plotchar_metrics_bundle_from_provider(
        obj,
        provider,
    )

    return render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
        obj,
        bundle,
        width=width,
        height=height,
        background=background,
        stroke=stroke,
        text_fill=text_fill,
        default_label_font_height=default_label_font_height,
    )


def save_adjusted_labelbar_svg_from_plotchar_metrics_provider(
    obj: Any,
    provider: Any,
    path: str | Path,
    *,
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
    stroke: Any = "black",
    text_fill: Any | None = None,
    default_label_font_height: float = 0.012,
) -> Path:
    bundle = build_labelbar_plotchar_metrics_bundle_from_provider(
        obj,
        provider,
    )

    return save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
        obj,
        bundle,
        path,
        width=width,
        height=height,
        background=background,
        stroke=stroke,
        text_fill=text_fill,
        default_label_font_height=default_label_font_height,
    )


__all__ = [
    "build_labelbar_adjust_pipeline_from_plotchar_metrics_provider",
    "build_labelbar_plotchar_metrics_bundle_from_provider",
    "compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider",
    "render_adjusted_labelbar_svg_from_plotchar_metrics_provider",
    "save_adjusted_labelbar_svg_from_plotchar_metrics_provider",
]
