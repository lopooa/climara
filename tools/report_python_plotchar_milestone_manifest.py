from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_milestone_manifest.md"

RUNTIME_MODULES = [
    "src/climara/graphics/_plotchar_state.py",
    "src/climara/graphics/_plotchar_fontcap.py",
    "src/climara/graphics/_plotchar_function_code.py",
    "src/climara/graphics/_plotchar_plchhq_extent.py",
    "src/climara/graphics/_plotchar_mapped_coordinate.py",
    "src/climara/graphics/_plotchar_mapped_runtime_strategy.py",
    "src/climara/graphics/_plotchar_mapped_transform_ncl.py",
    "src/climara/graphics/_plotchar_mapped_opt_in.py",
    "src/climara/graphics/mapped_plotchar.py",
    "src/climara/graphics/_plotchar_size_address_unit.py",
    "src/climara/graphics/_plotchar_size_runtime_strategy.py",
    "src/climara/graphics/_plotchar_size_address_provider.py",
    "src/climara/graphics/size_address_plotchar.py",
    "src/climara/graphics/_plotchar_pwritx_nonfontcap.py",
    "src/climara/graphics/_plotchar_pwritx_runtime_strategy.py",
    "src/climara/graphics/_plotchar_pwritx_provider.py",
    "src/climara/graphics/pwritx_plotchar.py",
]

STATUS_DOCS = [
    "docs/python_plotchar_stage_status.md",
    "docs/python_plotchar_final_stage_closure.md",
    "docs/python_plotchar_completion_roadmap.md",
    "docs/python_plotchar_milestone_manifest.md",
    "docs/python_plotchar_mapped_backend_status.md",
    "docs/python_plotchar_mapped_opt_in_backend_usage.md",
    "docs/python_plotchar_size_address_provider_backend_status.md",
    "docs/python_plotchar_pwritx_provider_backend_status.md",
    "docs/python_plotchar_function_code_remaining_roadmap.md",
]

SOURCE_DOCS = [
    "docs/ncl_plotchar_mapped_coordinate_branch_source_map.md",
    "docs/ncl_plotchar_mapped_exact_branch_packet.md",
    "docs/ncl_plotchar_coordinate_transform_source_map.md",
    "docs/ncl_coordinate_transform_function_definitions.md",
    "docs/ncl_coordinate_transform_direction_readiness.md",
    "docs/ncl_coordinate_transform_formula_audit.md",
    "docs/ncl_plotchar_size_address_unit_branch_source_map.md",
    "docs/ncl_plotchar_size_address_exact_branch_packet.md",
    "docs/ncl_plotchar_size_address_formula_audit.md",
    "docs/ncl_plotchar_pwritx_nonfontcap_branch_source_map.md",
    "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md",
    "docs/ncl_plotchar_pwritx_formula_audit.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
]

SMOKE_SCRIPTS = [
    "tools/smoke_python_plotchar_final_stage_closure.py",
    "tools/smoke_python_plotchar_stage_docs_after_pwritx.py",
    "tools/smoke_python_plotchar_function_code_remaining_roadmap.py",
    "tools/smoke_python_plotchar_mapped_public_facade.py",
    "tools/smoke_python_plotchar_mapped_opt_in_backend.py",
    "tools/smoke_python_plotchar_size_address_public_facade.py",
    "tools/smoke_python_plotchar_pwritx_public_facade.py",
    "tools/smoke_python_plotchar_measurement_contract_guard.py",
    "tools/smoke_python_mainline_project_boundary.py",
]


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def checklist(items: list[str]) -> list[str]:
    return [f"- [{'x' if exists(item) else ' '}] `{item}`" for item in items]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    all_items = RUNTIME_MODULES + STATUS_DOCS + SOURCE_DOCS + SMOKE_SCRIPTS
    missing = [item for item in all_items if not exists(item)]

    lines = []
    lines.append("# Python Plotchar Milestone Manifest")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This manifest records the current bounded Python Plotchar milestone artifacts.")
    lines.append("")
    lines.append("It is not a full NCL PLCHHQ parity claim.")
    lines.append("")
    lines.append("## Milestone scope")
    lines.append("")
    lines.append("- TextItem/fontcap mainline for the audited subset.")
    lines.append("- Explicit mapped-coordinate opt-in seam.")
    lines.append("- Explicit SIZE/address provider-backed seam.")
    lines.append("- Explicit PWRITX/font0/non-fontcap provider-backed seam.")
    lines.append("- Remaining function-code roadmap and guard policy.")
    lines.append("- No default enablement for unsupported complex branches.")
    lines.append("")
    lines.append("## Runtime modules")
    lines.append("")
    lines.extend(checklist(RUNTIME_MODULES))
    lines.append("")
    lines.append("## Status documents")
    lines.append("")
    lines.extend(checklist(STATUS_DOCS))
    lines.append("")
    lines.append("## Source-map documents")
    lines.append("")
    lines.extend(checklist(SOURCE_DOCS))
    lines.append("")
    lines.append("## Smoke scripts")
    lines.append("")
    lines.extend(checklist(SMOKE_SCRIPTS))
    lines.append("")
    lines.append("## Missing artifacts")
    lines.append("")
    if missing:
        for item in missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("No required milestone artifacts are missing.")
    lines.append("")
    lines.append("## Guard policy")
    lines.append("")
    lines.append("- Unsupported function-code commands remain guarded.")
    lines.append("- Default mapped-coordinate behavior remains guarded.")
    lines.append("- Default SIZE/address-unit behavior remains guarded.")
    lines.append("- Default PWRITX/font0/non-fontcap behavior remains guarded.")
    lines.append("- Source-mapped opt-in providers are implementation seams, not parity claims.")
    lines.append("")
    lines.append("## Recommended next action")
    lines.append("")
    lines.append("Run the full mainline smoke suite. If it passes, commit this milestone before starting another runtime branch.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")

    if missing:
        print("Milestone manifest status: missing artifacts detected")
        for item in missing:
            print(f"missing: {item}")
    else:
        print("Milestone manifest status: required artifacts present")


if __name__ == "__main__":
    main()
