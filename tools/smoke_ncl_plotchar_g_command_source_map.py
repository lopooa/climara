from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_g_command_source_map.md"


def assert_g_still_guarded() -> None:
    try:
        parse_textitem_plotchar_real_string(
            "~A~A~G~B",
            func_code="~",
            default_font_number=21,
        )
    except PlotcharUnsupportedError as exc:
        assert "got command 'G'" in str(exc), str(exc)
    else:
        raise AssertionError("G command must remain guarded until its source branch is fully mapped")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_g_command_source_map.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "NCL Plotchar `G` Command Source Map",
        "Current decision",
        "Why this stage does not implement `G`",
        "Implementation checklist before `G` can move out of guarded state",
        "Current guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "G command source-map report is missing required sections: "
            + ", ".join(missing)
        )

    assert_g_still_guarded()

    print("✅ NCL Plotchar G command source-map smoke passed")


if __name__ == "__main__":
    main()
