from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_mapped_branch_labels.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_mapped_branch_labels.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "NCL Plotchar Mapped Branch Label / Control-Flow Source Map",
        "Current decision",
        "Focused source windows",
        "All labels in `plchhq.f`",
        "Referenced labels from GO TO / IF lines",
        "Manual mapping checklist",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Mapped branch label report missing required sections: "
            + ", ".join(missing)
        )

    print("✅ NCL Plotchar mapped branch label/control-flow smoke passed")


if __name__ == "__main__":
    main()
