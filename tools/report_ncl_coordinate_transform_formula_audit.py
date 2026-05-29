from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFS = ROOT / "docs" / "ncl_coordinate_transform_function_definitions.md"
READY = ROOT / "docs" / "ncl_coordinate_transform_direction_readiness.md"
OUT = ROOT / "docs" / "ncl_coordinate_transform_formula_audit.md"

TARGETS = ("CFUX", "CFUY", "CUFX", "CUFY", "GETSET", "SET")
FORMULA_HINTS = (
    "=",
    "RETURN",
    "CALL",
    "WINDOW",
    "VIEWPORT",
    "XMIN",
    "XMAX",
    "YMIN",
    "YMAX",
    "VL",
    "VR",
    "VB",
    "VT",
    "WL",
    "WR",
    "WB",
    "WT",
)


def read(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required document: {path}")
    return path.read_text(encoding="utf-8")


def target_blocks(text: str, target: str) -> list[str]:
    pattern = re.compile(
        rf"#### `{target}` definition \d+:.*?\n\n```fortran\n(.*?)\n```",
        flags=re.DOTALL,
    )
    return pattern.findall(text)


def fallback_blocks(text: str, target: str) -> list[str]:
    pattern = re.compile(
        rf"#### `{target}` window \d+:.*?\n\n```fortran\n(.*?)\n```",
        flags=re.DOTALL,
    )
    return pattern.findall(text)


def formula_lines(block: str) -> list[str]:
    out = []
    for line in block.splitlines():
        upper = line.upper()
        if any(hint in upper for hint in FORMULA_HINTS):
            out.append(line)
    return out


def write_report() -> None:
    defs = read(DEFS)
    ready = read(READY)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Coordinate Transform Formula Audit")
    lines.append("")
    lines.append("This report extracts compact formula-like lines from the local NCL coordinate-transform definition report.")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append(
        "The Python linear window/viewport provider may only be used with an explicit, manually verified direction contract. "
        "This audit is evidence support; it is not automatic proof that runtime behavior is complete."
    )
    lines.append("")
    lines.append("## Direction readiness excerpt")
    lines.append("")
    lines.append("```text")
    for line in ready.splitlines():
        if any(target in line for target in TARGETS) or "Ready flag" in line or "Decision" in line:
            lines.append(line)
    lines.append("```")
    lines.append("")
    lines.append("## Formula-like source lines")
    lines.append("")

    for target in TARGETS:
        lines.append(f"### `{target}`")
        lines.append("")

        blocks = target_blocks(defs, target)
        fallbacks = fallback_blocks(defs, target)

        if not blocks and not fallbacks:
            lines.append("No definition or fallback block found.")
            lines.append("")
            continue

        for idx, block in enumerate(blocks, start=1):
            lines.append(f"#### definition block {idx}")
            lines.append("")
            lines.append("```fortran")
            extracted = formula_lines(block)
            if extracted:
                lines.extend(extracted)
            else:
                lines.append("No formula-like line extracted from this block.")
            lines.append("```")
            lines.append("")

        if not blocks:
            for idx, block in enumerate(fallbacks[:3], start=1):
                lines.append(f"#### fallback window {idx}")
                lines.append("")
                lines.append("```fortran")
                extracted = formula_lines(block)
                if extracted:
                    lines.extend(extracted)
                else:
                    lines.append("No formula-like line extracted from this window.")
                lines.append("```")
                lines.append("")

    lines.append("## Python implementation boundary")
    lines.append("")
    lines.append("- `CFUX/CFUY` are represented by user-to-plotchar conversion only when the direction contract is manually verified.")
    lines.append("- `CUFX/CUFY` are represented by plotchar-to-user conversion only when the direction contract is manually verified.")
    lines.append("- `GETSET/SET` are represented by an explicit window/viewport state object, not global hidden state.")
    lines.append("- No provider is enabled by default.")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
