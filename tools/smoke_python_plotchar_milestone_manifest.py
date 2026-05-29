from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_milestone_manifest.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_python_plotchar_milestone_manifest.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected manifest to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar Milestone Manifest",
        "Milestone scope",
        "Runtime modules",
        "Status documents",
        "Source-map documents",
        "Smoke scripts",
        "Guard policy",
        "not a full NCL PLCHHQ parity claim",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("milestone manifest missing sections: " + ", ".join(missing))

    if "No required milestone artifacts are missing." not in text:
        raise AssertionError("milestone manifest reports missing artifacts; inspect docs/python_plotchar_milestone_manifest.md")

    print("✅ Python Plotchar milestone manifest smoke passed")


if __name__ == "__main__":
    main()
