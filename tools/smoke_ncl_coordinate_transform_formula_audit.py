from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_coordinate_transform_formula_audit.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_coordinate_transform_formula_audit.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Coordinate Transform Formula Audit",
        "Direction readiness excerpt",
        "Formula-like source lines",
        "Python implementation boundary",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("Formula audit report missing sections: " + ", ".join(missing))

    print("✅ NCL coordinate-transform formula audit smoke passed")


if __name__ == "__main__":
    main()
