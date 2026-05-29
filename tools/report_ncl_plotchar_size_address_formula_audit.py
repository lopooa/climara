from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOC = ROOT / "docs" / "ncl_plotchar_size_address_exact_branch_packet.md"
OUT = ROOT / "docs" / "ncl_plotchar_size_address_formula_audit.md"

TARGETS = (
    "SIZE",
    "ISIZ",
    "RSIZ",
    "PCGTDI",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "XCEN",
    "YCEN",
    "XRGT",
    "YRGT",
)

FORMULA_HINTS = (
    "=",
    "SIZE",
    "ISIZ",
    "RSIZ",
    "PCGTDI",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "XCEN",
    "YCEN",
    "XRGT",
    "YRGT",
    "IF",
    "GO TO",
    "CALL",
)


def read_doc(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required document: {path}")
    return path.read_text(encoding="utf-8")


def source_blocks(text: str) -> list[str]:
    return re.findall(r"```fortran\n(.*?)\n```", text, flags=re.DOTALL)


def formula_like_lines(block: str) -> list[str]:
    out = []
    for line in block.splitlines():
        upper = line.upper()
        if any(hint in upper for hint in FORMULA_HINTS):
            out.append(line)
    return out


def target_lines(text: str, target: str, limit: int = 80) -> list[str]:
    lines = []
    upper_target = target.upper()
    for line in text.splitlines():
        if upper_target in line.upper():
            lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def write_report() -> None:
    text = read_doc(SOURCE_DOC)
    blocks = source_blocks(text)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Plotchar SIZE / Address-Unit Formula Audit")
    lines.append("")
    lines.append("This report extracts formula-like lines from the local SIZE/address exact branch packet.")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append(
        "This audit is evidence support only. It does not implement address-unit SIZE. "
        "A Python provider may only compute address-unit scaling after the relevant "
        "NCL formulas and state transitions are manually mapped."
    )
    lines.append("")
    lines.append("## Compact target lines")
    lines.append("")

    for target in TARGETS:
        lines.append(f"### `{target}`")
        lines.append("")
        lines.append("```text")
        compact = target_lines(text, target)
        if compact:
            lines.extend(compact)
        else:
            lines.append("No compact target line found.")
        lines.append("```")
        lines.append("")

    lines.append("## Formula-like lines from source windows")
    lines.append("")

    if not blocks:
        lines.append("No Fortran source blocks found in SIZE/address exact branch packet.")
        lines.append("")
    else:
        for index, block in enumerate(blocks, start=1):
            extracted = formula_like_lines(block)
            if not extracted:
                continue

            lines.append(f"### Source block {index}")
            lines.append("")
            lines.append("```fortran")
            lines.extend(extracted)
            lines.append("```")
            lines.append("")

    lines.append("## Manual mapping checklist")
    lines.append("")
    lines.append("- Identify exact conversion from address-unit SIZE to the fractional core size used for fontcap metrics.")
    lines.append("- Identify whether `SIZE == 0`, `SIZE < 0`, and `SIZE >= 1` are separate NCL branches.")
    lines.append("- Identify how `ISIZ/RSIZ` interact with `PCGTDI` and inline function-code size commands.")
    lines.append("- Identify whether address-unit SIZE affects origin, advance, extent, or all geometry state.")
    lines.append("- Identify whether `DSTL/DSTR/DSTB/DSTT` are recomputed or scaled from an intermediate core result.")
    lines.append("- Preserve current `0 < SIZE < 1` behavior exactly.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        "Until the checklist is manually mapped, provider-backed SIZE/address runtime must remain opt-in and guarded by source-map contracts."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
