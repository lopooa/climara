from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_milestone_lock.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_python_plotchar_milestone_lock.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected milestone lock document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar Milestone Lock",
        "Locked milestone behavior",
        "Locked smoke entry",
        "Smoke scripts",
        "Public opt-in facades",
        "not a full NCL PLCHHQ parity claim",
        "No locked milestone artifacts are missing.",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("milestone lock document missing sections: " + ", ".join(missing))

    print("✅ Python Plotchar milestone lock smoke passed")


if __name__ == "__main__":
    main()
