from __future__ import annotations

from dataclasses import dataclass

from ._labelbar_adjust import has_labelbar_adjust_geometry_engine
from ._plotchar_metrics import has_plotchar_metrics_engine
from ._text_bbox import has_text_bbox_engine


@dataclass(frozen=True)
class GraphicsCapabilities:
    no_mpl_runtime: bool
    no_cartopy_runtime: bool
    svg_backend: bool

    text_item_semantics: bool
    multitext_semantics: bool

    text_bbox_requests: bool
    labelbar_text_bbox_requests: bool
    plotchar_metrics_requests: bool
    labelbar_plotchar_metrics_requests: bool

    text_bbox_from_supplied_plotchar_metrics: bool
    multitext_bbox_from_supplied_plotchar_metrics: bool
    labelbar_bbox_from_supplied_plotchar_metrics: bool

    labelbar_adjust_request_from_supplied_bboxes: bool
    labelbar_adjust_box_semantics_from_supplied_bboxes: bool
    labelbar_adjust_perimeter_semantics_from_supplied_bboxes: bool
    labelbar_adjust_writeback_semantics_from_supplied_bboxes: bool
    labelbar_adjust_execution_from_supplied_bboxes: bool
    labelbar_adjust_materialization_from_supplied_bboxes: bool
    labelbar_adjust_apply_geometry_from_supplied_bboxes: bool
    labelbar_adjust_pipeline_from_supplied_metrics: bool

    explicit_adjusted_labelbar_svg_adapter: bool
    explicit_adjusted_labelbar_svg_export: bool

    text_bbox_engine: bool
    plotchar_metrics_engine: bool
    labelbar_adjust_geometry_engine: bool

    plotchar_parser: bool
    down_text_rendering: bool
    default_renderer_uses_adjusted_labelbar: bool


def graphics_capabilities() -> GraphicsCapabilities:
    return GraphicsCapabilities(
        no_mpl_runtime=True,
        no_cartopy_runtime=True,
        svg_backend=True,

        text_item_semantics=True,
        multitext_semantics=True,

        text_bbox_requests=True,
        labelbar_text_bbox_requests=True,
        plotchar_metrics_requests=True,
        labelbar_plotchar_metrics_requests=True,

        text_bbox_from_supplied_plotchar_metrics=True,
        multitext_bbox_from_supplied_plotchar_metrics=True,
        labelbar_bbox_from_supplied_plotchar_metrics=True,

        labelbar_adjust_request_from_supplied_bboxes=True,
        labelbar_adjust_box_semantics_from_supplied_bboxes=True,
        labelbar_adjust_perimeter_semantics_from_supplied_bboxes=True,
        labelbar_adjust_writeback_semantics_from_supplied_bboxes=True,
        labelbar_adjust_execution_from_supplied_bboxes=True,
        labelbar_adjust_materialization_from_supplied_bboxes=True,
        labelbar_adjust_apply_geometry_from_supplied_bboxes=True,
        labelbar_adjust_pipeline_from_supplied_metrics=True,

        explicit_adjusted_labelbar_svg_adapter=True,
        explicit_adjusted_labelbar_svg_export=True,

        text_bbox_engine=has_text_bbox_engine(),
        plotchar_metrics_engine=has_plotchar_metrics_engine(),
        labelbar_adjust_geometry_engine=has_labelbar_adjust_geometry_engine(),

        plotchar_parser=False,
        down_text_rendering=False,
        default_renderer_uses_adjusted_labelbar=False,
    )


__all__ = [
    "GraphicsCapabilities",
    "graphics_capabilities",
]
