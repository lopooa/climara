from __future__ import annotations

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_nonfontcap import PwritxNonFontcapResult
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics.pwritx_plotchar import (
    PwritxMetricsProvider,
    build_pwritx_provider_backend_config,
    compute_plchhq_with_pwritx_provider,
)


class SourceMappedProvider(PwritxMetricsProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def __init__(self):
        self.calls = []

    def metrics_for_request(self, request):
        self.calls.append(request)
        return PwritxNonFontcapResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.71,
                dr=0.72,
                db=0.73,
                dt=0.74,
            ),
            state=request.state,
            text="ABC",
            font_number=0,
            glyph_count=3,
        )


class PlainProvider(PwritxMetricsProvider):
    pass


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
    out.pcseti("MA", 0)
    return out


def real_string(st: PlotcharState) -> str:
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    provider = SourceMappedProvider()
    config = build_pwritx_provider_backend_config(metrics_provider=provider)

    st = state()
    result = compute_plchhq_with_pwritx_provider(
        chrs=real_string(st),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        config=config,
        fontcap_dir=None,
    )

    assert provider.calls, "PWRITX public facade did not call provider"
    request = provider.calls[0]
    assert request.metrics_provider is provider
    assert request.runtime_strategy is not None
    assert result.text == "ABC"
    assert result.font_number == 0
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.71
    assert result.metrics.dr == 0.72
    assert result.metrics.db == 0.73
    assert result.metrics.dt == 0.74

    try:
        build_pwritx_provider_backend_config(metrics_provider=PlainProvider())
    except PlotcharUnsupportedError as exc:
        assert "not source-mapped" in str(exc), str(exc)
    else:
        raise AssertionError("PWRITX public facade accepted non-source-mapped provider")

    print("✅ Python Plotchar PWRITX public facade smoke passed")


if __name__ == "__main__":
    main()
