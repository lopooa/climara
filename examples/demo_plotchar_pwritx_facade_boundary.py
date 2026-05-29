from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_nonfontcap import PwritxNonFontcapResult
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics.pwritx_plotchar import (
    PwritxMetricsProvider,
    build_pwritx_provider_backend_config,
    compute_plchhq_with_pwritx_provider,
)


class DemoSourceMappedPwritxProvider(PwritxMetricsProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def __init__(self):
        self.calls = []

    def metrics_for_request(self, request):
        self.calls.append(request)
        return PwritxNonFontcapResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.10,
                dr=0.30,
                db=0.05,
                dt=0.08,
            ),
            state=request.state,
            text="PWRITX",
            font_number=0,
            glyph_count=6,
        )


class BadPwritxProvider(PwritxMetricsProvider):
    pass


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
    out.pcseti("MA", 0)
    return out


def real_string(st, text):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def main():
    provider = DemoSourceMappedPwritxProvider()
    config = build_pwritx_provider_backend_config(metrics_provider=provider)

    st = state()

    result = compute_plchhq_with_pwritx_provider(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        config=config,
        fontcap_dir=None,
    )

    print("provider calls:", len(provider.calls))
    print("result text:", result.text)
    print("result font_number:", result.font_number)
    print("result glyph_count:", result.glyph_count)
    print("result metrics:", result.metrics)

    if not provider.calls:
        raise AssertionError("PWRITX provider was not called")

    if result.text != "PWRITX":
        raise AssertionError("Unexpected PWRITX provider result text")

    if result.font_number != 0:
        raise AssertionError("PWRITX provider result should represent font0 branch")

    try:
        build_pwritx_provider_backend_config(metrics_provider=BadPwritxProvider())
    except PlotcharUnsupportedError as exc:
        print("bad provider guarded:", exc)
    else:
        raise AssertionError("Non-source-mapped PWRITX provider should be guarded")

    print("✅ PWRITX provider facade boundary demo passed")


if __name__ == "__main__":
    main()
