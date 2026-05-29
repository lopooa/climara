from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._labelbar_adjust import (
    LabelBarAdjustGeometryRequest,
    LabelBarAdjustGeometryResult,
    adjust_labelbar_geometry_for_text,
    build_labelbar_adjust_geometry_request,
)
from ._labelbar_adjust_apply import apply_labelbar_adjusted_geometry
from ._labelbar_adjust_materialize import (
    LabelBarAdjustedGeometry,
    materialize_labelbar_adjusted_geometry,
)
from ._labelbar_bbox_plotchar_provider import (
    compute_labelbar_text_bbox_from_plotchar_provider,
)
from ._labelbar_bbox_semantics import LabelBarTextBBoxSemantics
from ._labelbar_geometry import LabelBarGeometry
from ._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider


@dataclass(frozen=True)
class LabelBarPlotcharProviderAdjustRequest:
    text_bboxes: LabelBarTextBBoxSemantics
    adjust_request: LabelBarAdjustGeometryRequest


@dataclass(frozen=True)
class LabelBarPlotcharProviderAdjustPipeline:
    source_object: Any
    provider_adjust_request: LabelBarPlotcharProviderAdjustRequest
    adjust_result: LabelBarAdjustGeometryResult
    materialized: LabelBarAdjustedGeometry
    geometry: LabelBarGeometry


def _resources(obj: Any) -> dict[str, Any]:
    values = getattr(obj, "resources", None)
    if isinstance(values, dict):
        return values
    return {}


def build_labelbar_adjust_request_from_plotchar_provider_bboxes(
    obj: Any,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarPlotcharProviderAdjustRequest:
    """Build a LabelBar AdjustGeometry request from explicit provider bboxes.

    This path intentionally computes LabelBar title and label bboxes through the
    explicit TextItem/MultiText Plotchar-provider bridges before calling the
    supplied-bbox AdjustGeometry execution path. It does not change default
    renderer behavior and does not enable a global LabelBar/TextItem engine.
    """
    if not hasattr(obj, "compute_geometry"):
        raise TypeError("Expected a LabelBar-like object with compute_geometry()")

    geometry = obj.compute_geometry()
    text_bboxes = compute_labelbar_text_bbox_from_plotchar_provider(
        obj,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )

    title_bbox = None if text_bboxes.title is None else text_bboxes.title.bbox
    label_bbox = None if text_bboxes.labels is None else text_bboxes.labels.bbox
    resources = _resources(obj)

    return LabelBarPlotcharProviderAdjustRequest(
        text_bboxes=text_bboxes,
        adjust_request=build_labelbar_adjust_geometry_request(
            geometry,
            title_bbox=title_bbox,
            label_bbox=label_bbox,
            justification=resources.get("lbJustification", "CenterCenter"),
        ),
    )


def build_labelbar_adjust_pipeline_from_plotchar_provider_bboxes(
    obj: Any,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarPlotcharProviderAdjustPipeline:
    request = build_labelbar_adjust_request_from_plotchar_provider_bboxes(
        obj,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )
    result = adjust_labelbar_geometry_for_text(request.adjust_request)
    materialized = materialize_labelbar_adjusted_geometry(result)
    geometry = apply_labelbar_adjusted_geometry(materialized)

    return LabelBarPlotcharProviderAdjustPipeline(
        source_object=obj,
        provider_adjust_request=request,
        adjust_result=result,
        materialized=materialized,
        geometry=geometry,
    )


def compute_labelbar_adjusted_geometry_from_plotchar_provider_bboxes(
    obj: Any,
    provider: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarGeometry:
    return build_labelbar_adjust_pipeline_from_plotchar_provider_bboxes(
        obj,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    ).geometry


def build_labelbar_adjust_pipeline_from_ncl_plotchar_backend_bboxes(
    obj: Any,
    backend: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarPlotcharProviderAdjustPipeline:
    provider = build_ncl_plotchar_metrics_provider(backend=backend)
    return build_labelbar_adjust_pipeline_from_plotchar_provider_bboxes(
        obj,
        provider,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    )


def compute_labelbar_adjusted_geometry_from_ncl_plotchar_backend_bboxes(
    obj: Any,
    backend: Any,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> LabelBarGeometry:
    return build_labelbar_adjust_pipeline_from_ncl_plotchar_backend_bboxes(
        obj,
        backend,
        perim_on=perim_on,
        background_fill_on=background_fill_on,
        perim_space=perim_space,
    ).geometry


__all__ = [
    "LabelBarPlotcharProviderAdjustPipeline",
    "LabelBarPlotcharProviderAdjustRequest",
    "build_labelbar_adjust_pipeline_from_ncl_plotchar_backend_bboxes",
    "build_labelbar_adjust_pipeline_from_plotchar_provider_bboxes",
    "build_labelbar_adjust_request_from_plotchar_provider_bboxes",
    "compute_labelbar_adjusted_geometry_from_ncl_plotchar_backend_bboxes",
    "compute_labelbar_adjusted_geometry_from_plotchar_provider_bboxes",
]
