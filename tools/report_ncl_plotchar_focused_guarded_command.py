from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANDIDATES_DOC = ROOT / "docs" / "ncl_plotchar_next_implementation_candidates.md"
WINDOW_DOC = ROOT / "docs" / "ncl_plotchar_guarded_command_windows.md"
OUT_DOC = ROOT / "docs" / "ncl_plotchar_next_guarded_command_focus.md"

IMPLEMENTED_COMMANDS = set("ABCDEFHIKLNPSUVXYZ")
ALL_COMMANDS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GUARDED_COMMANDS = tuple(letter for letter in ALL_COMMANDS if letter not in IMPLEMENTED_COMMANDS)

WINDOW_RADIUS = 42

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
    "PCGETR",
    "PCSETR",
    "PCSETI",
    "FONT",
    "QUALITY",
]


@dataclass(frozen=True)
class Candidate:
    command: str
    status: str
    source_windows: int
    score: int
    risk_flags: str


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


def parse_candidates() -> list[Candidate]:
    if not CANDIDATES_DOC.exists():
        raise SystemExit(
            f"Missing {CANDIDATES_DOC}. Run tools/report_ncl_plotchar_next_implementation_candidates.py first."
        )

    text = CANDIDATES_DOC.read_text(encoding="utf-8")
    sections = re.findall(
        r"^### `([A-Z])`\n\n(.*?)(?=^### `[A-Z]`\n\n|^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    candidates: list[Candidate] = []

    for command, body in sections:
        if command not in GUARDED_COMMANDS:
            continue

        status_match = re.search(r"^- Status:\s*(.+)$", body, flags=re.MULTILINE)
        windows_match = re.search(r"^- Source windows:\s*(-?\d+)$", body, flags=re.MULTILINE)
        score_match = re.search(r"^- Score:\s*(-?\d+)$", body, flags=re.MULTILINE)
        risk_match = re.search(r"^- Risk flags:\s*(.+)$", body, flags=re.MULTILINE)

        candidates.append(
            Candidate(
                command=command,
                status=status_match.group(1).strip() if status_match else "unknown",
                source_windows=int(windows_match.group(1)) if windows_match else 0,
                score=int(score_match.group(1)) if score_match else -999,
                risk_flags=risk_match.group(1).strip() if risk_match else "unknown",
            )
        )

    if not candidates:
        raise SystemExit("No guarded command candidates were parsed from the candidate report.")

    return candidates


def already_focused(command: str) -> bool:
    specific = ROOT / "docs" / f"ncl_plotchar_{command.lower()}_command_source_map.md"
    if specific.exists():
        return True

    if OUT_DOC.exists():
        text = OUT_DOC.read_text(encoding="utf-8")
        if f"Target command: `{command}`" in text:
            return True

    return False


def select_target(candidates: list[Candidate]) -> Candidate:
    forced = os.environ.get("CLIMARA_PLOTCHAR_COMMAND", "").strip().upper()

    if forced:
        if forced not in GUARDED_COMMANDS:
            raise SystemExit(
                f"CLIMARA_PLOTCHAR_COMMAND={forced!r} is not a current guarded command."
            )

        for candidate in candidates:
            if candidate.command == forced:
                return candidate

        return Candidate(
            command=forced,
            status="forced",
            source_windows=0,
            score=0,
            risk_flags="unknown",
        )

    fresh = [candidate for candidate in candidates if not already_focused(candidate.command)]

    if not fresh:
        fresh = candidates

    low_risk = [
        candidate
        for candidate in fresh
        if candidate.source_windows > 0
        and candidate.score > 0
        and candidate.risk_flags == "none"
        and "no source window" not in candidate.status.lower()
    ]

    if low_risk:
        return sorted(low_risk, key=lambda item: (-item.score, item.command))[0]

    with_windows = [
        candidate
        for candidate in fresh
        if candidate.source_windows > 0
        and candidate.score > 0
        and "no source window" not in candidate.status.lower()
    ]

    if with_windows:
        return sorted(with_windows, key=lambda item: (-item.score, item.command))[0]

    return sorted(fresh, key=lambda item: (-item.score, item.command))[0]


def command_patterns(letter: str) -> list[tuple[str, re.Pattern[str]]]:
    ordinal = ord(letter)
    return [
        (f"{letter} is for", re.compile(rf"\b{re.escape(letter)}\s+is\s+for\b", re.IGNORECASE)),
        (f"quoted {letter}", re.compile(rf"['\"]{re.escape(letter)}['\"]")),
        (f"ICHAR({letter})", re.compile(rf"\bICHAR\s*\(\s*['\"]{re.escape(letter)}['\"]\s*\)", re.IGNORECASE)),
        (f"ASCII {ordinal} near function-code logic", re.compile(rf"\b{ordinal}\b")),
    ]


def relevant_line(line: str, reason: str) -> bool:
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
                "PWRIT",
                "GO TO",
                "GOTO",
                "IS FOR",
                "FONT",
                "QUALITY",
            )
        )

    return True


