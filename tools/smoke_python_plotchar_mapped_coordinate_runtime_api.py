from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_mapped_coordinate import (
    build_mapped_coordinate_request,
    compute_mapped_coordinate_extent,
    mapped_coordinate_boundary,
    mapped_coordinate_report_paths,
    mapped_coordinate_requested,
    validate_mapped_coordinate_request,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]


def state_with_ma(value: int) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", value)
    return state


def request_for_state(state: PlotcharState):
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return build_mapped_coordinate_request(
        chrs=f"{code}A{code}ABC",
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=None,
    )


def main() -> None:
    mapped = state_with_ma(1)
    unmapped = state_with_ma(0)

    assert mapped_coordinate_requested(mapped) is True
    assert mapped_coordinate_requested(unmapped) is False

    request = request_for_state(mapped)
    assert request.snapshot.imap == 1
    assert request.snapshot.textitem_mode == 1
    assert request.snapshot.quality_index == 0
    assert request.snapshot.font_number == 21
    assert request.snapshot.size == 0.03

    validate_mapped_coordinate_request(request)

    try:
        compute_mapped_coordinate_extent(request)
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert "mapped-coordinate branch is not implemented" in message
        assert "IMAP == 0" in message
    else:
        raise AssertionError("mapped-coordinate runtime endpoint unexpectedly returned")

    try:
        validate_mapped_coordinate_request(request_for_state(unmapped))
    except PlotcharUnsupportedError as exc:
        assert "IMAP == 0" in str(exc)
    else:
        raise AssertionError("unmapped request unexpectedly entered mapped-coordinate runtime endpoint")

    paths = mapped_coordinate_report_paths(ROOT)
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise AssertionError("missing mapped-coordinate source-map docs: " + ", ".join(str(path) for path in missing))

    assert mapped_coordinate_boundary().implemented is False

    print("✅ Python Plotchar mapped-coordinate runtime API smoke passed")


if __name__ == "__main__":
    main()
