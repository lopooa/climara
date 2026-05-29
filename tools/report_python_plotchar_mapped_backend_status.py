from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_mapped_backend_status.md"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Python Plotchar Mapped Backend Status")
    lines.append("")
    lines.append("## Current stage")
    lines.append("")
    lines.append("The mapped-coordinate Plotchar path now has a public explicit opt-in facade.")
    lines.append("")
    lines.append("## Stable public facade")
    lines.append("")
    lines.append("```python")
    lines.append("from climara.graphics.mapped_plotchar import (")
    lines.append("    NclCoordinateTransformDirectionContract,")
    lines.append("    NclWindowViewportState,")
    lines.append("    build_ncl_linear_mapped_backend_config,")
    lines.append("    compute_plchhq_with_ncl_linear_mapping,")
    lines.append(")")
    lines.append("```")
    lines.append("")
    lines.append("## Supported opt-in subset")
    lines.append("")
    lines.append("- TextItem measurement subset.")
    lines.append("- High-quality fontcap path.")
    lines.append("- Fractional `0 < SIZE < 1` subset.")
    lines.append("- Explicit `IMAP != 0` only through opt-in backend.")
    lines.append("- Explicit linear window/viewport state.")
    lines.append("- Manually verified direction contract.")
    lines.append("")
    lines.append("## Still guarded")
    lines.append("")
    lines.append("- Default `IMAP != 0` without opt-in backend.")
    lines.append("- Log scaling.")
    lines.append("- Non-linear map/projection transforms.")
    lines.append("- PWRITX / font 0 / non-fontcap metrics.")
    lines.append("- Medium / Low / Workstation quality paths.")
    lines.append("- Address-unit `SIZE` semantics.")
    lines.append("- Generic PLCHHQ calls outside current TextItem measurement contract.")
    lines.append("")
    lines.append("## Required source-map documents")
    lines.append("")
    for doc in [
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
    ]:
        lines.append(f"- `{doc}`")
    lines.append("")
    lines.append("## Boundary rule")
    lines.append("")
    lines.append(
        "The opt-in backend is not the default mapped-coordinate implementation. "
        "It is a source-contract-gated path for the current linear window/viewport subset only."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
