from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_g_command_source_map.md"

WINDOW_RADIUS = 36

RISK_TERMS = [
    "SIZE",
    "IMAP",
    "MAP",
    "PWRIT",
    "PWRITX",
    "PWRITY",
    "IQUF",
    "WORKSTATION",
    "ADDRESS",
    "COORD",
    "XPOS",
    "YPOS",
    "XCRA",
    "YCRA",
    "ICRA",
    "PCGETR",
    "PCSETR",
]


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


def line_window(lines: list[str], line_number: int, radius: int = WINDOW_RADIUS) -> list[tuple[int, str]]:
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
    return [(index, lines[index - 1].rstrip()) for index in range(start, end + 1)]


def relevant_g_hits(lines: list[str]) -> list[tuple[int, str, str]]:
    patterns = [
        ("G is for", re.compile(r"\bG\s+is\s+for\b", re.IGNORECASE)),
        ("quoted G", re.compile(r"['\"]G['\"]")),
        ("ICHAR(G)", re.compile(r"\bICHAR\s*\(\s*['\"]G['\"]\s*\)", re.IGNORECASE)),
        ("ASCII 71 near function-code logic", re.compile(r"\b71\b")),
    ]

    hits: list[tuple[int, str, str]] = []

    for index, line in enumerate(lines, start=1):
        upper = line.upper()

        for reason, pattern in patterns:
            if not pattern.search(line):
                continue

            if reason.startswith("ASCII") and not any(
                token in upper
                for token in (
                    "NFCC",
                    "ICHAR",
                    "FUNCTION",
                    "COMMAND",
                    "PCGTDI",
                    "SIZE",
                    "MAP",
                    "PWRIT",
                    "GO TO",
                    "GOTO",
                )
            ):
                continue

            if reason == "quoted G" and not any(
                token in upper
                for token in (
                    "NFCC",
                    "ICHAR",
                    "FUNCTION",
                    "COMMAND",
                    "PCGTDI",
                    "SIZE",
                    "MAP",
                    "PWRIT",
                    "GO TO",
                    "GOTO",
                    "IS FOR",
                )
            ):
                continue

            hits.append((index, reason, line.rstrip()))
            break

    return hits


def risk_hits(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    out: dict[str, list[tuple[int, str]]] = {term: [] for term in RISK_TERMS}

    for index, line in enumerate(lines, start=1):
        upper = line.upper()

        for term in RISK_TERMS:
            if term in upper:
                out[term].append((index, line.rstrip()))

    return out


def compact_context_around_hits(lines: list[str], hits: list[tuple[int, str, str]]) -> list[str]:
    out: list[str] = []

    for hit_no, (line_number, reason, _) in enumerate(hits[:8], start=1):
        out.append(f"#### G hit {hit_no}: line {line_number}, reason: {reason}")
        out.append("")
        out.append("```fortran")

        for number, source in line_window(lines, line_number):
            marker = ">>" if number == line_number else "  "
            out.append(f"{marker} {number:6d}: {source}")

        out.append("```")
        out.append("")

    return out


def branch_decision_text(g_hits: list[tuple[int, str, str]], risks: dict[str, list[tuple[int, str]]]) -> str:
    present_risks = [term for term, hits in risks.items() if hits]

    if not g_hits:
        return (
            "No reliable local `plchhq.f` source window for `G` was detected. "
            "`G` must remain guarded until complete source context is located."
        )

    if any(term in present_risks for term in ("SIZE", "IMAP", "MAP", "ADDRESS", "COORD")):
        return (
            "`G` has local source context, but the surrounding source/report contains "
            "coordinate or address-unit risk terms. Do not implement `G` until the "
            "full branch is manually mapped against `SIZE`, `IMAP`, coordinate, and "
            "PCGETR-visible state semantics."
        )

    return (
        "`G` has local source context and no automatic coordinate/address-unit risk "
        "flag in this report. It may be reviewed for implementation, but only after "
        "manual source mapping of the complete branch."
    )


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    lines = text.splitlines()

    g_hits = relevant_g_hits(lines)
    risks = risk_hits(lines)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc: list[str] = []
    doc.append("# NCL Plotchar `G` Command Source Map")
    doc.append("")
    doc.append("This report is generated from the local NCL source tree.")
    doc.append("")
    doc.append(f"- `NCL_SRC_ROOT`: `{root}`")
    doc.append(f"- `plchhq.f`: `{plchhq}`")
    doc.append("")
    doc.append("## Current decision")
    doc.append("")
    doc.append(branch_decision_text(g_hits, risks))
    doc.append("")
    doc.append("## Why this stage does not implement `G`")
    doc.append("")
    doc.append(
        "The previous candidate report flagged `G` as potentially involving "
        "address-unit `SIZE` semantics. Current Python Plotchar mainline is still "
        "limited to TextItem measurement calls with `0 < SIZE < 1`, `IMAP == 0`, "
        "`ANGD == 360.0`, and `CNTR == -1.0`."
    )
    doc.append("")
    doc.append(
        "Therefore `G` must remain guarded until the complete NCL branch is mapped "
        "to Python state transitions, glyph position effects, metrics effects, and "
        "PCGETR-visible state."
    )
    doc.append("")
    doc.append("## `G` source windows")
    doc.append("")

    if g_hits:
        doc.extend(compact_context_around_hits(lines, g_hits))
    else:
        doc.append("No relevant local `plchhq.f` source window was detected for `G`.")
        doc.append("")

    doc.append("## Risk keyword hits in `plchhq.f`")
    doc.append("")

    for term in RISK_TERMS:
        hits = risks.get(term, [])
        doc.append(f"### `{term}`")
        doc.append("")

        if not hits:
            doc.append("No hits.")
            doc.append("")
            continue

        for line_number, source in hits[:12]:
            doc.append(f"- line {line_number}: `{source.strip()}`")

        doc.append("")

    doc.append("## Implementation checklist before `G` can move out of guarded state")
    doc.append("")
    doc.append("- Identify the exact `G` branch entry and exit labels in `plchhq.f`.")
    doc.append("- Determine whether `G` reads integers through `PCGTDI` or uses other parser state.")
    doc.append("- Determine whether it changes `SIZE`, coordinate mapping, or address-unit interpretation.")
    doc.append("- Map its effect on `XCEN/YCEN/XRGT/YRGT/XBEG/YBEG/XEND/YEND`.")
    doc.append("- Map its effect on `DL/DR/DB/DT` and `PCGETR` state.")
    doc.append("- Add positive smoke for implemented `G` cases.")
    doc.append("- Keep unsupported `G` subcases guarded.")
    doc.append("")
    doc.append("## Current guard rule")
    doc.append("")
    doc.append(
        "`G` remains unsupported in Python Plotchar mainline. It must raise a "
        "guarded `PlotcharUnsupportedError` until the checklist above is complete."
    )
    doc.append("")

    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT}")
    print("")
    print(branch_decision_text(g_hits, risks))


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
