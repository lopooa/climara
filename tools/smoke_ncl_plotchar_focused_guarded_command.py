from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_next_guarded_command_focus.md"


def target_command() -> str:
    text = DOC.read_text(encoding="utf-8")
    match = re.search(r"Target command: `([A-Z])`", text)
    if not match:
        raise AssertionError("Focused command report does not contain a target command.")

    return match.group(1)


def assert_target_still_guarded(command: str) -> None:
    try:
        parse_textitem_plotchar_real_string(
            f"~A~A~{command}~B",
            func_code="~",
            default_font_number=21,
        )
    except PlotcharUnsupportedError as exc:
        assert f"got command '{command}'" in str(exc), str(exc)
    else:
        raise AssertionError(
            f"Focused command {command!r} must remain guarded until implementation is complete."
        )


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_focused_guarded_command.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "Target command:",
        "Current decision",
        "Source windows",
        "Checklist before implementation",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Focused guarded command report is missing required sections: "
            + ", ".join(missing)
        )

    assert_target_still_guarded(target_command())

    print("✅ NCL Plotchar focused guarded command smoke passed")


if __name__ == "__main__":
    main()
