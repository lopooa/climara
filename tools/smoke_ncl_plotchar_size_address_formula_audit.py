from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_size_address_formula_audit.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_size_address_formula_audit.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar SIZE / Address-Unit Formula Audit",
        "Current decision",
        "Compact target lines",
        "Formula-like lines",
        "Manual mapping checklist",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("SIZE/address formula audit missing sections: " + ", ".join(missing))

    print("✅ NCL Plotchar SIZE/address formula audit smoke passed")


if __name__ == "__main__":
    main()
