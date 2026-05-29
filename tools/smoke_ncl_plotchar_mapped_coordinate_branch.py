from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_mapped_coordinate_branch_source_map.md"


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def base_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 0)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def compute(state: PlotcharState):
    return compute_plchhq_fontcap_text_extent(
        chrs=real_string(state),
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected guarded failure containing {message_part!r}")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_mapped_coordinate_branch.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar Mapped-Coordinate Branch Source Map",
        "Current decision",
        "Why this branch is separate",
        "Keyword source windows",
        "Checklist before implementation",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("Mapped-coordinate report missing required sections: " + ", ".join(missing))

    valid = compute(base_state())
    assert valid.metrics.width > 0.0
    assert valid.metrics.height > 0.0

    mapped = base_state()
    mapped.pcseti("MA", 1)
    assert_guarded("IMAP == 0", lambda: compute(mapped))

    print("✅ NCL Plotchar mapped-coordinate branch source-map smoke passed")


if __name__ == "__main__":
    main()
