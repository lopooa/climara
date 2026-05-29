from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_coordinate_transform_source_map.md"

KEYWORDS = [
    "CFUX",
    "CFUY",
    "CUFX",
    "CUFY",
    "GETSET",
    "SET",
    "GKS",
    "WINDOW",
    "VIEWPORT",
    "XMIN",
    "XMAX",
    "YMIN",
    "YMAX",
    "XPOS",
    "YPOS",
    "IMAP",
    "MAP",
    "USER",
    "FRACTIONAL",
]

WINDOW_RADIUS = 26


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running.")

    root = Path(value)
    if not root.exists():
        raise SystemExit(f"NCL_SRC_ROOT does not exist: {root}")

    return root


def safe_read(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return ""


def candidate_source_files(root: Path) -> list[Path]:
    suffixes = {".f", ".F", ".f90", ".F90", ".c", ".h", ".ncl", ".txt"}
    out: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue

        lower = str(path).lower()
        name = path.name.lower()

        if (
            "plotchar" in lower
            or "plot" in lower
            or "gks" in lower
            or "gridal" in lower
            or name in {"plchhq.f", "c_plchhq.c"}
            or name.startswith(("cfu", "cuf", "set", "getset", "pc"))
        ):
            out.append(path)

    return sorted(set(out))


def is_relevant(keyword: str, line: str) -> bool:
    upper = line.upper()
    key = keyword.upper()

    if key not in upper:
        return False

    if key in {"SET", "MAP", "USER"}:
        return any(
            token in upper
            for token in (
                "CALL",
                "SUBROUTINE",
                "FUNCTION",
                "GETSET",
                "CFUX",
                "CFUY",
                "CUFX",
                "CUFY",
                "XPOS",
                "YPOS",
                "IMAP",
                "WINDOW",
                "VIEWPORT",
            )
        )

    return True


def windows_for_keyword(path: Path, keyword: str) -> list[tuple[int, list[tuple[int, str]]]]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    hits: list[tuple[int, list[tuple[int, str]]]] = []

    for index, line in enumerate(lines, start=1):
        if not is_relevant(keyword, line):
            continue

        start = max(1, index - WINDOW_RADIUS)
        end = min(len(lines), index + WINDOW_RADIUS)
        hits.append(
            (
                index,
                [(number, lines[number - 1].rstrip()) for number in range(start, end + 1)],
            )
        )

        if len(hits) >= 6:
            break

    return hits


def write_report() -> None:
    root = ncl_root()
    files = candidate_source_files(root)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Coordinate Transform Source Map for Plotchar")
    lines.append("")
    lines.append("This report is generated from the local NCL source tree.")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append(
        "The Python mapped-coordinate Plotchar provider must not implement coordinate "
        "conversion until the local NCL transform functions are mapped. This report "
        "collects source windows for `CFUX`, `CFUY`, `CUFX`, `CUFY`, `GETSET`, and "
        "`SET`-related coordinate state."
    )
    lines.append("")
    lines.append("## Candidate source files")
    lines.append("")

    for path in files[:160]:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        lines.append(f"- `{rel}`")

    lines.append("")
    lines.append("## Keyword source windows")
    lines.append("")

    total_hits = 0

    for keyword in KEYWORDS:
        lines.append(f"### `{keyword}`")
        lines.append("")

        count = 0

        for path in files:
            hits = windows_for_keyword(path, keyword)
            if not hits:
                continue

            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path

            for center, window in hits[:3]:
                count += 1
                total_hits += 1
                lines.append(f"#### `{keyword}` hit {count}: `{rel}` line {center}")
                lines.append("")
                lines.append("```fortran")

                for line_number, source_line in window:
                    marker = ">>" if line_number == center else "  "
                    lines.append(f"{marker} {line_number:6d}: {source_line}")

                lines.append("```")
                lines.append("")

                if count >= 10:
                    break

            if count >= 10:
                break

        if count == 0:
            lines.append("No relevant source window detected.")
            lines.append("")

    lines.append("## Required mapping checklist")
    lines.append("")
    lines.append("- Identify whether `CFUX/CFUY` convert from user to fractional/NDC or the reverse.")
    lines.append("- Identify whether `CUFX/CUFY` convert from fractional/NDC to user or the reverse.")
    lines.append("- Identify how `GETSET` exposes viewport/window state.")
    lines.append("- Identify how Plotchar `IMAP != 0` chooses which conversion direction to use.")
    lines.append("- Identify whether text extents `DSTL/DSTR/DSTB/DSTT` are converted or remain local offsets.")
    lines.append("- Identify whether PCGETR geometry values `XB/XC/XE/YB/YC/YE` are transformed before exposure.")
    lines.append("- Add source-mapped positive smokes before enabling runtime.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        "Until this checklist is complete, the NCL mapped-coordinate transform provider "
        "must remain guarded and `source_mapped=False`."
    )
    lines.append("")
    lines.append(f"Total source-window hits: `{total_hits}`")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"Coordinate transform source-window hits: {total_hits}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
