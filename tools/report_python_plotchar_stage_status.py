from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_stage_status.md"


REQUIRED_SOURCE_DOCS = [
    "docs/ncl_plotchar_metrics_source_map.md",
    "docs/ncl_plotchar_function_code_coverage.md",
    "docs/ncl_plotchar_guarded_command_windows.md",
    "docs/ncl_plotchar_next_implementation_candidates.md",
    "docs/ncl_plotchar_size_address_unit_branch_source_map.md",
    "docs/ncl_plotchar_pwritx_nonfontcap_branch_source_map.md",
    "docs/ncl_plotchar_mapped_coordinate_branch_source_map.md",
    "docs/ncl_plotchar_mapped_branch_labels.md",
    "docs/ncl_plotchar_mapped_label_resolution.md",
    "docs/ncl_plotchar_mapped_branch_readiness.md",
    "docs/ncl_plotchar_mapped_exact_branch_packet.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
    "docs/ncl_plotchar_coordinate_transform_source_map.md",
    "docs/ncl_coordinate_transform_function_definitions.md",
    "docs/ncl_coordinate_transform_direction_readiness.md",
    "docs/ncl_coordinate_transform_formula_audit.md",
    "docs/ncl_plotchar_mapped_opt_in_backend_status.md",
    "docs/python_plotchar_mapped_backend_status.md",
]


REQUIRED_RUNTIME_MODULES = [
    "src/climara/graphics/_plotchar_state.py",
    "src/climara/graphics/_plotchar_fontcap.py",
    "src/climara/graphics/_plotchar_function_code.py",
    "src/climara/graphics/_plotchar_plchhq_extent.py",
    "src/climara/graphics/_plotchar_mapped_coordinate.py",
    "src/climara/graphics/_plotchar_mapped_runtime_strategy.py",
    "src/climara/graphics/_plotchar_mapped_transform_ncl.py",
    "src/climara/graphics/_plotchar_mapped_opt_in.py",
    "src/climara/graphics/mapped_plotchar.py",
]


def present(path: str) -> bool:
    return (ROOT / path).exists()


