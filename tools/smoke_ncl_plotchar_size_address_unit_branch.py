from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_size_address_unit_branch_source_map.md"


def assert_command_guarded(command: str) -> None:
    try:
        parse_textitem_plotchar_real_string(
            f"~A~A~{command}~B",
            func_code="~",
            default_font_number=21,
        )
    except PlotcharUnsupportedError as exc:
        assert f"got command '{command}'" in str(exc), str(exc)
    else:
        raise AssertionError(f"{command} must remain guarded until SIZE/address branch is mapped")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_size_address_unit_branch.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "NCL Plotchar SIZE / Address-Unit Branch Source Map",
        "Current decision",
        "Current supported measurement contract remains",
        "Keyword source windows",
        "Checklist before implementation",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "SIZE/address-unit branch source-map report is missing required sections: "
            + ", ".join(missing)
        )

    assert_command_guarded("G")
    assert_command_guarded("R")

    print("✅ NCL Plotchar SIZE/address-unit branch source-map smoke passed")


if __name__ == "__main__":
    main()
