from __future__ import annotations

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_size_address_unit import SizeAddressUnitResult
from climara.graphics._plotchar_size_runtime_strategy import SizeAddressRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState


class FakeSizeAddressRuntimeStrategy(SizeAddressRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_size_address_exact_branch_packet.md"

    def __init__(self):
        self.calls = []

    def compute(self, request):
        self.calls.append(request)
        return SizeAddressUnitResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.41,
                dr=0.42,
                db=0.43,
                dt=0.44,
            ),
            state=request.state,
            text="ABC",
            font_number=21,
            glyph_count=3,
        )


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
    st = state()
    strategy = FakeSizeAddressRuntimeStrategy()

    result = compute_plchhq_fontcap_text_extent(
        chrs=real_string(st),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=1.0,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=None,
        size_address_runtime_strategy=strategy,
    )

    assert strategy.calls, "SIZE/address runtime strategy was not called"
    request = strategy.calls[0]
    assert request.size == 1.0
    assert request.runtime_strategy is strategy

    assert result.text == "ABC"
    assert result.font_number == 21
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.41
    assert result.metrics.dr == 0.42
    assert result.metrics.db == 0.43
    assert result.metrics.dt == 0.44

    print("✅ Python Plotchar SIZE/address runtime strategy injection smoke passed")


if __name__ == "__main__":
    main()
