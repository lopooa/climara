from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_r_size_branch_source_map.md"

WINDOW_RADIUS = 44

FOCUS_TERMS = [
    "R",
    "SIZE",
    "IMAP",
    "MAP",
    "PCGTDI",
    "PCGETR",
    "PCSETR",
    "PCSETI",
    "XPOS",
    "YPOS",
    "XCEN",
    "YCEN",
    "XRGT",
    "YRGT",
    "XBEG",
    "YBEG",
    "XEND",
    "YEND",
    "DL",
    "DR",
    "DB",
    "DT",
    "PWRIT",
    "PWRITX",
    "PWRITY",
]

SOURCE_NAMES = [
    "plchhq.f",
    "pcgtdi.f",
    "pcgetr.f",
    "pcsetr.f",
    "pcseti.f",
    "pcsetc.f",
    "c_plchhq.c",
    "c_pcgetr.c",
    "c_pcsetr.c",
    "c_pcseti.c",
    "c_pcsetc.c",
]


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
    raise SystemExit(f"Could not decode {path}")


def find_named_sources(root: Path) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {name: [] for name in SOURCE_NAMES}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        lower = path.name.lower()
        for name in SOURCE_NAMES:
            if lower == name.lower():
                out[name].append(path)

    return out


def find_plchhq(root: Path) -> Path:
    sources = find_named_sources(root)
    hits = sources.get("plchhq.f", [])
    if not hits:
        raise SystemExit(f"Could not find plchhq.f under {root}")

    for path in hits:
        lower = str(path).lower()
        if "plotchar" in lower or "plot" in lower:
            return path

    return hits[0]


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def line_window(lines: list[str], line_number: int, radius: int = WINDOW_RADIUS) -> list[tuple[int, str]]:
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
    return [(idx, lines[idx - 1].rstrip()) for idx in range(start, end + 1)]


def r_patterns() -> list[tuple[str, re.Pattern[str]]]:
    return [
        ("R is for", re.compile(r"\bR\s+is\s+for\b", re.IGNORECASE)),
        ("quoted R", re.compile(r"['\"]R['\"]")),
        ("ICHAR(R)", re.compile(r"\bICHAR\s*\(\s*['\"]R['\"]\s*\)", re.IGNORECASE)),
        ("ASCII 82 near function-code logic", re.compile(r"\b82\b")),
    ]


def looks_relevant(line: str, reason: str) -> bool:
    upper = line.upper()
    if reason.startswith("ASCII") or reason.startswith("quoted"):
        return any(
            token in upper
            for token in (
                "NFCC",
                "ICHAR",
                "FUNCTION",
                "COMMAND",
                "PCGTDI",
                "SIZE",
                "MAP",
                "IMAP",
                "GO TO",
                "GOTO",
                "IS FOR",
                "PWRIT",
                "FONT",
                "QUALITY",
            )
        )
    return True


