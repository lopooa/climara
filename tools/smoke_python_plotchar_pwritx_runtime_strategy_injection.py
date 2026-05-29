from __future__ import annotations

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_nonfontcap import (
    PwritxNonFontcapResult,
    build_pwritx_nonfontcap_request,
    compute_pwritx_nonfontcap_extent,
)
from climara.graphics._plotchar_pwritx_runtime_strategy import PwritxRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState


class FakePwritxRuntimeStrategy(PwritxRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"

    def __init__(self):
        self.calls = []

    def compute(self, request):
        self.calls.append(request)
        return PwritxNonFontcapResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.51,
                dr=0.52,
                db=0.53,
                dt=0.54,
            ),
            state=request.state,
            text="ABC",
            font_number=0,
            glyph_count=3,
        )


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
    out.pcseti("MA", 0)
    return out


def main() -> None:
    strategy = FakePwritxRuntimeStrategy()
    request = build_pwritx_nonfontcap_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        runtime_strategy=strategy,
    )

    result = compute_pwritx_nonfontcap_extent(request)

    assert strategy.calls, "PWRITX runtime strategy was not called"
    assert strategy.calls[0] is request
    assert result.text == "ABC"
    assert result.font_number == 0
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.51
    assert result.metrics.dr == 0.52
    assert result.metrics.db == 0.53
    assert result.metrics.dt == 0.54

    print("✅ Python Plotchar PWRITX runtime strategy injection smoke passed")


if __name__ == "__main__":
    main()
