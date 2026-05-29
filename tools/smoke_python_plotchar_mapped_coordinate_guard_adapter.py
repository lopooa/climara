from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._plotchar_mapped_coordinate import build_mapped_coordinate_guard_message
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def state_with_imap(value: int) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", value)
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


def main() -> None:
    base = compute(state_with_imap(0))
    assert base.metrics.width > 0.0
    assert base.metrics.height > 0.0

    message = build_mapped_coordinate_guard_message()
    assert "mapped-coordinate branch is not implemented" in message
    assert "IMAP == 0" in message

    try:
        compute(state_with_imap(1))
    except PlotcharUnsupportedError as exc:
        text = str(exc)
        assert "mapped-coordinate branch is not implemented" in text, text
        assert "IMAP == 0" in text, text
        assert "ncl_plotchar_mapped_branch_readiness.md" in text, text
    else:
        raise AssertionError("IMAP != 0 must route through mapped-coordinate guard")

    print("✅ Python Plotchar mapped-coordinate guard adapter smoke passed")


if __name__ == "__main__":
    main()
