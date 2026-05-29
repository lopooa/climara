from __future__ import annotations

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_nonfontcap import (
    PwritxNonFontcapResult,
    build_pwritx_nonfontcap_request,
    compute_pwritx_nonfontcap_extent,
)
from climara.graphics._plotchar_pwritx_provider import PwritxMetricsProvider
from climara.graphics._plotchar_pwritx_runtime_strategy import ProviderBackedPwritxRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState


class SourceMappedProvider(PwritxMetricsProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def __init__(self):
        self.calls = []

    def metrics_for_request(self, request):
        self.calls.append(request)
        return PwritxNonFontcapResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.61,
                dr=0.62,
                db=0.63,
                dt=0.64,
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
    provider = SourceMappedProvider()
    strategy = ProviderBackedPwritxRuntimeStrategy()
    request = build_pwritx_nonfontcap_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        runtime_strategy=strategy,
        metrics_provider=provider,
    )

    result = compute_pwritx_nonfontcap_extent(request)

    assert provider.calls, "PWRITX metrics provider was not called"
    assert provider.calls[0] is request
    assert request.metrics_provider is provider
    assert request.runtime_strategy is strategy
    assert result.text == "ABC"
    assert result.font_number == 0
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.61
    assert result.metrics.dr == 0.62
    assert result.metrics.db == 0.63
    assert result.metrics.dt == 0.64

    print("✅ Python Plotchar provider-backed PWRITX strategy smoke passed")


if __name__ == "__main__":
    main()