def find_r_windows(lines: list[str]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    hits: list[tuple[int, str, list[tuple[int, str]]]] = []
    seen: set[int] = set()

    for index, line in enumerate(lines, start=1):
        for reason, pattern in r_patterns():
            if not pattern.search(line):
                continue
            if not looks_relevant(line, reason):
                continue
            if index in seen:
                continue
            seen.add(index)
            hits.append((index, reason, line_window(lines, index)))
            break

    return hits


def term_hits(text: str, terms: list[str], max_hits: int = 16) -> dict[str, list[tuple[int, str]]]:
    lines = text.splitlines()
    out: dict[str, list[tuple[int, str]]] = {term: [] for term in terms}

    for index, line in enumerate(lines, start=1):
        upper = line.upper()
        for term in terms:
            if term.upper() in upper and len(out[term]) < max_hits:
                out[term].append((index, line.rstrip()))

    return out


def nearby_term_summary(lines: list[str], windows: list[tuple[int, str, list[tuple[int, str]]]]) -> dict[str, int]:
    counts = {term: 0 for term in FOCUS_TERMS if term != "R"}
    for _, _, window in windows:
        combined = "\n".join(source for _, source in window).upper()
        for term in counts:
            counts[term] += combined.count(term.upper())
    return counts


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    source = safe_read(plchhq)
    lines = source.splitlines()
    windows = find_r_windows(lines)
    nearby_counts = nearby_term_summary(lines, windows)
    hits = term_hits(source, FOCUS_TERMS)
    sources = find_named_sources(root)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc: list[str] = []
    doc.append("# NCL Plotchar `R` / SIZE Branch Source Map")
    doc.append("")
    doc.append("This document is generated from the local NCL source tree.")
    doc.append("")
    doc.append(f"- `NCL_SRC_ROOT`: `{root}`")
    doc.append(f"- `plchhq.f`: `{rel(plchhq, root)}`")
    doc.append("")
    doc.append("## Current decision")
    doc.append("")
    doc.append(
        "`R` remains guarded. The candidate report flagged it as involving "
        "address-unit `SIZE` semantics, and this stage only source-maps that risk. "
        "It does not implement `R`."
    )
    doc.append("")
    doc.append("## Required local source anchors")
    doc.append("")
    for name in SOURCE_NAMES:
        paths = sources.get(name, [])
        if not paths:
            doc.append(f"- `{name}`: not found")
        else:
            doc.append(f"- `{name}`")
            for path in paths[:4]:
                doc.append(f"  - `{rel(path, root)}`")
    doc.append("")
    doc.append("## `R` source windows from `plchhq.f`")
    doc.append("")
    if not windows:
        doc.append("No reliable local `R` source window was detected. `R` must remain guarded.")
        doc.append("")
    else:
        for hit_no, (line_number, reason, window) in enumerate(windows[:8], start=1):
            doc.append(f"### `R` hit {hit_no}: line {line_number}, reason: {reason}")
            doc.append("")
            doc.append("```fortran")
            for number, source_line in window:
                marker = ">>" if number == line_number else "  "
                doc.append(f"{marker} {number:6d}: {source_line}")
            doc.append("```")
            doc.append("")
    doc.append("## Risk terms near `R` windows")
    doc.append("")
    for term, count in sorted(nearby_counts.items(), key=lambda item: (-item[1], item[0])):
        doc.append(f"- `{term}`: {count}")
    doc.append("")
    doc.append("## Global keyword hits in `plchhq.f`")
    doc.append("")
    for term in FOCUS_TERMS:
        doc.append(f"### `{term}`")
        doc.append("")
        term_lines = hits.get(term, [])
        if not term_lines:
            doc.append("No hits.")
            doc.append("")
            continue
        for line_number, source_line in term_lines:
            doc.append(f"- line {line_number}: `{source_line.strip()}`")
        doc.append("")
    doc.append("## Checklist before implementing `R`")
    doc.append("")
    doc.append("- Locate the exact `R` branch entry and all exits in `plchhq.f`.")
    doc.append("- Determine whether `R` reads values through `PCGTDI` or a different parser path.")
    doc.append("- Map whether `R` changes `SIZE`, address-unit mode, or coordinate mapping.")
    doc.append("- Map effects on `XCEN/YCEN/XRGT/YRGT/XBEG/YBEG/XEND/YEND`.")
    doc.append("- Map effects on `DL/DR/DB/DT` and PCGETR-visible state.")
    doc.append("- Add positive smoke only for source-mapped supported `R` cases.")
    doc.append("- Keep any unmapped `R` subcases guarded.")
    doc.append("")
    doc.append("## Guard rule")
    doc.append("")
    doc.append(
        "`R` must continue to raise `PlotcharUnsupportedError` until the checklist is complete. "
        "It must not be ignored, approximated, or treated as a normal glyph."
    )
    doc.append("")

    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT}")
    print("R remains guarded; SIZE/address-unit branch requires full source mapping before implementation.")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
