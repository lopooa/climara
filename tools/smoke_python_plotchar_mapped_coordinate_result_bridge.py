from __future__ import annotations

from climara.graphics import _plotchar_plchhq_extent as extent
from climara.graphics._plotchar_mapped_coordinate import MappedCoordinateResult
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_state import PlotcharState


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


def main() -> None:
    state = mapped_state()
    calls = []

    original = extent.compute_mapped_coordinate_extent

    def fake_mapped_runtime(request):
        calls.append(request)
        return MappedCoordinateResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.01,
                dr=0.02,
                db=0.03,
                dt=0.04,
            ),
            state=request.state,
            text="ABC",
            font_number=21,
            glyph_count=3,
        )

    extent.compute_mapped_coordinate_extent = fake_mapped_runtime

    try:
        result = extent.compute_plchhq_fontcap_text_extent(
            chrs=real_string(state),
            state=state,
            xpos=0.5,
            ypos=0.5,
            size=0.03,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=None,
        )
    finally:
        extent.compute_mapped_coordinate_extent = original

    assert calls, "mapped runtime was not called"
    request = calls[0]
    assert request.snapshot.imap == 1
    assert request.snapshot.size == 0.03

    assert result.text == "ABC"
    assert result.font_number == 21
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.01
    assert result.metrics.dr == 0.02
    assert result.metrics.db == 0.03
    assert result.metrics.dt == 0.04

    print("✅ Python Plotchar mapped-coordinate result bridge smoke passed")


if __name__ == "__main__":
    main()
