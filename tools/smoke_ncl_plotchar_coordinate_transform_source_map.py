from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_coordinate_transform_source_map.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_coordinate_transform_source_map.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "NCL Coordinate Transform Source Map for Plotchar",
        "Current decision",
        "Keyword source windows",
        "Required mapping checklist",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Coordinate transform source-map report missing sections: "
            + ", ".join(missing)
        )

    print("✅ NCL Plotchar coordinate-transform source-map smoke passed")


if __name__ == "__main__":
    main()