def format_checklist(items: list[str]) -> list[str]:
    lines = []
    for item in items:
        mark = "x" if present(item) else " "
        lines.append(f"- [{mark}] `{item}`")
    return lines


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    missing_docs = [item for item in REQUIRED_SOURCE_DOCS if not present(item)]
    missing_modules = [item for item in REQUIRED_RUNTIME_MODULES if not present(item)]

    lines = []
    lines.append("# Python Plotchar Stage Status")
    lines.append("")
    lines.append("## Stage summary")
    lines.append("")
    lines.append(
        "This document records the current Python Plotchar stage in climara. "
        "It separates implemented behavior, explicit opt-in behavior, and guarded behavior."
    )
    lines.append("")
    lines.append("## Completed runtime pieces")
    lines.append("")
    lines.append("- Source-mapped Plotchar state model boundary.")
    lines.append("- PCGTDI-style signed decimal parser coverage.")
    lines.append("- TextItem measurement call boundary.")
    lines.append("- High-quality fontcap glyph parsing path.")
    lines.append("- Printable/source-mapped subset of PLCHHQ text extent computation.")
    lines.append("- Implemented function-code groups currently covered by smoke tests:")
    lines.append("  - Across / Down direction prefix handling.")
    lines.append("  - Font change subset.")
    lines.append("  - B/S/E/N script handling.")
    lines.append("  - P/I/K size-level handling.")
    lines.append("  - U/L case handling.")
    lines.append("  - C carriage return handling.")
    lines.append("  - X/Y/Z zoom handling.")
    lines.append("  - H/V movement handling.")
    lines.append("- Default TextItem bbox engine integration through the Python Plotchar mainline.")
    lines.append("- Default MultiText bbox engine integration through the Python Plotchar mainline.")
    lines.append("- LabelBar / AdjustGeometry pathway can consume Plotchar-provider bboxes.")
    lines.append("")
    lines.append("## Mapped-coordinate stage")
    lines.append("")
    lines.append("### Completed")
    lines.append("")
    lines.append("- Mapped-coordinate source-map documents.")
    lines.append("- Fixed-form label resolution for mapped-coordinate branch.")
    lines.append("- Mapped-coordinate readiness gate.")
    lines.append("- Exact mapped branch packet.")
    lines.append("- Extent alias source-map for `DSTL/DSTR/DSTB/DSTT` and `DL/DR/DB/DT`.")
    lines.append("- Mapped-coordinate boundary module.")
    lines.append("- Runtime dispatch seam from `compute_plchhq_fontcap_text_extent(...)`.")
    lines.append("- Runtime API and result bridge.")
    lines.append("- Transform provider contract.")
    lines.append("- Runtime strategy contract.")
    lines.append("- Provider-backed runtime strategy.")
    lines.append("- NCL coordinate-transform source-map.")
    lines.append("- NCL linear window/viewport transform provider.")
    lines.append("- Explicit opt-in mapped backend.")
    lines.append("- Public facade: `climara.graphics.mapped_plotchar`.")
    lines.append("")
    lines.append("### Supported explicit opt-in subset")
    lines.append("")
    lines.append("- `IMAP != 0` only through explicit opt-in backend.")
    lines.append("- TextItem measurement subset.")
    lines.append("- High-quality fontcap path.")
    lines.append("- Fractional `0 < SIZE < 1` subset.")
    lines.append("- Linear window/viewport transform only.")
    lines.append("- Explicit `NclWindowViewportState`.")
    lines.append("- Manually verified `NclCoordinateTransformDirectionContract`.")
    lines.append("")
    lines.append("### Default behavior")
    lines.append("")
    lines.append("- Default `IMAP != 0` path remains guarded.")
    lines.append("- No automatic mapped-coordinate runtime is enabled.")
    lines.append("- The opt-in backend must remain separate from the default mainline until broader semantics are complete.")
    lines.append("")
    lines.append("## Still guarded / not complete")
    lines.append("")
    lines.append("- Address-unit `SIZE` semantics.")
    lines.append("- PWRITX / font 0 / non-fontcap branch.")
    lines.append("- Medium / Low / Workstation quality branches.")
    lines.append("- Log scaling in coordinate transforms.")
    lines.append("- Non-linear map/projection transforms.")
    lines.append("- Generic PLCHHQ calls outside current TextItem measurement contract.")
    lines.append("- Unsupported function-code branches not covered by current source-mapped subset.")
    lines.append("- Full NCL parity cannot be claimed.")
    lines.append("")
    lines.append("## Runtime modules")
    lines.append("")
    lines.extend(format_checklist(REQUIRED_RUNTIME_MODULES))
    lines.append("")
    lines.append("## Source-map documents")
    lines.append("")
    lines.extend(format_checklist(REQUIRED_SOURCE_DOCS))
    lines.append("")
    lines.append("## Missing items detected by this report")
    lines.append("")
    if missing_modules or missing_docs:
        if missing_modules:
            lines.append("### Missing runtime modules")
            lines.append("")
            for item in missing_modules:
                lines.append(f"- `{item}`")
            lines.append("")
        if missing_docs:
            lines.append("### Missing source-map documents")
            lines.append("")
            for item in missing_docs:
                lines.append(f"- `{item}`")
            lines.append("")
    else:
        lines.append("No missing required stage artifacts were detected.")
        lines.append("")
    lines.append("## Next recommended stages")
    lines.append("")
    lines.append("1. Add focused smokes for the public mapped facade in downstream TextItem bbox calls.")
    lines.append("2. Decide whether the opt-in mapped backend should stay experimental/private or receive public documentation.")
    lines.append("3. Start `SIZE/address-unit` branch implementation only after exact source mapping.")
    lines.append("4. Start PWRITX/non-fontcap branch implementation only after exact source mapping.")
    lines.append("5. Keep all non-source-mapped subcases guarded.")
    lines.append("")
    lines.append("## Boundary rule")
    lines.append("")
    lines.append(
        "This stage report is not a full parity claim. It records a source-mapped, "
        "smoke-tested Python Plotchar subset plus an explicit opt-in mapped-coordinate "
        "linear backend. Anything outside the listed subset remains guarded."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")

    if missing_modules or missing_docs:
        print("Stage status: incomplete artifacts detected")
        for item in missing_modules + missing_docs:
            print(f"missing: {item}")
    else:
        print("Stage status: required artifacts present")


if __name__ == "__main__":
    main()
