from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_final_stage_closure.md"

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
    "docs/python_plotchar_mapped_backend_status.md",
    "docs/python_plotchar_mapped_opt_in_backend_usage.md",
    "docs/python_plotchar_size_address_provider_backend_status.md",
    "docs/python_plotchar_pwritx_provider_backend_status.md",
    "docs/python_plotchar_completion_roadmap.md",
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


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def checklist(items: list[str]) -> list[str]:
    return [f"- [{'x' if exists(item) else ' '}] `{item}`" for item in items]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    missing = [item for item in RUNTIME_MODULES + STATUS_DOCS + SOURCE_DOCS if not exists(item)]

    lines = []
    lines.append("# Python Plotchar Final Stage Closure")
    lines.append("")
    lines.append("## Closure scope")
    lines.append("")
    lines.append("This document closes the current TextItem/fontcap Plotchar stage as a bounded milestone.")
    lines.append("")
    lines.append("This is not a full NCL PLCHHQ parity claim.")
    lines.append("")
    lines.append("## What this stage supports")
    lines.append("")
    lines.append("- Source-mapped TextItem measurement boundary.")
    lines.append("- High-quality fontcap mainline for the audited subset.")
    lines.append("- Current implemented inline function-code subset covered by smoke tests.")
    lines.append("- Default TextItem bbox integration through Python Plotchar provider.")
    lines.append("- Default MultiText bbox integration through Python Plotchar provider.")
    lines.append("- LabelBar / AdjustGeometry pathways using Plotchar-provider bbox semantics.")
    lines.append("- Explicit opt-in mapped-coordinate linear window/viewport backend.")
    lines.append("- Explicit provider-backed SIZE/address-unit backend seam.")
    lines.append("- Explicit provider-backed PWRITX/font0/non-fontcap backend seam.")
    lines.append("")
    lines.append("## Default behavior that remains guarded")
    lines.append("")
    lines.append("- Default `IMAP != 0` without explicit mapped backend.")
    lines.append("- Default `SIZE <= 0` and `SIZE >= 1` without explicit SIZE/address provider.")
    lines.append("- Default PWRITX / font 0 / non-fontcap branch without explicit PWRITX provider.")
    lines.append("- Medium / Low / Workstation quality branches without source-mapped provider.")
    lines.append("- Log scaling.")
    lines.append("- Non-linear map/projection transforms.")
    lines.append("- Generic PLCHHQ outside the current TextItem measurement contract.")
    lines.append("- Any unsupported function-code branch not explicitly covered by source-map and smoke.")
    lines.append("")
    lines.append("## Public opt-in facades")
    lines.append("")
    lines.append("### Mapped-coordinate")
    lines.append("")
    lines.append("```python")
    lines.append("from climara.graphics.mapped_plotchar import compute_plchhq_with_ncl_linear_mapping")
    lines.append("```")
    lines.append("")
    lines.append("### SIZE/address-unit")
    lines.append("")
    lines.append("```python")
    lines.append("from climara.graphics.size_address_plotchar import compute_plchhq_with_size_address_provider")
    lines.append("```")
    lines.append("")
    lines.append("### PWRITX/font0/non-fontcap")
    lines.append("")
    lines.append("```python")
    lines.append("from climara.graphics.pwritx_plotchar import compute_plchhq_with_pwritx_provider")
    lines.append("```")
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
    lines.append("## Missing artifacts")
    lines.append("")
    if missing:
        for item in missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("No required closure artifacts are missing.")
    lines.append("")
    lines.append("## Recommended next branch")
    lines.append("")
    lines.append("Start the next branch only after this closure smoke passes. Good candidates:")
    lines.append("")
    lines.append("1. Update `python_plotchar_stage_status.md` and `python_plotchar_completion_roadmap.md` to include PWRITX facade.")
    lines.append("2. Start real SIZE/address-unit formula implementation after manual source mapping.")
    lines.append("3. Start remaining inline function-code commands.")
    lines.append("4. Start higher-level TextItem/MultiText/LabelBar integration docs/examples.")
    lines.append("")
    lines.append("## Boundary rule")
    lines.append("")
    lines.append("Anything outside this listed subset remains guarded. Do not present this milestone as complete NCL PLCHHQ parity.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")

    if missing:
        print("Final stage closure status: missing artifacts detected")
        for item in missing:
            print(f"missing: {item}")
    else:
        print("Final stage closure status: required artifacts present")


if __name__ == "__main__":
    main()
