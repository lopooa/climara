from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_pwritx_nonfontcap_branch_source_map.md"

KEYWORDS = [
    "PWRITX",
    "PWRITY",
    "PWRIT",
    "PWR",
    "NODF",
    "FONT",
    "FN",
    "FONT 0",
    "IQUF",
    "QU",
    "QUALITY",
    "WORKSTATION",
    "LOW",
    "MEDIUM",
    "HIGH",
    "FONTCAP",
    "FCAP",
    "DB",
    "DATABASE",
    "PCSETI",
    "PCSETR",
    "PCGETR",
    "PLCHHQ",
]

WINDOW_RADIUS = 22


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running this report.")

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
            or "fontcap" in lower
            or "pwrit" in lower
            or "pwr" in name
            or name.startswith("pc")
            or name in {"plchhq.f", "c_plchhq.c"}
        ):
            out.append(path)

    return sorted(set(out))


def keyword_windows(path: Path, keyword: str) -> list[tuple[int, list[tuple[int, str]]]]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    upper_keyword = keyword.upper()
    hits: list[tuple[int, list[tuple[int, str]]]] = []

    for index, line in enumerate(lines, start=1):
        upper = line.upper()

        if upper_keyword not in upper:
            continue

        if keyword in {"LOW", "MEDIUM", "HIGH", "DB", "FN", "QU"}:
            if not any(
                token in upper
                for token in (
                    "PWR",
                    "FONT",
                    "QUALITY",
                    "IQUF",
                    "PCSET",
                    "PCGET",
                    "PLCHHQ",
                    "FUNCTION",
                    "COMMAND",
                )
            ):
                continue

        start = max(1, index - WINDOW_RADIUS)
        end = min(len(lines), index + WINDOW_RADIUS)
        window = [
            (line_number, lines[line_number - 1].rstrip())
            for line_number in range(start, end + 1)
        ]
        hits.append((index, window))

        if len(hits) >= 6:
            break

    return hits


def write_report() -> None:
    root = ncl_root()
    files = candidate_source_files(root)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Plotchar PWRITX / Non-Fontcap Branch Source Map")
    lines.append("")
    lines.append("This report is generated from the local NCL source tree.")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append(
        "PWRITX, font 0, non-fontcap metrics, and non-high-quality Plotchar paths "
        "remain guarded in Python. The current Python mainline implements only the "
        "TextItem high-quality fontcap measurement subset."
    )
    lines.append("")
    lines.append("## Current supported Python subset")
    lines.append("")
    lines.append("- TextItem measurement")
    lines.append("- High quality")
    lines.append("- fontcap glyph data")
    lines.append("- `IMAP == 0`")
    lines.append("- `0 < SIZE < 1`")
    lines.append("- `ANGD == 360.0`")
    lines.append("- `CNTR == -1.0`")
    lines.append("")
    lines.append("## Candidate NCL source files")
    lines.append("")

    for path in files[:120]:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        lines.append(f"- `{rel}`")

    lines.append("")
    lines.append("## Keyword source windows")
    lines.append("")

    any_hit = False

    for keyword in KEYWORDS:
        lines.append(f"### `{keyword}`")
        lines.append("")

        keyword_hit_count = 0

        for path in files:
            hits = keyword_windows(path, keyword)

            if not hits:
                continue

            any_hit = True

            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path

            for hit_number, (center, window) in enumerate(hits[:3], start=1):
                keyword_hit_count += 1
                lines.append(f"#### `{keyword}` hit {keyword_hit_count}: `{rel}` line {center}")
                lines.append("")
                lines.append("```fortran")

                for line_number, source_line in window:
                    marker = ">>" if line_number == center else "  "
                    lines.append(f"{marker} {line_number:6d}: {source_line}")

                lines.append("```")
                lines.append("")

                if keyword_hit_count >= 8:
                    break

            if keyword_hit_count >= 8:
                break

        if keyword_hit_count == 0:
            lines.append("No relevant source window detected.")
            lines.append("")

    lines.append("## Checklist before implementation")
    lines.append("")
    lines.append("- Locate the exact NCL branch where font 0 selects PWRITX / database font behavior.")
    lines.append("- Map quality selector resources, especially `QU` / `IQUF`.")
    lines.append("- Determine how PWRITX obtains glyph metrics and how those differ from fontcap RDGU metrics.")
    lines.append("- Map effects on `DL/DR/DB/DT` and PCGETR-visible state.")
    lines.append("- Map whether PWRITX participates in the same `XCEN/YCEN/XRGT/YRGT` state flow as fontcap.")
    lines.append("- Add positive smokes only after complete metrics semantics are mapped.")
    lines.append("- Keep non-mapped subcases guarded.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        "Font 0, PWRITX, non-fontcap metrics, Medium, Low, and Workstation quality "
        "paths must continue to raise guarded errors. They must not fall back to "
        "fontcap metrics, SVG text metrics, browser metrics, character-count metrics, "
        "or fixed-width estimates."
    )
    lines.append("")

    if not any_hit:
        lines.append("## Warning")
        lines.append("")
        lines.append(
            "No keyword source windows were detected. This means the local source layout "
            "needs manual inspection before attempting implementation."
        )
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
