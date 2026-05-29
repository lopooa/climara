from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_mapped_opt_in_backend_status.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_mapped_opt_in_backend_status.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar Explicit Opt-In Mapped Backend Status",
        "What is supported",
        "What remains guarded",
        "Runtime entry",
        "Boundary rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("mapped opt-in backend status report missing sections: " + ", ".join(missing))

    print("✅ NCL Plotchar mapped opt-in backend status smoke passed")


if __name__ == "__main__":
    main()