def source_windows_for_command(lines: list[str], command: str) -> list[tuple[int, str, list[tuple[int, str]]]]:
    hits: list[tuple[int, str, list[tuple[int, str]]]] = []
    seen: set[int] = set()

    for index, line in enumerate(lines, start=1):
        for reason, pattern in command_patterns(command):
            if not pattern.search(line):
                continue

            if not relevant_line(line, reason):
                continue

            if index in seen:
                continue

            seen.add(index)
            start = max(1, index - WINDOW_RADIUS)
            end = min(len(lines), index + WINDOW_RADIUS)
            window = [(line_no, lines[line_no - 1].rstrip()) for line_no in range(start, end + 1)]
            hits.append((index, reason, window))
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


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    source = safe_read(plchhq)
    source_lines = source.splitlines()

    candidates = parse_candidates()
    target = select_target(candidates)
    windows = source_windows_for_command(source_lines, target.command)
    risks = risk_hits(source_lines)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Plotchar Focused Guarded Command Source Map")
    lines.append("")
    lines.append(f"- Target command: `{target.command}`")
    lines.append(f"- Candidate status: {target.status}")
    lines.append(f"- Candidate source windows: {target.source_windows}")
    lines.append(f"- Candidate score: {target.score}")
    lines.append(f"- Candidate risk flags: {target.risk_flags}")
    lines.append(f"- `plchhq.f`: `{plchhq}`")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")

    if target.risk_flags != "none":
        lines.append(
            f"`{target.command}` remains guarded. Candidate risk flags are present: "
            f"{target.risk_flags}. Do not implement until the full branch is manually mapped."
        )
    elif not windows:
        lines.append(
            f"`{target.command}` remains guarded. No reliable local `plchhq.f` source "
            "window was detected by the focused report."
        )
    else:
        lines.append(
            f"`{target.command}` has source windows and no automatic risk flag in the "
            "candidate report. It is eligible for manual source review, but not yet "
            "implemented in this stage."
        )

    lines.append("")
    lines.append("## Source windows")
    lines.append("")

    if not windows:
        lines.append("No focused source windows were detected.")
        lines.append("")
    else:
        for hit_no, (line_number, reason, window) in enumerate(windows[:8], start=1):
            lines.append(f"### `{target.command}` hit {hit_no}: line {line_number}, reason: {reason}")
            lines.append("")
            lines.append("```fortran")

            for number, source_line in window:
                marker = ">>" if number == line_number else "  "
                lines.append(f"{marker} {number:6d}: {source_line}")

            lines.append("```")
            lines.append("")

    lines.append("## Risk keyword summary in `plchhq.f`")
    lines.append("")

    for term in RISK_TERMS:
        hits = risks.get(term, [])
        lines.append(f"### `{term}`")
        lines.append("")

        if not hits:
            lines.append("No hits.")
            lines.append("")
            continue

        for line_number, source_line in hits[:10]:
            lines.append(f"- line {line_number}: `{source_line.strip()}`")

        lines.append("")

    lines.append("## Checklist before implementation")
    lines.append("")
    lines.append(f"- Identify the exact `{target.command}` branch entry and exit labels.")
    lines.append("- Determine whether the branch calls `PCGTDI` or uses another parser path.")
    lines.append("- Determine whether it changes font, size, quality, coordinate mapping, or address-unit semantics.")
    lines.append("- Map effects on `XCEN/YCEN/XRGT/YRGT/XBEG/YBEG/XEND/YEND`.")
    lines.append("- Map effects on `DL/DR/DB/DT` and PCGETR-visible state.")
    lines.append("- Add positive smoke for supported cases.")
    lines.append("- Add guarded smoke for unsupported subcases.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        f"`{target.command}` remains unsupported until the checklist is complete. "
        "It must raise `PlotcharUnsupportedError` rather than being ignored or treated as a glyph."
    )
    lines.append("")

    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_DOC}")
    print("")
    print(f"Focused target command: {target.command}")
    print(f"Candidate risk flags: {target.risk_flags}")
    print(f"Candidate score: {target.score}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
