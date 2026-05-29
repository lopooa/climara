from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_mapped_opt_in_backend_status.md"


def write_report() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Plotchar Explicit Opt-In Mapped Backend Status")
    lines.append("")
    lines.append("## Current status")
    lines.append("")
    lines.append("The Python Plotchar mapped-coordinate path now has an explicit opt-in linear window/viewport backend.")
    lines.append("")
    lines.append("## What is supported")
    lines.append("")
    lines.append("- `IMAP != 0` only through explicit opt-in.")
    lines.append("- TextItem measurement subset.")
    lines.append("- High-quality fontcap path.")
    lines.append("- Fractional `0 < SIZE < 1` subset.")
    lines.append("- Linear window/viewport transform provider.")
    lines.append("- Manually verified direction contract.")
    lines.append("- Explicit `NclWindowViewportState` instead of hidden global GKS state.")
    lines.append("")
    lines.append("## What remains guarded")
    lines.append("")
    lines.append("- Default `IMAP != 0` path without opt-in backend.")
    lines.append("- Log scaling.")
    lines.append("- Map projection / non-linear transforms.")
    lines.append("- PWRITX / font 0 / non-fontcap branch.")
    lines.append("- Medium / Low / Workstation quality.")
    lines.append("- Address-unit `SIZE` semantics.")
    lines.append("- Generic PLCHHQ calls outside TextItem measurement.")
    lines.append("")
    lines.append("## Runtime entry")
    lines.append("")
    lines.append("```python")
    lines.append("from climara.graphics._plotchar_mapped_opt_in import compute_plchhq_with_ncl_linear_mapping")
    lines.append("```")
    lines.append("")
    lines.append("## Source-map documents")
    lines.append("")
    for doc in [
        "docs/ncl_coordinate_transform_function_definitions.md",
        "docs/ncl_coordinate_transform_direction_readiness.md",
        "docs/ncl_coordinate_transform_formula_audit.md",
        "docs/ncl_plotchar_mapped_exact_branch_packet.md",
        "docs/ncl_plotchar_extent_alias_source_map.md",
    ]:
        lines.append(f"- `{doc}`")
    lines.append("")
    lines.append("## Boundary rule")
    lines.append("")
    lines.append(
        "This backend is an explicit opt-in path only. It must not be enabled as the default "
        "for `IMAP != 0` until broader mapped-coordinate semantics are completed and validated."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
