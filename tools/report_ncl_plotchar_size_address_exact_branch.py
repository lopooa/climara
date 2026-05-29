from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_size_address_exact_branch_packet.md"

FOCUS_TERMS = [
    "SIZE",
    "ISIZ",
    "RSIZ",
    "PCGTDI",
    "PCGETR",
    "PCSETR",
    "PCSETI",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "DL",
    "DR",
    "DB",
    "DT",
    "XPOS",
    "YPOS",
    "XCEN",
    "YCEN",
    "XRGT",
    "YRGT",
    "G",
    "R",
    "ADDRESS",
    "FRACTIONAL",
]

WINDOW_RADIUS = 36


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running.")

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


def is_comment(line: str) -> bool:
    return not line or line[0] in {"c", "C", "*", "!"}


def fixed_label(line: str) -> str | None:
    if is_comment(line):
        return None

    field = line[:5]
    stripped = field.strip()

    if stripped and stripped.isdigit():
        return stripped

    return None


def command_letter_relevant(line: str, letter: str) -> bool:
    upper = line.upper()
    patterns = [
        rf"\b{letter}\s+IS\s+FOR\b",
        rf"['\"]{letter}['\"]",
        rf"\bICHAR\s*\(\s*['\"]{letter}['\"]\s*\)",
        rf"\b{ord(letter)}\b",
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
            "ADDRESS",
            "GOTO",
            "GO TO",
        )
    )


def focus_lines(lines: list[str]) -> set[int]:
    out: set[int] = set()

    for number, line in enumerate(lines, start=1):
        if is_comment(line):
            continue

        upper = line.upper()

        for term in FOCUS_TERMS:
            if term in {"G", "R"}:
                if command_letter_relevant(line, term):
                    out.add(number)
                continue

            if term in upper:
                out.add(number)

    return out


def window(lines: list[str], center: int) -> list[tuple[int, str]]:
    start = max(1, center - WINDOW_RADIUS)
    end = min(len(lines), center + WINDOW_RADIUS)
    return [(number, lines[number - 1].rstrip()) for number in range(start, end + 1)]


def compact_windows(lines: list[str], centers: set[int]) -> list[tuple[int, list[tuple[int, str]]]]:
    out: list[tuple[int, list[tuple[int, str]]]] = []
    used: set[int] = set()

    for center in sorted(centers):
        if center in used:
            continue

        nums = set(range(max(1, center - WINDOW_RADIUS), min(len(lines), center + WINDOW_RADIUS) + 1))
        used.update(nums)
        out.append((center, window(lines, center)))

        if len(out) >= 16:
            break

    return out


def nearby_control(lines: list[str], centers: set[int]) -> list[tuple[int, str]]:
    neighborhood: set[int] = set()

    for center in centers:
        neighborhood.update(range(max(1, center - WINDOW_RADIUS), min(len(lines), center + WINDOW_RADIUS) + 1))

    out: list[tuple[int, str]] = []

    for number in sorted(neighborhood):
        line = lines[number - 1]
        upper = line.upper()

        if (
            "GO TO" in upper
            or "GOTO" in upper
            or upper.strip().startswith("IF")
            or "CALL " in upper
            or "RETURN" in upper
            or "CONTINUE" in upper
        ):
            out.append((number, line.rstrip()))

    return out


def has_terms(text: str, terms: tuple[str, ...]) -> bool:
    upper = text.upper()
    return all(term in upper for term in terms)


def implementation_readiness(source: str) -> tuple[bool, str]:
    checks = {
        "SIZE": has_terms(source, ("SIZE",)),
        "PCGTDI/command parsing": "PCGTDI" in source.upper(),
        "position state": has_terms(source, ("XPOS", "YPOS")),
        "center/right state": has_terms(source, ("XCEN", "YCEN", "XRGT", "YRGT")),
        "extent aliases": (
            has_terms(source, ("DL", "DR", "DB", "DT"))
            or has_terms(source, ("DSTL", "DSTR", "DSTB", "DSTT"))
        ),
        "control flow": any(term in source.upper() for term in ("GO TO", "GOTO", "IF", "CALL")),
    }

    missing = [name for name, ok in checks.items() if not ok]

    if missing:
        return False, "Not ready for implementation planning: missing " + ", ".join(missing)

    return (
        True,
        "Potentially ready for manual SIZE/address-unit implementation planning. "
        "This is not a runtime implementation claim.",
    )


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    lines = text.splitlines()

    centers = focus_lines(lines)
    windows = compact_windows(lines, centers)
    controls = nearby_control(lines, centers)
    ready, decision = implementation_readiness(text)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc: list[str] = []
    doc.append("# NCL Plotchar SIZE / Address-Unit Exact Branch Packet")
    doc.append("")
    doc.append(f"- `NCL_SRC_ROOT`: `{root}`")
    doc.append(f"- `plchhq.f`: `{plchhq}`")
    doc.append("")
    doc.append("## Decision")
    doc.append("")
    doc.append(decision)
    doc.append("")
    doc.append(f"- Exact branch packet ready: `{ready}`")
    doc.append("")
    doc.append("## Current Python boundary")
    doc.append("")
    doc.append(
        "Current Python Plotchar mainline supports the TextItem fractional-size subset "
        "`0 < SIZE < 1`. Address-unit `SIZE <= 0` and `SIZE >= 1` remain guarded."
    )
    doc.append("")
    doc.append("## Focus terms")
    doc.append("")
    doc.append("`" + " ".join(FOCUS_TERMS) + "`")
    doc.append("")
    doc.append("## Focus windows")
    doc.append("")

    for index, (center, win) in enumerate(windows, start=1):
        doc.append(f"### Window {index}: center line {center}")
        doc.append("")
        doc.append("```fortran")
        for number, source in win:
            marker = ">>" if number == center else "  "
            doc.append(f"{marker} {number:6d}: {source}")
        doc.append("```")
        doc.append("")

    doc.append("## Nearby control lines")
    doc.append("")

    if controls:
        for number, source in controls[:240]:
            doc.append(f"- line {number}: `{source.strip()}`")
    else:
        doc.append("No nearby control lines detected.")

    doc.append("")
    doc.append("## Manual implementation checklist")
    doc.append("")
    doc.append("- Determine exact NCL meaning of `SIZE <= 0`, `0 < SIZE < 1`, and `SIZE >= 1`.")
    doc.append("- Determine whether address-unit `SIZE` changes glyph geometry scale only or also coordinate state.")
    doc.append("- Determine whether `G` and `R` commands alter `SIZE`, address units, or parser state.")
    doc.append("- Map effects on `XCEN/YCEN/XRGT/YRGT/XBEG/YBEG/XEND/YEND`.")
    doc.append("- Map effects on `DSTL/DSTR/DSTB/DSTT` and PCGETR-visible `DL/DR/DB/DT`.")
    doc.append("- Preserve current fractional `0 < SIZE < 1` behavior exactly.")
    doc.append("- Keep unsupported subcases guarded.")
    doc.append("")
    doc.append("## Guard rule")
    doc.append("")
    doc.append(
        "This packet does not implement address-unit SIZE. It only defines the source boundary "
        "for the next Python runtime stage."
    )
    doc.append("")

    OUT.write_text("\n".join(doc), encoding="utf-8")

    print(f"wrote {OUT}")
    print("")
    print("SIZE/address exact branch packet:")
    print(decision)
    print(f"Exact branch packet ready: {ready}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
