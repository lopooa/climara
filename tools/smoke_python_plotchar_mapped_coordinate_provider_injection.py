from __future__ import annotations

from climara.graphics import _plotchar_plchhq_extent as extent
from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateResult,
    MappedCoordinateTransformProvider,
)
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_state import PlotcharState


class ProbeProvider(MappedCoordinateTransformProvider):
    pass


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
    provider = ProbeProvider()
    calls = []

    original = extent.compute_mapped_coordinate_extent

    def fake_runtime(request):
        calls.append(request)
        assert request.transform_provider is provider
        return MappedCoordinateResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.11,
                dr=0.12,
                db=0.13,
                dt=0.14,
            ),
            state=request.state,
            text="ABC",
            font_number=21,
            glyph_count=3,
        )

    extent.compute_mapped_coordinate_extent = fake_runtime

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
            mapped_transform_provider=provider,
        )
    finally:
        extent.compute_mapped_coordinate_extent = original

    assert calls, "mapped runtime was not called"
    request = calls[0]
    assert request.snapshot.imap == 1
    assert request.transform_provider is provider

    assert result.text == "ABC"
    assert result.font_number == 21
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.11
    assert result.metrics.dr == 0.12
    assert result.metrics.db == 0.13
    assert result.metrics.dt == 0.14

    # Touch these dataclasses so import/export stays covered.
    assert MappedCoordinatePoint(1.0, 2.0).x == 1.0
    assert MappedCoordinateExtent(1.0, 2.0, 3.0, 4.0).dt == 4.0

    print("✅ Python Plotchar mapped-coordinate provider injection smoke passed")


if __name__ == "__main__":
    main()
