
from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_pwritx_nonfontcap import (
    build_pwritx_nonfontcap_guard_message,
    build_pwritx_nonfontcap_request,
    compute_pwritx_nonfontcap_extent,
    pwritx_nonfontcap_boundary,
    pwritx_nonfontcap_report_paths,
    raise_pwritx_nonfontcap_guard,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
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
    boundary = pwritx_nonfontcap_boundary()
    assert boundary.implemented is False
    assert "PWRITX" in boundary.reason

    message = build_pwritx_nonfontcap_guard_message()
    assert "PWRITX/font0/non-fontcap" in message
    assert "ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md" in message

    assert_guarded("PWRITX/font0/non-fontcap", raise_pwritx_nonfontcap_guard)

    request = build_pwritx_nonfontcap_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
    )
    assert request.size == 0.03
    assert_guarded("PWRITX/font0/non-fontcap", lambda: compute_pwritx_nonfontcap_extent(request))

    missing = [path for path in pwritx_nonfontcap_report_paths(ROOT) if not path.exists()]
    if missing:
        raise AssertionError("missing PWRITX/non-fontcap source-map docs: " + ", ".join(str(path) for path in missing))

    print("✅ Python Plotchar PWRITX/non-fontcap boundary smoke passed")


if __name__ == "__main__":
    main()
