from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_size_address_unit import (
    build_size_address_unit_guard_message,
    build_size_address_unit_request,
    compute_size_address_unit_extent,
    raise_size_address_unit_guard,
    size_address_unit_boundary,
    size_address_unit_report_paths,
    size_address_unit_requested,
    validate_fractional_textitem_size,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main() -> None:
    boundary = size_address_unit_boundary()
    assert boundary.implemented is False
    assert "0 < SIZE < 1" in boundary.reason

    assert size_address_unit_requested(0.03) is False
    assert size_address_unit_requested(1.0) is True
    assert size_address_unit_requested(0.0) is True
    assert size_address_unit_requested(-1.0) is True

    validate_fractional_textitem_size(0.03)
    assert_guarded("SIZE", lambda: validate_fractional_textitem_size(1.0))
    assert_guarded("SIZE", lambda: raise_size_address_unit_guard(1.0))

    message = build_size_address_unit_guard_message(1.0)
    assert "address-unit SIZE is not implemented" in message
    assert "ncl_plotchar_size_address_exact_branch_packet.md" in message

    request = build_size_address_unit_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=1.0,
        angle=360.0,
        cntr=-1.0,
    )
    assert request.size == 1.0
    assert_guarded("SIZE", lambda: compute_size_address_unit_extent(request))

    missing = [path for path in size_address_unit_report_paths(ROOT) if not path.exists()]
    if missing:
        raise AssertionError("missing SIZE/address source-map docs: " + ", ".join(str(path) for path in missing))

    print("✅ Python Plotchar SIZE/address boundary smoke passed")


if __name__ == "__main__":
    main()
