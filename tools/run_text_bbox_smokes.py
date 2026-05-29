import subprocess
import sys
from pathlib import Path


SMOKES = [
    "tools/smoke_python_plotchar_default_engine_integration.py",
    "tools/smoke_text_bbox_guard.py",
    "tools/smoke_ncl_text_bbox_source_map_doc.py",
    "tools/smoke_ncl_source_requirements.py",
    "tools/smoke_text_bbox_dependency_gate.py",
    "tools/smoke_text_bbox_implementation_preflight.py",
    "tools/smoke_ncl_source_availability_report.py",
    "tools/smoke_no_text_bbox_heuristics.py",
    "tools/smoke_plotchar_metrics_guard.py",
    "tools/smoke_text_bbox_plotchar_bridge.py",
    "tools/smoke_text_bbox_semantics_from_plotchar_metrics.py",
    "tools/smoke_text_bbox_semantics_boundary.py",
    "tools/smoke_plotchar_metrics_not_used_by_render_path.py",
    "tools/smoke_labelbar_plotchar_metrics_request_builder.py",
    "tools/smoke_text_bbox_pipeline_report.py",
    "tools/smoke_labelbar_plotchar_metrics_builder_not_used.py",
    "tools/smoke_text_bbox_not_used_by_render_path.py",
    "tools/smoke_text_bbox_coordinate_space_contract.py",
    "tools/smoke_text_bbox_union_contract.py",
    "tools/smoke_multitext_bbox_request_builder.py",
    "tools/smoke_multitext_child_bbox_aggregation.py",
    "tools/smoke_multitext_bbox_semantics_from_plotchar_metrics.py",
    "tools/smoke_multitext_bbox_semantics_boundary.py",
    "tools/smoke_labelbar_text_bbox_request_contract.py",
    "tools/smoke_labelbar_text_bbox_request_builder.py",
    "tools/smoke_labelbar_bbox_semantics_from_plotchar_metrics.py",
    "tools/smoke_labelbar_bbox_semantics_boundary.py",
    "tools/smoke_labelbar_adjust_bridge_from_supplied_metrics.py",
    "tools/smoke_labelbar_adjust_box_semantics.py",
    "tools/smoke_labelbar_adjust_box_semantics_boundary.py",
    "tools/smoke_labelbar_adjust_perim_semantics.py",
    "tools/smoke_labelbar_adjust_writeback_semantics.py",
    "tools/smoke_labelbar_adjust_writeback_semantics_not_used.py",
    "tools/smoke_labelbar_adjust_perim_semantics_not_used.py",
    "tools/smoke_labelbar_adjust_box_semantics_not_used.py",
    "tools/smoke_labelbar_adjust_bridge_not_used.py",
    "tools/smoke_labelbar_bbox_semantics_not_used.py",
    "tools/smoke_labelbar_text_bbox_builder_not_used.py",
    "tools/smoke_labelbar_adjust_geometry_execution.py",
    "tools/smoke_labelbar_adjust_materialize.py",
    "tools/smoke_labelbar_adjust_apply_geometry.py",
    "tools/smoke_labelbar_adjust_pipeline.py",
    "tools/smoke_labelbar_adjusted_svg_adapter.py",
    "tools/smoke_labelbar_adjusted_svg_export.py",
    "tools/smoke_labelbar_plotchar_metrics_bundle.py",
    "tools/smoke_ncl_plotchar_metrics_source_map.py",
    "tools/smoke_ncl_plotchar_ctypes_backend_boundary.py",
    "tools/smoke_ncl_plotchar_real_library_validation.py",
    "tools/smoke_text_bbox_from_plotchar_provider.py",
    "tools/smoke_multitext_bbox_from_plotchar_provider.py",
    "tools/smoke_labelbar_adjust_from_plotchar_provider_bboxes.py",
    "tools/smoke_labelbar_plotchar_metrics_provider.py",
    "tools/smoke_hlu_labelbar_plotchar_metrics_provider_methods.py",
    "tools/smoke_labelbar_plotchar_metrics_provider_not_default.py",
    "tools/smoke_labelbar_adjusted_public_api.py",
    "tools/smoke_hlu_labelbar_adjusted_methods.py",
    "tools/smoke_hlu_labelbar_adjusted_methods_not_default.py",
    "tools/smoke_public_plotchar_metrics_api.py",
    "tools/smoke_example_adjusted_labelbar_supplied_metrics_svg.py",
    "tools/smoke_adjusted_labelbar_example_not_default.py",
    "tools/smoke_labelbar_adjusted_public_api_not_default.py",
    "tools/smoke_labelbar_plotchar_metrics_bundle_not_default.py",
    "tools/smoke_labelbar_adjusted_svg_export_not_default.py",
    "tools/smoke_labelbar_adjusted_svg_adapter_not_default_render.py",
    "tools/smoke_labelbar_adjust_pipeline_not_used.py",
    "tools/smoke_labelbar_adjust_apply_not_used.py",
    "tools/smoke_labelbar_adjust_materialize_not_used.py",
    "tools/smoke_labelbar_adjust_geometry_guard.py",
    "tools/smoke_labelbar_adjust_geometry_not_used.py",
]


def main():
    root = Path.cwd()
    failures = []

    for smoke in SMOKES:
        path = root / smoke
        if not path.exists():
            print(f"SKIP missing {smoke}", flush=True)
            continue

        print(f"RUN {smoke}", flush=True)
        result = subprocess.run(
            [sys.executable, smoke],
            cwd=root,
            text=True,
        )

        if result.returncode != 0:
            failures.append(smoke)
            print(f"FAIL {smoke}", flush=True)
        else:
            print(f"PASS {smoke}", flush=True)

    if failures:
        print()
        print("Failed TextBBox / LabelBar AdjustGeometry smokes:")
        for smoke in failures:
            print(f"  - {smoke}")
        raise SystemExit(1)

    print("✅ TextBBox / LabelBar AdjustGeometry smoke bundle passed")


if __name__ == "__main__":
    main()
# tools/smoke_default_live_text_bbox_engine_gate.py
# tools/smoke_default_live_text_bbox_engine_invalid_config.py
tools/smoke_default_renderer_labelbar_live_adjust_gate.py

# Python mainline renderer smoke: tools/smoke_python_mainline_renderer_labelbar_adjust.py
