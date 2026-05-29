from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def state_with_ma(value: int) -> PlotcharState:
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


def assert_source_handoff_exists() -> None:
    source = (ROOT / "src" / "climara" / "graphics" / "_plotchar_plchhq_extent.py").read_text(encoding="utf-8")
    assert "build_mapped_coordinate_request" in source
    assert "compute_mapped_coordinate_extent(request)" in source
    assert "mapped_coordinate_requested(state)" in source


def main() -> None:
    assert_source_handoff_exists()

    unmapped = compute(state_with_ma(0))
    assert unmapped.metrics.width > 0.0
    assert unmapped.metrics.height > 0.0

    try:
        compute(state_with_ma(1))
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert "mapped-coordinate branch is not implemented" in message, message
        assert "Required source-map documents" in message, message
    else:
        raise AssertionError("IMAP != 0 unexpectedly bypassed mapped-coordinate runtime handoff")

    print("✅ Python Plotchar mapped-coordinate runtime handoff smoke passed")


if __name__ == "__main__":
    main()
