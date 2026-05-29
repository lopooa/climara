from __future__ import annotations

from climara.graphics import _plotchar_plchhq_extent as extent
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_size_address_unit import SizeAddressUnitResult
from climara.graphics._plotchar_state import PlotcharState


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st: PlotcharState) -> str:
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    calls = []
    original = extent.compute_size_address_unit_extent

    def fake_size_runtime(request):
        calls.append(request)
        return SizeAddressUnitResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.31,
                dr=0.32,
                db=0.33,
                dt=0.34,
            ),
            state=request.state,
            text="ABC",
            font_number=21,
            glyph_count=3,
        )

    extent.compute_size_address_unit_extent = fake_size_runtime

    try:
        st = state()
        result = extent.compute_plchhq_fontcap_text_extent(
            chrs=real_string(st),
            state=st,
            xpos=0.5,
            ypos=0.5,
            size=1.0,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=None,
        )
    finally:
        extent.compute_size_address_unit_extent = original

    assert calls, "SIZE/address runtime was not called"
    request = calls[0]
    assert request.size == 1.0

    assert result.text == "ABC"
    assert result.font_number == 21
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.31
    assert result.metrics.dr == 0.32
    assert result.metrics.db == 0.33
    assert result.metrics.dt == 0.34

    print("✅ Python Plotchar SIZE/address result bridge smoke passed")


if __name__ == "__main__":
    main()
