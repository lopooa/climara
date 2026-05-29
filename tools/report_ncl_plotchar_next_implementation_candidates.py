from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

WINDOW_DOC = ROOT / "docs" / "ncl_plotchar_guarded_command_windows.md"
COVERAGE_DOC = ROOT / "docs" / "ncl_plotchar_function_code_coverage.md"
BRANCH_DOC = ROOT / "docs" / "ncl_plotchar_remaining_branch_source_map.md"
OUT_DOC = ROOT / "docs" / "ncl_plotchar_next_implementation_candidates.md"

IMPLEMENTED_COMMANDS = set("ABCDEFHIKLNPSUVXYZ")
GUARDED_COMMANDS = tuple(letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letter not in IMPLEMENTED_COMMANDS)

HIGH_RISK_TERMS = {
    "PWRIT": "likely tied to PWRITX/non-fontcap branch",
    "PWRITX": "likely tied to PWRITX/non-fontcap branch",
    "PWRITY": "likely tied to PWRITX/non-fontcap branch",
    "IMAP": "likely tied to mapped-coordinate branch",
    "MAP": "may involve mapped-coordinate branch",
    "SIZE": "may involve address-unit SIZE semantics",
    "IQUF": "may involve quality branch",
    "WORKSTATION": "may involve workstation quality branch",
}

USEFUL_SOURCE_TERMS = {
    " IS FOR ": 8,
    "PCGTDI": 6,
    "GO TO": 3,
    "GOTO": 3,
    "NFCC": 2,
    "ICHAR": 2,
    "COMMAND": 2,
}


@dataclass(frozen=True)
class Candidate:
    command: str
    windows: int
    score: int
    risk_notes: tuple[str, ...]
    has_no_source_window: bool
    excerpt: str


def require_docs() -> None:
    missing = [path for path in (WINDOW_DOC, COVERAGE_DOC, BRANCH_DOC) if not path.exists()]

    if missing:
        raise SystemExit(
            "Missing source-map documents. Run the previous Plotchar source-map smokes first:\n"
            + "\n".join(str(path) for path in missing)
        )


def section_for_command(text: str, command: str) -> str:
    pattern = re.compile(
        rf"^### `{re.escape(command)}`\n\n(.*?)(?=^### `[A-Z]`\n\n|^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return ""

    return match.group(1)


def score_section(command: str, section: str) -> Candidate:
    has_no_window = "No relevant local `plchhq.f` source window was detected" in section
    windows = len(re.findall(rf"^#### `{re.escape(command)}` hit", section, flags=re.MULTILINE))

    upper = section.upper()
    score = windows * 10

    for term, value in USEFUL_SOURCE_TERMS.items():
        score += upper.count(term) * value

    risk_notes: list[str] = []

    for term, note in HIGH_RISK_TERMS.items():
        if term in upper and note not in risk_notes:
            risk_notes.append(note)
            score -= 5

    if has_no_window:
        score = -100

    excerpt_lines = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("####") or stripped.startswith(">>") or " IS FOR " in stripped.upper():
            excerpt_lines.append(stripped)

        if len(excerpt_lines) >= 10:
            break

    excerpt = "\n".join(excerpt_lines) if excerpt_lines else "No compact excerpt."

    return Candidate(
        command=command,
        windows=windows,
        score=score,
        risk_notes=tuple(risk_notes),
        has_no_source_window=has_no_window,
        excerpt=excerpt,
    )


def candidate_ranking() -> list[Candidate]:
    require_docs()
    text = WINDOW_DOC.read_text(encoding="utf-8")

    candidates = [
        score_section(command, section_for_command(text, command))
        for command in GUARDED_COMMANDS
    ]

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.has_no_source_window,
            -candidate.score,
            candidate.command,
        ),
    )


def recommended_action(candidates: list[Candidate]) -> str:
    viable = [
        candidate
        for candidate in candidates
        if not candidate.has_no_source_window and candidate.score > 0
    ]

    if not viable:
        return (
            "No guarded command has enough automatically detected local source context. "
            "Keep all remaining command letters guarded and inspect the full NCL source manually."
        )

    low_risk = [candidate for candidate in viable if not candidate.risk_notes]

    if low_risk:
        best = low_risk[0]
        return (
            f"Recommended next command for manual source-aligned implementation: `{best.command}`. "
            "It has detected PLCHHQ source windows and no automatic high-risk branch flags."
        )

    best = viable[0]
    return (
        f"Recommended next review target: `{best.command}`, but it has risk flags: "
        + "; ".join(best.risk_notes)
        + ". Do not implement until the linked branch is manually source-mapped."
    )


def write_report() -> None:
    candidates = candidate_ranking()
    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Plotchar Next Implementation Candidates")
    lines.append("")
    lines.append("This report is generated from local source-map documents.")
    lines.append("")
    lines.append("## Current implemented command letters")
    lines.append("")
    lines.append("`" + " ".join(sorted(IMPLEMENTED_COMMANDS)) + "`")
    lines.append("")
    lines.append("## Current guarded command letters")
    lines.append("")
    lines.append("`" + " ".join(GUARDED_COMMANDS) + "`")
    lines.append("")
    lines.append("## Recommended next action")
    lines.append("")
    lines.append(recommended_action(candidates))
    lines.append("")
    lines.append("## Candidate ranking")
    lines.append("")

    for candidate in candidates:
        status = "no source window" if candidate.has_no_source_window else "source-window detected"
        risk = "; ".join(candidate.risk_notes) if candidate.risk_notes else "none"

        lines.append(f"### `{candidate.command}`")
        lines.append("")
        lines.append(f"- Status: {status}")
        lines.append(f"- Source windows: {candidate.windows}")
        lines.append(f"- Score: {candidate.score}")
        lines.append(f"- Risk flags: {risk}")
        lines.append("")
        lines.append("Excerpt:")
        lines.append("")
        lines.append("```text")
        lines.append(candidate.excerpt)
        lines.append("```")
        lines.append("")

    lines.append("## Implementation rule")
    lines.append("")
    lines.append(
        "Do not implement a candidate merely because it has a high score. "
        "Before changing `src/climara`, inspect the complete source window and map "
        "state transitions, glyph-position effects, metrics effects, PCGETR-visible "
        "state, and guarded unsupported cases."
    )
    lines.append("")

    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_DOC}")

    print("")
    print("Recommended next action:")
    print(recommended_action(candidates))


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
