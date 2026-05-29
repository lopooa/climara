from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_pwritx_provider_backend_status.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_python_plotchar_pwritx_provider_backend_status.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected status document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar PWRITX / Font0 Provider Backend Status",
        "Stable facade",
        "Supported opt-in mechanism",
        "Still guarded",
        "Boundary rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("PWRITX provider backend status missing sections: " + ", ".join(missing))

    print("✅ Python Plotchar PWRITX provider backend status smoke passed")


if __name__ == "__main__":
    main()
