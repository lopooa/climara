from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_next_implementation_candidates.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_next_implementation_candidates.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "Current implemented command letters",
        "Current guarded command letters",
        "Recommended next action",
        "Candidate ranking",
        "Implementation rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Next implementation candidate report is missing required sections: "
            + ", ".join(missing)
        )

    print("✅ NCL Plotchar next implementation candidate smoke passed")


if __name__ == "__main__":
    main()
