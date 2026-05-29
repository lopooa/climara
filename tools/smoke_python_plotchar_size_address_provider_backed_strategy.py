from __future__ import annotations

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_size_address_provider import SizeAddressScaleProvider
from climara.graphics._plotchar_size_address_unit import SizeAddressUnitResult
from climara.graphics._plotchar_size_runtime_strategy import ProviderBackedSizeAddressRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState


class SourceMappedScaleProvider(SizeAddressScaleProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_size_address_formula_audit.md"

    def __init__(self):
        self.fractional_calls = []
        self.result_calls = []

    def fractional_core_size(self, request) -> float:
        self.fractional_calls.append(request)
        return 0.03

    def result_from_core(self, *, request, core_result) -> SizeAddressUnitResult:
        self.result_calls.append((request, core_result))
        return SizeAddressUnitResult(
            metrics=build_plotchar_extent_metrics(
                dl=core_result.metrics.dl * 10.0,
                dr=core_result.metrics.dr * 10.0,
                db=core_result.metrics.db * 10.0,
                dt=core_result.metrics.dt * 10.0,
            ),
            state=core_result.state,
            text=core_result.text,
            font_number=core_result.font_number,
            glyph_count=core_result.glyph_count,
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
    provider = SourceMappedScaleProvider()
    strategy = ProviderBackedSizeAddressRuntimeStrategy()

    sized = compute_plchhq_fontcap_text_extent(
        chrs=real_string(st),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=1.0,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=None,
        size_address_runtime_strategy=strategy,
        size_address_scale_provider=provider,
    )

    core_state = state()
    core = compute_plchhq_fontcap_text_extent(
        chrs=real_string(core_state),
        state=core_state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=None,
    )

    assert provider.fractional_calls, "provider fractional_core_size was not called"
    assert provider.result_calls, "provider result_from_core was not called"

    request = provider.fractional_calls[0]
    assert request.size == 1.0
    assert request.scale_provider is provider
    assert request.runtime_strategy is strategy

    assert sized.text == core.text
    assert sized.font_number == core.font_number
    assert sized.glyph_count == core.glyph_count
    assert sized.metrics.dl == core.metrics.dl * 10.0
    assert sized.metrics.dr == core.metrics.dr * 10.0
    assert sized.metrics.db == core.metrics.db * 10.0
    assert sized.metrics.dt == core.metrics.dt * 10.0

    print("✅ Python Plotchar provider-backed SIZE/address strategy smoke passed")


if __name__ == "__main__":
    main()
