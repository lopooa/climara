from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL or CLIMARA_PLOTCHAR_FONTCAP_DIR")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def base_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 0)
    return state


def real_string_for_state(state: PlotcharState, text: str = "ABC") -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def compute_with_state(
    state: PlotcharState,
    *,
    size: float = 0.03,
    angle: float = 360.0,
    cntr: float = -1.0,
):
    return compute_plchhq_fontcap_text_extent(
        chrs=real_string_for_state(state),
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=size,
        angle=angle,
        cntr=cntr,
        fontcap_dir=fontcap_dir(),
    )


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main():
    valid = compute_with_state(base_state())
    assert valid.metrics.width > 0.0
    assert valid.metrics.height > 0.0

    assert_guarded(
        "SIZE <= 0.0",
        lambda: compute_with_state(base_state(), size=0.0),
    )

    assert_guarded(
        "fractional SIZE < 1.0",
        lambda: compute_with_state(base_state(), size=1.0),
    )

    mapped_state = base_state()
    mapped_state.pcseti("MA", 1)
    assert_guarded(
        "IMAP == 0",
        lambda: compute_with_state(mapped_state),
    )

    not_textitem_state = base_state()
    not_textitem_state.pcseti("TE", 0)
    assert_guarded(
        "PCSETI('TE', 1)",
        lambda: compute_with_state(not_textitem_state),
    )

    assert_guarded(
        "ANGD must be 360.0",
        lambda: compute_with_state(base_state(), angle=0.0),
    )

    assert_guarded(
        "CNTR must be -1.0",
        lambda: compute_with_state(base_state(), cntr=0.0),
    )

    print("✅ Python Plotchar TextItem measurement contract guard smoke passed")


if __name__ == "__main__":
    main()
