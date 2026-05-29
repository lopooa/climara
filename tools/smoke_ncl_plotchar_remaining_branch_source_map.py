from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_remaining_branch_source_map.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_remaining_branches.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected source-map document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "Remaining guarded branches",
        "PWRITX / font-0 / database font branch",
        "mapped-coordinate branch",
        "address-unit SIZE semantics",
        "Keyword hits for remaining branches",
        "Implementation boundary",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Remaining branch source-map document is missing required sections: "
            + ", ".join(missing)
        )

    print("✅ NCL Plotchar remaining branch source-map smoke passed")


if __name__ == "__main__":
    main()
