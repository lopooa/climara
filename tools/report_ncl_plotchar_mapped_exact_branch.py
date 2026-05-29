from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_mapped_exact_branch_packet.md"

FOCUS = [
    "IMAP",
    "MA",
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
    "DL",
    "DR",
    "DB",
    "DT",
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "XB",
    "XC",
    "XE",
    "YB",
    "YC",
    "YE",
    "PCGETR",
    "PCSETR",
    "PCSETI",
    "CFUX",
    "CFUY",
    "CUFX",
    "CUFY",
    "SET",
    "GETSET",
]

WINDOW_RADIUS = 34


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


def read_text(path: Path) -> str:
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


def labels(lines: list[str]) -> dict[str, tuple[int, str]]:
    out: dict[str, tuple[int, str]] = {}

    for number, line in enumerate(lines, start=1):
        label = fixed_label(line)
        if label:
            out.setdefault(label, (number, line.rstrip()))

    return out


def goto_refs(line: str) -> set[str]:
    refs: set[str] = set()
    upper = line.upper()

    for match in re.finditer(r"\bGO\s*TO\s*\(([^)]*)\)", upper):
        refs.update(re.findall(r"\b\d{1,5}\b", match.group(1)))

    for match in re.finditer(r"\b(?:GO\s*TO|GOTO)\s+(\d{1,5})\b", upper):
        refs.add(match.group(1))

    stripped = upper.strip()

    if stripped.startswith("IF") and "GO TO" not in upper and "GOTO" not in upper and "THEN" not in upper:
        close = stripped.find(")")
        if close >= 0:
            rest = stripped[close + 1:].strip()
            if re.fullmatch(r"\d{1,5}\s*,\s*\d{1,5}\s*,\s*\d{1,5}", rest):
                refs.update(re.findall(r"\b\d{1,5}\b", rest))

    return refs


def focus_lines(lines: list[str]) -> set[int]:
    out: set[int] = set()

    for number, line in enumerate(lines, start=1):
        if is_comment(line):
            continue

        upper = line.upper()

        if "IMAP" in upper:
            out.add(number)
            continue

        if any(term in upper for term in ("CFUX", "CFUY", "CUFX", "CUFY", "GETSET")):
            out.add(number)
            continue

        if any(term in upper for term in ("XPOS", "YPOS", "PCGETR", "PCSETR", "PCSETI")):
            out.add(number)
            continue

    return out


def window(lines: list[str], center: int, radius: int = WINDOW_RADIUS) -> list[tuple[int, str]]:
    start = max(1, center - radius)
    end = min(len(lines), center + radius)
    return [(number, lines[number - 1].rstrip()) for number in range(start, end + 1)]


def expanded_focus_windows(lines: list[str]) -> list[tuple[int, list[tuple[int, str]]]]:
    centers = sorted(focus_lines(lines))
    windows: list[tuple[int, list[tuple[int, str]]]] = []
    used: set[int] = set()

    for center in centers:
        nums = set(range(max(1, center - WINDOW_RADIUS), min(len(lines), center + WINDOW_RADIUS) + 1))

        if center in used:
            continue

        used.update(nums)
        windows.append((center, window(lines, center)))

        if len(windows) >= 14:
            break

    return windows


def nearby_control_lines(lines: list[str]) -> list[tuple[int, str]]:
    centers = focus_lines(lines)
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


def referenced_near_focus(lines: list[str]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}

    for number, line in nearby_control_lines(lines):
        for ref in goto_refs(line):
            out.setdefault(ref, []).append(number)

    return out


def implementation_decision(lines: list[str]) -> tuple[str, bool]:
    text = "\n".join(lines).upper()

    has_imap = "IMAP" in text
    has_coord = all(term in text for term in ("XPOS", "YPOS"))
    has_internal = all(term in text for term in ("XCEN", "YCEN", "XRGT", "YRGT"))
    has_extent = (
        all(term in text for term in ("DL", "DR", "DB", "DT"))
        or all(term in text for term in ("DSTL", "DSTR", "DSTB", "DSTT"))
    )
    has_control = any(term in text for term in ("GO TO", "GOTO", "IF", "CALL"))

    ready = has_imap and has_coord and has_internal and has_extent and has_control

    if ready:
        return (
            "Exact branch packet contains enough automatic evidence for manual implementation planning. "
            "Runtime must still remain guarded until the branch is translated.",
            True,
        )

    missing = []
    if not has_imap:
        missing.append("IMAP")
    if not has_coord:
        missing.append("XPOS/YPOS")
    if not has_internal:
        missing.append("XCEN/YCEN/XRGT/YRGT")
    if not has_extent:
        missing.append("DL/DR/DB/DT or DSTL/DSTR/DSTB/DSTT")
    if not has_control:
        missing.append("control-flow")

    return "Not enough exact branch evidence: " + ", ".join(missing), False


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = read_text(plchhq)
    lines = text.splitlines()

    label_defs = labels(lines)
    refs = referenced_near_focus(lines)
    windows = expanded_focus_windows(lines)
    controls = nearby_control_lines(lines)
    decision, ready = implementation_decision(lines)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc: list[str] = []
    doc.append("# NCL Plotchar Mapped-Coordinate Exact Branch Packet")
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
    doc.append("## Focus windows")
    doc.append("")

    for idx, (center, win) in enumerate(windows, start=1):
        doc.append(f"### Window {idx}: center line {center}")
        doc.append("")
        doc.append("```fortran")
        for number, src in win:
            marker = ">>" if number == center else "  "
            doc.append(f"{marker} {number:6d}: {src}")
        doc.append("```")
        doc.append("")

    doc.append("## Nearby control lines")
    doc.append("")

    if controls:
        for number, src in controls[:220]:
            doc.append(f"- line {number}: `{src.strip()}`")
    else:
        doc.append("No nearby control lines detected.")

    doc.append("")
    doc.append("## Referenced labels near mapped branch")
    doc.append("")

    if refs:
        for ref, source_lines in sorted(refs.items(), key=lambda item: int(item[0])):
            if ref in label_defs:
                line_number, source = label_defs[ref]
                doc.append(
                    f"- `{ref}` referenced at lines {source_lines}; defined at line {line_number}: `{source.strip()}`"
                )
            else:
                doc.append(f"- `{ref}` referenced at lines {source_lines}; definition not found")
    else:
        doc.append("No labels referenced near mapped branch.")

    doc.append("")
    doc.append("## Manual implementation checklist")
    doc.append("")
    doc.append("- Identify whether mapped branch applies before glyph placement, after glyph placement, or only to output state.")
    doc.append("- Map coordinate conversion calls such as `CFUX/CFUY/CUFX/CUFY/GETSET` if present.")
    doc.append("- Map whether `DL/DR/DB/DT` remain in local text coordinates or mapped/user coordinates.")
    doc.append("- Map whether `XB/XC/XE/YB/YC/YE` are transformed before PCGETR exposure.")
    doc.append("- Preserve current `IMAP == 0` behavior exactly.")
    doc.append("- Keep `IMAP != 0` guarded until positive smokes are defined from source semantics.")
    doc.append("")
    doc.append("## Guard rule")
    doc.append("")
    doc.append("This packet does not implement `IMAP != 0`. It only defines the source boundary for the next implementation stage.")
    doc.append("")

    OUT.write_text("\n".join(doc), encoding="utf-8")

    print(f"wrote {OUT}")
    print("")
    print("Mapped exact branch packet:")
    print(decision)
    print(f"Exact branch packet ready: {ready}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
