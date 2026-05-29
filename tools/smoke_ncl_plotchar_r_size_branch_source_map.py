from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_r_size_branch_source_map.md"


def assert_r_still_guarded() -> None:
    try:
        parse_textitem_plotchar_real_string(
            "~A~A~R~B",
            func_code="~",
            default_font_number=21,
        )
    except PlotcharUnsupportedError as exc:
        assert "got command 'R'" in str(exc), str(exc)
    else:
        raise AssertionError("R command must remain guarded until the SIZE branch is fully mapped")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_r_size_branch_source_map.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar `R` / SIZE Branch Source Map",
        "Current decision",
        "`R` source windows from `plchhq.f`",
        "Checklist before implementing `R`",
        "Guard rule",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "R/SIZE branch source-map report is missing required sections: "
            + ", ".join(missing)
        )

    assert_r_still_guarded()
    print("✅ NCL Plotchar R/SIZE branch source-map smoke passed")


if __name__ == "__main__":
    main()
