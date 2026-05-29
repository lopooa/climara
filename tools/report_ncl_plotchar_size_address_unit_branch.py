from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_size_address_unit_branch_source_map.md"

KEYWORDS = [
    "SIZE",
    "ADDRESS",
    "IMAP",
    "MAP",
    "G",
    "R",
    "PCGTDI",
    "PCGETR",
    "PCSETR",
    "PCSETI",
    "XPOS",
    "YPOS",
    "XCRA",
    "YCRA",
    "XCEN",
    "YCEN",
    "XRGT",
    "YRGT",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
]

WINDOW_RADIUS = 28


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running this report.")

    root = Path(value)
    if not root.exists():
        raise SystemExit(f"NCL_SRC_ROOT does not exist: {root}")

    return root


def find_plchhq(root: Path) -> Path:
    hits = sorted(path for path in root.rglob("plchhq.f") if path.is_file())

    if not hits:
        raise SystemExit(f"Could not find plchhq.f under {root}")

    for path in hits:
        lower = str(path).lower()
        if "plotchar" in lower or "plot" in lower:
            return path

    return hits[0]


def safe_read(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise SystemExit(f"Could not decode {path}")


def is_relevant(line: str, keyword: str) -> bool:
    upper = line.upper()

    if keyword in {"G", "R"}:
        patterns = [
            rf"\b{keyword}\s+IS\s+FOR\b",
            rf"['\"]{keyword}['\"]",
            rf"\bICHAR\s*\(\s*['\"]{keyword}['\"]\s*\)",
            rf"\b{ord(keyword)}\b",
        ]

        if not any(re.search(pattern, upper) for pattern in patterns):
            return False

        return any(
            token in upper
            for token in (
                "IS FOR",
                "NFCC",
                "ICHAR",
                "COMMAND",
                "FUNCTION",
                "PCGTDI",
                "SIZE",
                "MAP",
                "GOTO",
                "GO TO",
            )
        )

    return keyword in upper


def windows_for_keyword(lines: list[str], keyword: str) -> list[tuple[int, list[tuple[int, str]]]]:
    hits: list[tuple[int, list[tuple[int, str]]]] = []

    for index, line in enumerate(lines, start=1):
        if not is_relevant(line, keyword):
            continue

        start = max(1, index - WINDOW_RADIUS)
        end = min(len(lines), index + WINDOW_RADIUS)

        window = [
            (line_number, lines[line_number - 1].rstrip())
            for line_number in range(start, end + 1)
        ]

        hits.append((index, window))

        if len(hits) >= 8:
            break

    return hits


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    lines = text.splitlines()

    OUT.parent.mkdir(parents=True, exist_ok=True)

    out: list[str] = []
    out.append("# NCL Plotchar SIZE / Address-Unit Branch Source Map")
    out.append("")
    out.append("This report is generated from the local NCL source tree.")
    out.append("")
    out.append(f"- `NCL_SRC_ROOT`: `{root}`")
    out.append(f"- `plchhq.f`: `{plchhq}`")
    out.append("")
    out.append("## Current decision")
    out.append("")
    out.append(
        "The Python Plotchar mainline must continue to guard address-unit `SIZE`, "
        "`IMAP != 0`, mapped-coordinate behavior, and guarded commands such as `G` "
        "and `R` until the complete NCL branch is mapped."
    )
    out.append("")
    out.append("Current supported measurement contract remains:")
    out.append("")
    out.append("- TextItem measurement call")
    out.append("- `PCSETI(\"TE\", 1)`")
    out.append("- `ANGD == 360.0`")
    out.append("- `CNTR == -1.0`")
    out.append("- `IMAP == 0`")
    out.append("- `0 < SIZE < 1`")
    out.append("- High-quality fontcap branch")
    out.append("")
    out.append("## Keyword source windows")
    out.append("")

    for keyword in KEYWORDS:
        out.append(f"### `{keyword}`")
        out.append("")

        hits = windows_for_keyword(lines, keyword)

        if not hits:
            out.append("No relevant source window detected.")
            out.append("")
            continue

        for hit_number, (center, window) in enumerate(hits, start=1):
            out.append(f"#### `{keyword}` hit {hit_number}: line {center}")
            out.append("")
            out.append("```fortran")

            for line_number, source_line in window:
                marker = ">>" if line_number == center else "  "
                out.append(f"{marker} {line_number:6d}: {source_line}")

            out.append("```")
            out.append("")

    out.append("## Checklist before implementation")
    out.append("")
    out.append("- Locate the exact NCL branch for address-unit `SIZE` semantics.")
    out.append("- Locate whether `G` and `R` are genuinely part of this branch or only heuristic noise.")
    out.append("- Map how NCL interprets `SIZE <= 0` and `SIZE >= 1`.")
    out.append("- Map how `IMAP != 0` changes input/output coordinates.")
    out.append("- Map effects on `XCEN/YCEN/XRGT/YRGT/XBEG/YBEG/XEND/YEND`.")
    out.append("- Map effects on `DL/DR/DB/DT` and `PCGETR` state.")
    out.append("- Add positive smokes only after the complete branch is mapped.")
    out.append("- Keep all unsupported subcases guarded.")
    out.append("")
    out.append("## Guard rule")
    out.append("")
    out.append(
        "`SIZE` address-unit behavior, `IMAP != 0`, `G`, and `R` remain guarded "
        "until this branch is fully mapped from NCL source."
    )
    out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
