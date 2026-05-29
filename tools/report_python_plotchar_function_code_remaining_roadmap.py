from __future__ import annotations

import ast
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_function_code_remaining_roadmap.md"

RUNTIME = ROOT / "src" / "climara" / "graphics" / "_plotchar_function_code.py"
COVERAGE_DOC = ROOT / "docs" / "ncl_plotchar_function_code_coverage.md"
CANDIDATES_DOC = ROOT / "docs" / "ncl_plotchar_next_implementation_candidates.md"
GUARDED_DOC = ROOT / "docs" / "ncl_plotchar_guarded_command_windows.md"

KNOWN_GROUPS = {
    "direction": ["A", "D"],
    "script": ["B", "S", "E", "N"],
    "size-level": ["P", "I", "K"],
    "case": ["U", "L"],
    "carriage-return": ["C"],
    "zoom": ["X", "Y", "Z"],
    "movement": ["H", "V"],
    "font-change": ["F"],
}

HIGH_RISK_TERMS = {
    "G": "may involve address-unit SIZE semantics",
    "R": "may involve address-unit SIZE semantics",
    "Q": "may involve quality / PWRITX / non-fontcap behavior",
    "W": "may involve workstation quality behavior",
    "M": "may involve medium quality behavior",
    "O": "may involve old PWRITX/font0 behavior",
}


def safe_read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def ncl_root() -> Path | None:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        return None
    root = Path(value)
    return root if root.exists() else None


def find_plchhq(root: Path | None) -> Path | None:
    if root is None:
        return None
    hits = sorted(path for path in root.rglob("plchhq.f") if path.is_file())
    return hits[0] if hits else None


def safe_read_any(path: Path | None) -> str:
    if path is None:
        return ""
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            pass
    return ""


def source_texts() -> dict[str, str]:
    root = ncl_root()
    plchhq = find_plchhq(root)
    return {
        "runtime": safe_read(RUNTIME),
        "coverage": safe_read(COVERAGE_DOC),
        "candidates": safe_read(CANDIDATES_DOC),
        "guarded": safe_read(GUARDED_DOC),
        "plchhq": safe_read_any(plchhq),
    }


def detect_implemented(runtime: str) -> set[str]:
    found: set[str] = set()
    upper = runtime.upper()

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        patterns = [
            f"COMMAND == {letter!r}",
            f"COMMAND=={letter!r}",
            f"CMD == {letter!r}",
            f"CMD=={letter!r}",
            f"'{letter}'",
            f'"{letter}"',
        ]

        if any(pattern in upper for pattern in patterns):
            # Avoid claiming implementation from generic strings alone by also requiring
            # function-code parser terms nearby in the file.
            if any(term in upper for term in ("FUNCTION-CODE", "PLOTCHAR", "COMMAND")):
                found.add(letter)

    # The current staged implementation is known by branch groups and smoke names.
    known_from_smokes = set()
    smoke_names = "\n".join(path.name for path in (ROOT / "tools").glob("smoke_python_plotchar_function_code_*.py"))
    for letters in KNOWN_GROUPS.values():
        for letter in letters:
            if letter.lower() in smoke_names.lower() or letter in upper:
                known_from_smokes.add(letter)

    return found | known_from_smokes


def classify_remaining(implemented: set[str]) -> tuple[list[str], list[str], list[str]]:
    all_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    remaining = [letter for letter in all_letters if letter not in implemented]

    high_risk = [letter for letter in remaining if letter in HIGH_RISK_TERMS]
    ordinary_unknown = [letter for letter in remaining if letter not in HIGH_RISK_TERMS]
    return remaining, high_risk, ordinary_unknown


def compact_evidence(letter: str, texts: dict[str, str], limit: int = 24) -> list[str]:
    out = []
    pattern = re.compile(rf"(^.*(?:['\"]{letter}['\"]|COMMAND.*{letter}|{letter}\s+IS\s+FOR|ICHAR\s*\(\s*['\"]{letter}['\"]\s*\)).*$)", re.IGNORECASE | re.MULTILINE)

    for name, text in texts.items():
        if not text:
            continue
        for match in pattern.finditer(text):
            line = match.group(1).strip()
            if line:
                out.append(f"{name}: {line}")
            if len(out) >= limit:
                return out

    return out


def main() -> None:
    texts = source_texts()
    implemented = detect_implemented(texts["runtime"])
    remaining, high_risk, ordinary_unknown = classify_remaining(implemented)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Python Plotchar Remaining Function-Code Roadmap")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This document tracks remaining inline Plotchar function-code commands after the current TextItem/fontcap milestone.")
    lines.append("")
    lines.append("It is not an implementation claim. Unsupported commands remain guarded unless explicitly source-mapped and smoke-tested.")
    lines.append("")
    lines.append("## Current implemented groups")
    lines.append("")
    for group, letters in KNOWN_GROUPS.items():
        status = ", ".join(f"`{letter}`" for letter in letters)
        lines.append(f"- {group}: {status}")
    lines.append("")
    lines.append("## Detected implemented letters")
    lines.append("")
    if implemented:
        lines.append("`" + " ".join(sorted(implemented)) + "`")
    else:
        lines.append("No implemented letters detected from runtime/source smoke names.")
    lines.append("")
    lines.append("## Remaining letters")
    lines.append("")
    lines.append("`" + " ".join(remaining) + "`")
    lines.append("")
    lines.append("## High-risk remaining letters")
    lines.append("")
    if high_risk:
        for letter in high_risk:
            lines.append(f"- `{letter}`: {HIGH_RISK_TERMS[letter]}")
    else:
        lines.append("No high-risk remaining letters detected by this report.")
    lines.append("")
    lines.append("## Other remaining letters needing manual source mapping")
    lines.append("")
    if ordinary_unknown:
        lines.append("`" + " ".join(ordinary_unknown) + "`")
    else:
        lines.append("No ordinary unknown remaining letters detected.")
    lines.append("")
    lines.append("## Evidence snippets for remaining letters")
    lines.append("")
    for letter in remaining:
        lines.append(f"### `{letter}`")
        lines.append("")
        snippets = compact_evidence(letter, texts)
        lines.append("```text")
        if snippets:
            lines.extend(snippets)
        else:
            lines.append("No compact evidence line detected. Manual NCL source search required.")
        lines.append("```")
        lines.append("")
    lines.append("## Recommended next implementation order")
    lines.append("")
    lines.append("1. Do not implement `G` or `R` until SIZE/address-unit formulas are manually mapped.")
    lines.append("2. Do not implement quality-related letters until PWRITX/font0/non-fontcap semantics are manually mapped.")
    lines.append("3. For any remaining ordinary letter, first generate an exact source packet and positive/negative smokes.")
    lines.append("4. Only then add parser/runtime behavior.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append("Remaining commands must stay guarded until the exact NCL branch behavior, state mutation, and metrics effects are source-mapped.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print("Remaining function-code letters:", " ".join(remaining))
    if high_risk:
        print("High-risk letters:", " ".join(high_risk))
    else:
        print("High-risk letters: none")


if __name__ == "__main__":
    main()
