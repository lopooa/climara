from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STAGE_STATUS = ROOT / "docs" / "python_plotchar_stage_status.md"
ROADMAP = ROOT / "docs" / "python_plotchar_completion_roadmap.md"
FINAL_CLOSURE = ROOT / "docs" / "python_plotchar_final_stage_closure.md"


def require_contains(path: Path, items: list[str]) -> None:
    if not path.exists():
        raise AssertionError(f"Missing expected document: {path}")

    text = path.read_text(encoding="utf-8")
    missing = [item for item in items if item not in text]
    if missing:
        raise AssertionError(f"{path} missing items: " + ", ".join(missing))


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/update_python_plotchar_stage_docs_after_function_code_roadmap.py"],
        cwd=ROOT,
        check=True,
    )

    require_contains(
        STAGE_STATUS,
        [
            "Remaining function-code roadmap addendum",
            "python_plotchar_function_code_remaining_roadmap.md",
            "Remaining commands must stay guarded",
        ],
    )

    require_contains(
        ROADMAP,
        [
            "Remaining function-code roadmap status update",
            "Do not implement `G` or `R` before SIZE/address-unit formulas are manually mapped.",
            "first generate an exact source packet",
        ],
    )

    require_contains(
        FINAL_CLOSURE,
        [
            "Function-code roadmap closure addendum",
            "does not implement new commands",
            "unsupported commands",
        ],
    )

    print("✅ Python Plotchar stage docs after function-code roadmap smoke passed")


if __name__ == "__main__":
    main()
