from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ._labelbar_adjust import (
    LabelBarAdjustGeometryResult,
    adjust_labelbar_geometry_for_text,
)
from ._labelbar_adjust_apply import apply_labelbar_adjusted_geometry
from ._labelbar_adjust_bridge import (
    LabelBarSuppliedMetricsAdjustRequest,
    build_labelbar_adjust_request_from_supplied_plotchar_metrics,
)
from ._labelbar_adjust_materialize import (
    LabelBarAdjustedGeometry,
    materialize_labelbar_adjusted_geometry,
)
from ._labelbar_geometry import LabelBarGeometry
from ._plotchar_metrics import PlotcharExtentMetrics


@dataclass(frozen=True)
class LabelBarSuppliedMetricsAdjustPipeline:
    source_object: Any
    supplied_metrics_request: LabelBarSuppliedMetricsAdjustRequest
    adjust_result: LabelBarAdjustGeometryResult
    materialized: LabelBarAdjustedGeometry
    geometry: LabelBarGeometry


def build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics(
    obj: Any,
    *,
    title_metrics: PlotcharExtentMetrics | None = None,
    label_metrics: Iterable[PlotcharExtentMetrics] = (),
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarSuppliedMetricsAdjustPipeline:
    supplied = build_labelbar_adjust_request_from_supplied_plotchar_metrics(
        obj,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )

    result = adjust_labelbar_geometry_for_text(supplied.adjust_request)
    materialized = materialize_labelbar_adjusted_geometry(result)
    geometry = apply_labelbar_adjusted_geometry(materialized)

    return LabelBarSuppliedMetricsAdjustPipeline(
        source_object=obj,
        supplied_metrics_request=supplied,
        adjust_result=result,
        materialized=materialized,
        geometry=geometry,
    )


def compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics(
    obj: Any,
    *,
    title_metrics: PlotcharExtentMetrics | None = None,
    label_metrics: Iterable[PlotcharExtentMetrics] = (),
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarGeometry:
    return build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics(
        obj,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    ).geometry


__all__ = [
    "LabelBarSuppliedMetricsAdjustPipeline",
    "build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics",
    "compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics",
]
