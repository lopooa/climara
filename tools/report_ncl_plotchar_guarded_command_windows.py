from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_guarded_command_windows.md"

IMPLEMENTED_COMMANDS = set("ABCDEFHIKLNPSUVXYZ")
ALL_COMMANDS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GUARDED_COMMANDS = tuple(letter for letter in ALL_COMMANDS if letter not in IMPLEMENTED_COMMANDS)

WINDOW_RADIUS = 24


@dataclass(frozen=True)
class WindowHit:
    command: str
    line_number: int
    reason: str
    window: tuple[tuple[int, str], ...]


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


def window(lines: list[str], line_number: int, radius: int = WINDOW_RADIUS) -> tuple[tuple[int, str], ...]:
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)

    return tuple((index, lines[index - 1].rstrip()) for index in range(start, end + 1))


def command_patterns(letter: str) -> list[tuple[str, re.Pattern[str]]]:
    ordinal = ord(letter)

    return [
        (
            f"{letter} is for",
            re.compile(rf"\b{re.escape(letter)}\s+is\s+for\b", re.IGNORECASE),
        ),
        (
            f"quoted {letter}",
            re.compile(rf"['\"]{re.escape(letter)}['\"]"),
        ),
        (
            f"ICHAR({letter})",
            re.compile(rf"\bICHAR\s*\(\s*['\"]{re.escape(letter)}['\"]\s*\)", re.IGNORECASE),
        ),
        (
            f"CHAR({ordinal})",
            re.compile(rf"\bCHAR\s*\(\s*{ordinal}\s*\)", re.IGNORECASE),
        ),
        (
            f"ASCII {ordinal} near function-code logic",
            re.compile(rf"\b{ordinal}\b"),
        ),
    ]


def line_looks_relevant(line: str, reason: str) -> bool:
    upper = line.upper()

    if "ASCII" in reason:
        return any(
            token in upper
            for token in (
                "NFCC",
                "ICHAR",
                "FUNCTION",
                "COMMAND",
                "PCGTDI",
                "PWRIT",
                "CASE",
                "FONT",
                "SIZE",
                "GOTO",
                "GO TO",
            )
        )

    if "quoted" in reason:
        return any(
            token in upper
            for token in (
                "NFCC",
                "ICHAR",
                "FUNCTION",
                "COMMAND",
                "PCGTDI",
                "PWRIT",
                "CASE",
                "FONT",
                "SIZE",
                "GOTO",
                "GO TO",
                "IS FOR",
            )
        )

    return True


def find_command_windows(text: str) -> dict[str, list[WindowHit]]:
    lines = text.splitlines()
    result: dict[str, list[WindowHit]] = {letter: [] for letter in GUARDED_COMMANDS}

    for letter in GUARDED_COMMANDS:
        seen_lines: set[int] = set()

        for index, line in enumerate(lines, start=1):
            for reason, pattern in command_patterns(letter):
                if not pattern.search(line):
                    continue

                if not line_looks_relevant(line, reason):
                    continue

                if index in seen_lines:
                    continue

                seen_lines.add(index)
                result[letter].append(
                    WindowHit(
                        command=letter,
                        line_number=index,
                        reason=reason,
                        window=window(lines, index),
                    )
                )
                break

    return result


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    windows = find_command_windows(text)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Plotchar Guarded Command Source Windows")
    lines.append("")
    lines.append("This document is generated from the local NCL source tree.")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append(f"- `plchhq.f`: `{rel(plchhq, root)}`")
    lines.append("")
    lines.append("## Current Python implemented command letters")
    lines.append("")
    lines.append("`" + " ".join(sorted(IMPLEMENTED_COMMANDS)) + "`")
    lines.append("")
    lines.append("## Current guarded command letters")
    lines.append("")
    lines.append("`" + " ".join(GUARDED_COMMANDS) + "`")
    lines.append("")
    lines.append("## Source windows")
    lines.append("")

    for letter in GUARDED_COMMANDS:
        hits = windows.get(letter, [])

        lines.append(f"### `{letter}`")
        lines.append("")

        if not hits:
            lines.append("No relevant local `plchhq.f` source window was detected by this report.")
            lines.append("")
            continue

        for hit_number, hit in enumerate(hits[:6], start=1):
            lines.append(f"#### `{letter}` hit {hit_number}: line {hit.line_number}, reason: {hit.reason}")
            lines.append("")
            lines.append("```fortran")

            for line_number, source_line in hit.window:
                marker = ">>" if line_number == hit.line_number else "  "
                lines.append(f"{marker} {line_number:6d}: {source_line}")

            lines.append("```")
            lines.append("")

    lines.append("## Rule for future implementation")
    lines.append("")
    lines.append(
        "A guarded command may only move to the implemented set after its complete "
        "`plchhq.f` branch has been mapped into Python state transitions, geometry "
        "effects, metrics effects, PCGETR-visible state, and smoke coverage."
    )
    lines.append("")
    lines.append(
        "If this report finds no source window for a command, that command remains "
        "guarded until the relevant complete NCL source context is located elsewhere."
    )
    lines.append("")

    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {DOC}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
