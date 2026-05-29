from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._plotchar_mapped_coordinate import (
    build_mapped_coordinate_guard_message,
    mapped_coordinate_boundary,
    mapped_coordinate_report_paths,
    raise_mapped_coordinate_guard,
)
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


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def assert_runtime_still_guarded() -> None:
    state = mapped_state()

    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(state),
            state=state,
            xpos=0.5,
            ypos=0.5,
            size=0.03,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
        )
    except PlotcharUnsupportedError as exc:
        assert "IMAP == 0" in str(exc), str(exc)
    else:
        raise AssertionError("IMAP != 0 must remain guarded until mapped branch runtime is implemented")


def assert_boundary_module() -> None:
    boundary = mapped_coordinate_boundary()
    assert boundary.implemented is False
    assert "IMAP != 0 must remain guarded" in boundary.reason

    message = build_mapped_coordinate_guard_message()
    assert "mapped-coordinate branch is not implemented" in message
    assert "IMAP == 0" in message

    for path in mapped_coordinate_report_paths(ROOT):
        assert path.exists(), f"missing mapped-coordinate source-map document: {path}"

    try:
        raise_mapped_coordinate_guard()
    except PlotcharUnsupportedError as exc:
        assert "mapped-coordinate branch is not implemented" in str(exc)
    else:
        raise AssertionError("raise_mapped_coordinate_guard() did not raise")


def main() -> None:
    assert_boundary_module()
    assert_runtime_still_guarded()

    print("✅ Python Plotchar mapped-coordinate implementation-boundary smoke passed")


if __name__ == "__main__":
    main()
