from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOC = ROOT / "docs" / "ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"
OUT = ROOT / "docs" / "ncl_plotchar_pwritx_formula_audit.md"

TARGETS = (
    "PWRITX",
    "PWRITY",
    "IFNT",
    "NFNT",
    "NODF",
    "IQUF",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "DL",
    "DR",
    "DB",
    "DT",
)

FORMULA_HINTS = (
    "=",
    "CALL",
    "PWRITX",
    "PWRITY",
    "IFNT",
    "NFNT",
    "NODF",
    "IQUF",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "DL",
    "DR",
    "DB",
    "DT",
)


def read_doc(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required document: {path}")
    return path.read_text(encoding="utf-8")


def source_blocks(text: str) -> list[str]:
    return re.findall(r"```fortran\n(.*?)\n```", text, flags=re.DOTALL)


def target_lines(text: str, target: str, limit: int = 70) -> list[str]:
    out = []
    key = target.upper()
    for line in text.splitlines():
        if key in line.upper():
            out.append(line)
        if len(out) >= limit:
            break
    return out


def formula_like_lines(block: str) -> list[str]:
    out = []
    for line in block.splitlines():
        upper = line.upper()
        if any(hint in upper for hint in FORMULA_HINTS):
            out.append(line)
    return out


def main() -> None:
    text = read_doc(SOURCE_DOC)
    blocks = source_blocks(text)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Plotchar PWRITX / Font0 Formula Audit")
    lines.append("")
    lines.append("This report extracts compact PWRITX/font0/non-fontcap formula-like evidence from the exact branch packet.")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append("This audit does not implement PWRITX/font0. It only supports the next provider-backed runtime boundary.")
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
        lines.append("No Fortran source blocks found.")
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
    lines.append("- Identify exact PWRITX/font0 branch selection condition.")
    lines.append("- Identify required font database inputs.")
    lines.append("- Identify quality-resource interaction with PWRITX/font0.")
    lines.append("- Identify how PWRITX computes or mutates text extents.")
    lines.append("- Identify how PCGETR-visible `DL/DR/DB/DT` are produced.")
    lines.append("- Preserve current high-quality fontcap subset exactly.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append("Until the checklist is manually mapped, PWRITX metrics provider must remain opt-in and source-map guarded.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
