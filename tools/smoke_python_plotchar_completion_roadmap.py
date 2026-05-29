from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_completion_roadmap.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_python_plotchar_completion_roadmap.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected roadmap document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar Completion Roadmap",
        "Honest status",
        "Remaining work for current stage closure",
        "Remaining work for full NCL PLCHHQ parity",
        "Practical answer",
        "Recommended next action",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("completion roadmap missing sections: " + ", ".join(missing))

    print("✅ Python Plotchar completion roadmap smoke passed")


if __name__ == "__main__":
    main()
