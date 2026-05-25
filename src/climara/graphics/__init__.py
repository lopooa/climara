"""
climara graphics public API.

The graphics package now exposes backend-neutral HLU/GSN-style objects and a
small SVG renderer.
"""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "._view": [
        "HluView",
        "HluBoundingBox",
    ],
    "._primitive": [
        "HluPrimitive",
        "HluPolyline",
        "HluPolygon",
        "HluMarker",
    ],
    "._text_item": [
        "HluTextItem",
    ],
    "._objects": [
        "HluObject",
        "HluPlot",
        "HluMapPlot",
        "HluContourPlot",
        "HluVectorPlot",
        "HluPanel",
        "ScalarField",
        "VectorField",
        "ContourPlot",
        "ContourMapPlot",
        "MapPlot",
        "PanelPlot",
        "as_resources",
    ],
    "._style": [
        "apply_style",
        "get_active_style",
        "get_default_style",
        "ncl_style",
        "reset_style",
        "set_style",
    ],
    "._colors": [
        "HluColorMap",
        "get_colormap",
        "make_discrete_colormap",
        "normalize_rgb",
        "read_rgb_colormap",
        "read_rgb_table",
        "resolve_colormap",
        "rgb_to_hex",
    ],
    "._workstation": [
        "NclWorkstation",
        "gsn_open_wks",
        "frame",
    ],
    "._polyline": [
        "gsn_add_polyline",
        "gsn_polyline_ndc",
    ],
    "._polygon": [
        "gsn_add_polygon",
        "gsn_polygon_ndc",
    ],
    "._polymarker": [
        "gsn_add_polymarker",
        "gsn_polymarker_ndc",
    ],
    "._ndc": [
        "gsn_create_text_ndc",
        "gsn_text_ndc",
    ],
    "._legend_ndc": [
        "gsn_panel_pattern_legend_ndc",
    ],
    "._labelbar_object": [
        "HluLabelBar",
        "build_hlu_labelbar",
        "create_hlu_labelbar",
    ],
    "._labelbar": [
        "add_labelbar",
        "build_labelbar",
        "create_labelbar",
        "draw_labelbar",
    ],
    "._contour": [
        "build_contour_plot",
        "contour",
        "contourf",
        "gsn_csm_contour",
        "gsn_csm_contour_map",
        "ncl_contourf",
        "pcolormesh",
    ],
    "._maps": [
        "build_map_plot",
        "create_map",
        "gsn_csm_map",
        "gsn_panel_maps",
        "map_plot",
        "ncl_panel_maps",
        "normalize_projection",
    ],
    "._panel": [
        "HluPanelItem",
        "HluPanelLayout",
        "build_panel",
        "compute_gsn_panel_layout",
        "compute_panel_rects",
        "draw_panel",
        "gsn_panel",
        "ncl_panel",
        "panel",
    ],
    "._hatching": [
        "HluPatternOverlay",
        "add_agreement_hatching",
        "add_hatching",
        "add_significance_hatching",
        "build_hatch_overlay",
    ],
    "._tickmark": [
        "HluTickMark",
        "add_tickmarks",
        "build_tickmark",
        "build_tickmarks",
    ],
    "._vector": [
        "build_vector_plot",
        "gsn_csm_vector",
        "gsn_csm_vector_map",
        "vector_plot",
    ],
    "._strings": [
        "add_plot_strings",
        "build_plot_strings",
        "create_plot_string",
        "gsn_center_string",
        "gsn_left_string",
        "gsn_right_string",
    ],
    "._labelbar_adjusted_svg_export": [
        "add_adjusted_labelbar_primitives_to_svg_document",
        "render_adjusted_labelbar_svg_from_supplied_plotchar_metrics",
        "save_adjusted_labelbar_svg_from_supplied_plotchar_metrics",
    ],
    "._labelbar_plotchar_metrics_bundle": [
        "LabelBarPlotcharMetricsBundle",
        "build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle",
        "build_labelbar_plotchar_metrics_bundle",
        "build_uniform_labelbar_plotchar_metrics_bundle",
        "compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle",
        "render_adjusted_labelbar_svg_from_plotchar_metrics_bundle",
        "save_adjusted_labelbar_svg_from_plotchar_metrics_bundle",
        "validate_labelbar_plotchar_metrics_bundle",
    ],
    "._plotchar_metrics": [
        "PlotcharExtentMetrics",
        "PlotcharMetricsRequest",
        "build_plotchar_extent_metrics",
        "build_plotchar_metrics_request",
        "has_plotchar_metrics_engine",
    ],
    "._labelbar_adjust": [
        "LabelBarAdjustGeometryRequest",
        "LabelBarAdjustGeometryResult",
        "adjust_labelbar_geometry_for_text",
        "build_labelbar_adjust_geometry_request",
        "has_labelbar_adjust_geometry_engine",
    ],
    "._render_svg": [
        "SvgDocument",
        "render_object",
        "render_svg",
        "save_svg",
    ],
}


_FAILED_IMPORTS: dict[str, str] = {}


def _load_public_api() -> list[str]:
    names: list[str] = []

    for module_name, export_names in _EXPORTS.items():
        try:
            module = import_module(module_name, __name__)
        except Exception as exc:
            _FAILED_IMPORTS[module_name] = repr(exc)
            continue

        for export_name in export_names:
            if hasattr(module, export_name):
                globals()[export_name] = getattr(module, export_name)
                names.append(export_name)

    return sorted(set(names))


__all__ = _load_public_api()
