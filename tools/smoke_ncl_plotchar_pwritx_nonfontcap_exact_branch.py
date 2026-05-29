
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_pwritx_nonfontcap_exact_branch.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar PWRITX / Font0 / Non-Fontcap Exact Branch Packet",
        "Decision",
        "Current Python boundary",
        "Definition blocks",
        "Focus windows",
        "Manual implementation checklist",
        "Guard rule",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("PWRITX/non-fontcap report missing sections: " + ", ".join(missing))

    print("✅ NCL Plotchar PWRITX/non-fontcap exact branch smoke passed")


if __name__ == "__main__":
    main()
