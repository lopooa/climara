from __future__ import annotations

from climara.graphics._plotchar_mapped_coordinate import (
    dispatch_mapped_coordinate_or_continue,
    mapped_coordinate_boundary,
    mapped_coordinate_requested,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


def state_with_ma(value: int) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", value)
    return state


def main() -> None:
    unmapped = state_with_ma(0)
    mapped = state_with_ma(1)

    assert mapped_coordinate_requested(unmapped) is False
    assert mapped_coordinate_requested(mapped) is True

    dispatch_mapped_coordinate_or_continue(unmapped)

    try:
        dispatch_mapped_coordinate_or_continue(mapped)
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert "mapped-coordinate branch is not implemented" in message
        assert "IMAP == 0" in message
    else:
        raise AssertionError("mapped-coordinate dispatch seam did not guard MA=1")

    boundary = mapped_coordinate_boundary()
    assert boundary.implemented is False

    print("✅ Python Plotchar mapped-coordinate dispatch seam smoke passed")


if __name__ == "__main__":
    main()
