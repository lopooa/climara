from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STAGE_STATUS = ROOT / "docs" / "python_plotchar_stage_status.md"
ROADMAP = ROOT / "docs" / "python_plotchar_completion_roadmap.md"
FINAL_CLOSURE = ROOT / "docs" / "python_plotchar_final_stage_closure.md"

REQUIRED_FILES = [
    "docs/python_plotchar_function_code_remaining_roadmap.md",
    "tools/report_python_plotchar_function_code_remaining_roadmap.py",
    "tools/smoke_python_plotchar_function_code_remaining_roadmap.py",
]

STAGE_ADDENDUM = """
## Remaining function-code roadmap addendum

The remaining inline Plotchar function-code commands now have a dedicated roadmap document:

- `docs/python_plotchar_function_code_remaining_roadmap.md`

This document separates:

- currently implemented function-code groups
- remaining letters
- high-risk remaining letters
- recommended implementation order
- guard rules for commands that depend on SIZE/address-unit or PWRITX/font0 behavior

### Boundary rule

Remaining commands must stay guarded until their exact NCL source branch behavior, state mutation, and metrics effects are source-mapped and smoke-tested.
""".strip()

ROADMAP_ADDENDUM = """
## Remaining function-code roadmap status update

A dedicated roadmap now tracks remaining inline Plotchar function-code commands:

- `docs/python_plotchar_function_code_remaining_roadmap.md`

This reduces the risk of accidentally implementing high-risk commands before their dependent branches are mapped.

### Updated next-step policy

- Do not implement `G` or `R` before SIZE/address-unit formulas are manually mapped.
- Do not implement quality-related commands before PWRITX/font0/non-fontcap semantics are manually mapped.
- For any remaining command, first generate an exact source packet and positive/negative smokes.
- Only then add parser/runtime behavior.
""".strip()

FINAL_CLOSURE_ADDENDUM = """
## Function-code roadmap closure addendum

The final stage closure now includes the remaining function-code roadmap as a milestone artifact:

- `docs/python_plotchar_function_code_remaining_roadmap.md`

This artifact does not implement new commands. It locks the guard policy for remaining inline commands and prevents unsupported commands from being treated as completed behavior.
""".strip()


def append_once(path: Path, marker: str, addendum: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing document: {path}")

    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"already updated: {path}")
        return

    if not text.endswith("\n"):
        text += "\n"

    text += "\n" + addendum + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"updated {path}")


def main() -> None:
    missing = [item for item in REQUIRED_FILES if not (ROOT / item).exists()]
    if missing:
        raise SystemExit(
            "Missing required function-code roadmap artifacts:\n" + "\n".join(missing)
        )

    append_once(
        STAGE_STATUS,
        "## Remaining function-code roadmap addendum",
        STAGE_ADDENDUM,
    )
    append_once(
        ROADMAP,
        "## Remaining function-code roadmap status update",
        ROADMAP_ADDENDUM,
    )
    append_once(
        FINAL_CLOSURE,
        "## Function-code roadmap closure addendum",
        FINAL_CLOSURE_ADDENDUM,
    )

    print("Function-code roadmap docs are up to date")


if __name__ == "__main__":
    main()
