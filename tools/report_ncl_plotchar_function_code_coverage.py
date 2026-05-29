from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_function_code_coverage.md"

IMPLEMENTED_COMMANDS = {
    "A": "Across direction",
    "B": "Subscript",
    "C": "Carriage return",
    "D": "Down direction",
    "E": "End script",
    "F": "Font change",
    "H": "Horizontal movement",
    "I": "Indexical size",
    "K": "Cartographic size",
    "L": "Lower case",
    "N": "Normal script",
    "P": "Principal size",
    "S": "Superscript",
    "U": "Upper case",
    "V": "Vertical movement",
    "X": "X zoom",
    "Y": "Y zoom",
    "Z": "Z zoom",
}

SPECIAL_IMPLEMENTED = [
    "Doubled function-code signal literal escape",
    "PCGTDI-style signed decimal integer parser",
    "TextItem real_string A/D direction prefix",
]

KNOWN_GUARDED_BRANCHES = [
    "PWRITX / font 0 / database font branch",
    "Medium / Low / Workstation quality branches",
    "mapped-coordinate branch, IMAP != 0",
    "address-unit SIZE semantics",
    "generic PLCHHQ calls outside TextItem measurement contract",
]

ALL_ASCII_COMMAND_LETTERS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


@dataclass(frozen=True)
class CommandHit:
    command: str
    line_number: int
    line: str


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

    # Prefer plotchar source if more than one copy exists.
    for path in hits:
        if "plotchar" in str(path).lower() or "plot" in str(path).lower():
            return path

    return hits[0]


def safe_read(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise SystemExit(f"Could not decode source file: {path}")


def detect_command_hits(text: str) -> dict[str, list[CommandHit]]:
    lines = text.splitlines()
    hits: dict[str, list[CommandHit]] = {letter: [] for letter in ALL_ASCII_COMMAND_LETTERS}

    # This intentionally uses multiple broad source patterns, because historical
    # PLCHHQ Fortran may express function-code branches via comments, ICHAR,
    # NFCC comparisons, GOTOs, or temporary variables.
    patterns_by_letter: dict[str, list[re.Pattern[str]]] = {}

    for letter in ALL_ASCII_COMMAND_LETTERS:
        patterns_by_letter[letter] = [
            re.compile(rf"\b{letter}\s+is\s+for\b", re.IGNORECASE),
            re.compile(rf"['\"]{letter}['\"]"),
            re.compile(rf"\bICHAR\s*\(\s*['\"]{letter}['\"]\s*\)", re.IGNORECASE),
            re.compile(rf"\bCHAR\s*\(\s*{ord(letter)}\s*\)", re.IGNORECASE),
            re.compile(rf"\b{ord(letter)}\b"),
        ]

    for index, line in enumerate(lines, start=1):
        stripped = line.rstrip()

        for letter, patterns in patterns_by_letter.items():
            if any(pattern.search(stripped) for pattern in patterns):
                # Avoid the decimal-code pattern becoming too noisy. Keep decimal
                # matches only when the line also looks like function-code logic.
                if stripped.strip().isdigit():
                    continue

                upper = stripped.upper()
                if (
                    f"{letter} IS FOR" in upper
                    or f"'{letter}'" in upper
                    or f'"{letter}"' in upper
                    or "ICHAR" in upper
                    or "NFCC" in upper
                    or "FUNCTION" in upper
                    or "PCGTDI" in upper
                    or "COMMAND" in upper
                    or "PWRIT" in upper
                    or "CASE" in upper
                ):
                    hits[letter].append(
                        CommandHit(
                            command=letter,
                            line_number=index,
                            line=stripped,
                        )
                    )

    return hits


def source_window(text: str, line_number: int, radius: int = 4) -> list[tuple[int, str]]:
    lines = text.splitlines()
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)

    return [(i, lines[i - 1].rstrip()) for i in range(start, end + 1)]


def format_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    hits = detect_command_hits(text)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    implemented = set(IMPLEMENTED_COMMANDS)
    not_implemented_letters = [
        letter for letter in ALL_ASCII_COMMAND_LETTERS if letter not in implemented
    ]

    lines: list[str] = []
    lines.append("# NCL Plotchar Function-Code Coverage")
    lines.append("")
    lines.append("This document is generated from the local NCL source tree.")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append(f"- `plchhq.f`: `{format_rel(plchhq, root)}`")
    lines.append("")
    lines.append("## Python implemented command subset")
    lines.append("")

    for letter in sorted(IMPLEMENTED_COMMANDS):
        lines.append(f"- `{letter}`: {IMPLEMENTED_COMMANDS[letter]}")

    for item in SPECIAL_IMPLEMENTED:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Guarded command letters")
    lines.append("")
    lines.append(
        "These ASCII uppercase command letters are not implemented in the current "
        "Python Plotchar mainline and must remain guarded unless a future stage maps "
        "their complete PLCHHQ source semantics."
    )
    lines.append("")

    for letter in not_implemented_letters:
        lines.append(f"- `{letter}`")

    lines.append("")
    lines.append("## Guarded non-command branches")
    lines.append("")

    for item in KNOWN_GUARDED_BRANCHES:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Source hits by command letter")
    lines.append("")

    for letter in ALL_ASCII_COMMAND_LETTERS:
        lines.append(f"### `{letter}`")
        lines.append("")

        command_hits = hits[letter][:8]

        if not command_hits:
            lines.append("No source hit found by the current heuristic.")
            lines.append("")
            continue

        for hit in command_hits:
            status = "implemented" if letter in implemented else "guarded"
            lines.append(f"- line {hit.line_number} ({status}): `{hit.line.strip()}`")

        lines.append("")

    lines.append("## Implementation rule")
    lines.append("")
    lines.append(
        "A command letter appearing in this report is not considered implemented "
        "until its PLCHHQ branch has been mapped to Python state transitions, "
        "metrics effects, PCGETR-visible state, and smoke coverage."
    )
    lines.append("")
    lines.append(
        "Unsupported commands must raise guarded errors. They must not be treated "
        "as ordinary glyphs, ignored, or approximated."
    )
    lines.append("")

    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {DOC}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
