from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SMOKE_SCRIPTS = [
    "tools/check_no_matplotlib.py",
    "tools/check_no_external_render_deps.py",
    "tools/smoke_plotchar_python_state.py",
    "tools/smoke_python_plotchar_pcgtdi_decimal_parser.py",
    "tools/smoke_python_plotchar_quality_pwrity_guard.py",
    "tools/smoke_python_plotchar_measurement_contract_guard.py",
    "tools/smoke_python_plotchar_no_stale_guards.py",
    "tools/smoke_python_plotchar_unsupported_command_matrix.py",
    "tools/smoke_ncl_plotchar_function_code_coverage.py",
    "tools/smoke_ncl_plotchar_guarded_command_windows.py",
    "tools/smoke_ncl_plotchar_next_implementation_candidates.py",
    "tools/smoke_ncl_plotchar_focused_guarded_command.py",
    "tools/smoke_ncl_plotchar_g_command_source_map.py",
    "tools/smoke_ncl_plotchar_r_size_branch_source_map.py",
    "tools/smoke_python_plotchar_function_code_guard.py",
    "tools/smoke_python_plotchar_function_code_literal_escape.py",
    "tools/smoke_python_plotchar_function_code_font_change.py",
    "tools/smoke_python_plotchar_function_code_size_level.py",
    "tools/smoke_python_plotchar_function_code_script.py",
    "tools/smoke_python_plotchar_function_code_down_text.py",
    "tools/smoke_python_plotchar_function_code_hv_movement.py",
    "tools/smoke_python_plotchar_function_code_zoom.py",
    "tools/smoke_python_plotchar_function_code_carriage_return.py",
    "tools/smoke_python_plotchar_function_code_case.py",
    "tools/smoke_python_plotchar_fontcap_plchhq_extent.py",
    "tools/smoke_python_plotchar_pcgetr_geometry_state.py",
    "tools/smoke_python_plotchar_default_engine_integration.py",
    "tools/smoke_python_mainline_renderer_labelbar_adjust.py",
    "tools/smoke_text_bbox_from_plotchar_provider.py",
    "tools/smoke_multitext_bbox_from_plotchar_provider.py",
    "tools/smoke_labelbar_adjust_from_plotchar_provider_bboxes.py",
    "tools/smoke_ncl_plotchar_metrics_source_map.py",
    "tools/smoke_ncl_plotchar_remaining_branch_source_map.py",
    "tools/smoke_ncl_plotchar_mapped_coordinate_branch.py",
    "tools/smoke_ncl_plotchar_mapped_branch_labels.py",
    "tools/smoke_ncl_plotchar_mapped_label_resolution.py",
    "tools/smoke_ncl_plotchar_mapped_branch_readiness.py",
    "tools/smoke_ncl_plotchar_extent_alias_source_map.py",
    "tools/smoke_ncl_plotchar_mapped_exact_branch.py",
    "tools/smoke_python_plotchar_mapped_coordinate_boundary.py",
    "tools/smoke_python_plotchar_mapped_coordinate_guard_adapter.py",
    "tools/smoke_python_plotchar_mapped_coordinate_dispatch_seam.py",
    "tools/smoke_python_plotchar_mapped_coordinate_runtime_api.py",
    "tools/smoke_python_plotchar_mapped_coordinate_transform_provider.py",
    "tools/smoke_python_plotchar_mapped_coordinate_provider_injection.py",
    "tools/smoke_python_plotchar_mapped_coordinate_source_mapped_provider_contract.py",
    "tools/smoke_python_plotchar_mapped_coordinate_runtime_strategy_injection.py",
    "tools/smoke_python_plotchar_mapped_coordinate_provider_backed_strategy_guard.py",
    "tools/smoke_ncl_plotchar_coordinate_transform_source_map.py",
    "tools/smoke_ncl_coordinate_transform_function_definitions.py",
    "tools/smoke_ncl_coordinate_transform_direction_readiness.py",
    "tools/smoke_python_plotchar_mapped_coordinate_with_ncl_linear_provider.py",
    "tools/smoke_ncl_plotchar_mapped_opt_in_backend_status.py",
    "tools/smoke_python_plotchar_mapped_default_still_guarded.py",
    "tools/smoke_python_plotchar_mapped_opt_in_backend.py",
    "tools/smoke_python_plotchar_mapped_backend_status.py",
    "tools/smoke_python_plotchar_stage_status.py",
    "tools/smoke_python_plotchar_completion_roadmap.py",
    "tools/smoke_python_plotchar_final_stage_closure.py",
    "tools/smoke_python_plotchar_stage_docs_after_pwritx.py",
    "tools/smoke_python_plotchar_function_code_remaining_roadmap.py",
    "tools/smoke_python_plotchar_milestone_manifest.py",
    "tools/smoke_python_plotchar_milestone_lock.py",
    "tools/smoke_python_plotchar_stage_docs_after_function_code_roadmap.py",
    "tools/smoke_python_plotchar_pwritx_nonfontcap_boundary.py",
    "tools/smoke_python_plotchar_pwritx_runtime_strategy_injection.py",
    "tools/smoke_python_plotchar_pwritx_provider_backed_strategy_guard.py",
    "tools/smoke_python_plotchar_pwritx_provider_backend_status.py",
    "tools/smoke_python_plotchar_pwritx_public_facade.py",
    "tools/smoke_python_plotchar_pwritx_provider_backed_strategy.py",
    "tools/smoke_python_plotchar_pwritx_provider_contract.py",
    "tools/smoke_ncl_plotchar_pwritx_formula_audit.py",
    "tools/smoke_python_plotchar_pwritx_runtime_strategy.py",
    "tools/smoke_ncl_plotchar_pwritx_nonfontcap_exact_branch.py",
    "tools/smoke_python_plotchar_mapped_opt_in_example.py",
    "tools/smoke_python_plotchar_mapped_public_facade.py",
    "tools/smoke_python_plotchar_ncl_linear_window_viewport_transform.py",
    "tools/smoke_ncl_coordinate_transform_formula_audit.py",
    "tools/smoke_python_plotchar_ncl_mapped_transform_boundary.py",
    "tools/smoke_python_plotchar_mapped_coordinate_provider_backed_strategy.py",
    "tools/smoke_python_plotchar_mapped_coordinate_runtime_strategy.py",
    "tools/smoke_python_plotchar_mapped_coordinate_runtime_handoff.py",
    "tools/smoke_python_plotchar_mapped_coordinate_result_bridge.py",
    "tools/smoke_ncl_plotchar_pwritx_nonfontcap_branch.py",
    "tools/smoke_ncl_plotchar_size_address_unit_branch.py",
    "tools/smoke_python_plotchar_size_address_unit_boundary.py",
    "tools/smoke_python_plotchar_size_address_result_bridge.py",
    "tools/smoke_python_plotchar_size_address_runtime_strategy_injection.py",
    "tools/smoke_python_plotchar_size_address_provider_backed_strategy_guard.py",
    "tools/smoke_python_plotchar_size_address_provider_backend_status.py",
    "tools/smoke_python_plotchar_size_address_public_facade.py",
    "tools/smoke_python_plotchar_size_address_provider_backed_strategy.py",
    "tools/smoke_python_plotchar_size_address_provider_contract.py",
    "tools/smoke_ncl_plotchar_size_address_formula_audit.py",
    "tools/smoke_python_plotchar_size_address_runtime_strategy.py",
    "tools/smoke_python_plotchar_size_address_runtime_handoff.py",
    "tools/smoke_ncl_plotchar_size_address_exact_branch.py",
    "tools/smoke_python_mainline_project_boundary.py",
]


def run(script: str) -> None:
    path = ROOT / script

    if not path.exists():
        print(f"SKIP missing smoke: {script}", flush=True)
        return

    print(f"RUN {script}", flush=True)
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


def main() -> None:
    for script in SMOKE_SCRIPTS:
        run(script)

    print("✅ Python mainline smoke suite passed")


if __name__ == "__main__":
    main()
