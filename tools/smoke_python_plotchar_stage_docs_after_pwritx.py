from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STAGE_STATUS = ROOT / "docs" / "python_plotchar_stage_status.md"
ROADMAP = ROOT / "docs" / "python_plotchar_completion_roadmap.md"
FINAL_CLOSURE = ROOT / "docs" / "python_plotchar_final_stage_closure.md"


def require_contains(path: Path, items: list[str]) -> None:
    if not path.exists():
        raise AssertionError(f"Missing expected document: {path}")

    text = path.read_text(encoding="utf-8")
    missing = [item for item in items if item not in text]
    if missing:
        raise AssertionError(f"{path} missing items: " + ", ".join(missing))


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/update_python_plotchar_stage_docs_after_pwritx.py"],
        cwd=ROOT,
        check=True,
    )

    require_contains(
        STAGE_STATUS,
        [
            "PWRITX / font0 / non-fontcap stage addendum",
            "compute_plchhq_with_pwritx_provider",
            "not a full PWRITX/font0 implementation",
        ],
    )

    require_contains(
        ROADMAP,
        [
            "PWRITX branch status update",
            "real PWRITX/font0 metrics are still not implemented",
            "full NCL PLCHHQ parity",
        ],
    )

    require_contains(
        FINAL_CLOSURE,
        [
            "Explicit provider-backed PWRITX/font0/non-fontcap backend seam",
            "compute_plchhq_with_pwritx_provider",
            "Do not present this milestone as complete NCL PLCHHQ parity",
        ],
    )

    print("✅ Python Plotchar stage docs after PWRITX smoke passed")


if __name__ == "__main__":
    main()
