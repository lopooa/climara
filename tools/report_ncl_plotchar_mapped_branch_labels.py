from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_mapped_branch_labels.md"

FOCUS_TERMS = [
    "IMAP",
    "MAP",
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
    "PCGETR",
    "PCSETR",
    "PCSETI",
    "CUFX",
    "CUFY",
    "CFUX",
    "CFUY",
    "SET",
    "GETSET",
    "FRSTD",
    "VECTOR",
]

WINDOW_RADIUS = 18


@dataclass(frozen=True)
class LabelLine:
    line_number: int
    label: str
    source: str


@dataclass(frozen=True)
class ControlLine:
    line_number: int
    kind: str
    source: str


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


def label_for_line(line: str) -> str | None:
    match = re.match(r"^\s*(\d{1,5})\b", line)
    if not match:
        return None

    # Avoid mistaking numeric constants in continuation text for labels.
    prefix = line[:6]
    if len(prefix) >= 5 and any(ch.isdigit() for ch in prefix):
        return match.group(1)

    return match.group(1)


def extract_labels(lines: list[str]) -> list[LabelLine]:
    out: list[LabelLine] = []

    for index, line in enumerate(lines, start=1):
        label = label_for_line(line)
        if label is None:
            continue

        out.append(LabelLine(index, label, line.rstrip()))

    return out


def extract_control_lines(lines: list[str]) -> list[ControlLine]:
    out: list[ControlLine] = []

    patterns = [
        ("GO TO", re.compile(r"\bGO\s*TO\b|\bGOTO\b", re.IGNORECASE)),
        ("IF", re.compile(r"^\s*IF\s*\(", re.IGNORECASE)),
        ("CALL", re.compile(r"\bCALL\s+[A-Z0-9_]+", re.IGNORECASE)),
        ("RETURN", re.compile(r"\bRETURN\b", re.IGNORECASE)),
        ("CONTINUE", re.compile(r"\bCONTINUE\b", re.IGNORECASE)),
    ]

    for index, line in enumerate(lines, start=1):
        for kind, pattern in patterns:
            if pattern.search(line):
                out.append(ControlLine(index, kind, line.rstrip()))
                break

    return out


def focus_line_numbers(lines: list[str]) -> set[int]:
    out: set[int] = set()

    for index, line in enumerate(lines, start=1):
        upper = line.upper()

        if any(term in upper for term in FOCUS_TERMS):
            out.add(index)

    return out


def nearby_lines(center: int, total: int, radius: int = WINDOW_RADIUS) -> range:
    start = max(1, center - radius)
    end = min(total, center + radius)
    return range(start, end + 1)


def compact_windows(lines: list[str], centers: set[int]) -> list[tuple[int, list[tuple[int, str]]]]:
    windows: list[tuple[int, list[tuple[int, str]]]] = []
    used: set[int] = set()

    for center in sorted(centers):
        if center in used:
            continue

        window_numbers = list(nearby_lines(center, len(lines)))
        used.update(window_numbers)

        windows.append(
            (
                center,
                [(number, lines[number - 1].rstrip()) for number in window_numbers],
            )
        )

        if len(windows) >= 12:
            break

    return windows


def referenced_labels(control_lines: list[ControlLine]) -> set[str]:
    refs: set[str] = set()

    for item in control_lines:
        if item.kind not in {"GO TO", "IF"}:
            continue

        for label in re.findall(r"\b\d{1,5}\b", item.source):
            refs.add(label)

    return refs


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    lines = text.splitlines()

    labels = extract_labels(lines)
    controls = extract_control_lines(lines)
    focuses = focus_line_numbers(lines)

    label_by_value = {}
    for label in labels:
        label_by_value.setdefault(label.label, []).append(label)

    refs = referenced_labels(controls)
    windows = compact_windows(lines, focuses)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc: list[str] = []
    doc.append("# NCL Plotchar Mapped Branch Label / Control-Flow Source Map")
    doc.append("")
    doc.append(f"- `NCL_SRC_ROOT`: `{root}`")
    doc.append(f"- `plchhq.f`: `{plchhq}`")
    doc.append("")
    doc.append("## Current decision")
    doc.append("")
    doc.append(
        "This report does not implement mapped-coordinate behavior. It extracts "
        "Fortran labels, control-flow statements, and focused source windows around "
        "`IMAP/MAP/XPOS/YPOS/PCGETR` terms so the branch can be manually mapped before "
        "any Python changes are made."
    )
    doc.append("")
    doc.append("## Focus terms")
    doc.append("")
    doc.append("`" + " ".join(FOCUS_TERMS) + "`")
    doc.append("")
    doc.append("## Focused source windows")
    doc.append("")

    if not windows:
        doc.append("No focused source windows detected.")
        doc.append("")
    else:
        for idx, (center, window) in enumerate(windows, start=1):
            doc.append(f"### Window {idx}: centered at line {center}")
            doc.append("")
            doc.append("```fortran")

            for number, source in window:
                marker = ">>" if number == center else "  "
                doc.append(f"{marker} {number:6d}: {source}")

            doc.append("```")
            doc.append("")

    doc.append("## All labels in `plchhq.f`")
    doc.append("")
    if not labels:
        doc.append("No Fortran labels detected.")
    else:
        for label in labels:
            doc.append(f"- label `{label.label}` at line {label.line_number}: `{label.source.strip()}`")
    doc.append("")

    doc.append("## Referenced labels from GO TO / IF lines")
    doc.append("")
    if not refs:
        doc.append("No referenced labels detected.")
    else:
        for ref in sorted(refs, key=lambda value: int(value)):
            defs = label_by_value.get(ref, [])
            if defs:
                locations = ", ".join(f"line {item.line_number}" for item in defs)
                doc.append(f"- `{ref}` -> {locations}")
            else:
                doc.append(f"- `{ref}` -> label definition not detected")
    doc.append("")

    doc.append("## Control lines near focus terms")
    doc.append("")
    focus_neighborhood = set()
    for center in focuses:
        focus_neighborhood.update(nearby_lines(center, len(lines), radius=WINDOW_RADIUS))

    near_controls = [item for item in controls if item.line_number in focus_neighborhood]

    if not near_controls:
        doc.append("No nearby control lines detected.")
    else:
        for item in near_controls[:160]:
            doc.append(f"- line {item.line_number} [{item.kind}]: `{item.source.strip()}`")
    doc.append("")

    doc.append("## Manual mapping checklist")
    doc.append("")
    doc.append("- Identify exact branch condition for `IMAP != 0`.")
    doc.append("- Identify all labels entered from mapped-coordinate branch.")
    doc.append("- Identify all labels shared with non-mapped branch.")
    doc.append("- Map coordinate conversions before and after glyph placement.")
    doc.append("- Map whether `DL/DR/DB/DT` remain in the same coordinate space.")
    doc.append("- Map PCGETR-visible values for `XB/XC/XE/YB/YC/YE`.")
    doc.append("- Only after this map is complete, implement positive mapped-coordinate smokes.")
    doc.append("")
    doc.append("## Guard rule")
    doc.append("")
    doc.append(
        "`IMAP != 0` remains guarded. This report is evidence gathering, not implementation."
    )
    doc.append("")

    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
