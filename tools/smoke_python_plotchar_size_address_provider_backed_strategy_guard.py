from __future__ import annotations

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_size_address_provider import SizeAddressScaleProvider
from climara.graphics._plotchar_size_runtime_strategy import ProviderBackedSizeAddressRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class PlainProvider(SizeAddressScaleProvider):
    def fractional_core_size(self, request) -> float:
        return 0.03


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

    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(st),
            state=st,
            xpos=0.5,
            ypos=0.5,
            size=1.0,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=None,
            size_address_runtime_strategy=ProviderBackedSizeAddressRuntimeStrategy(),
            size_address_scale_provider=PlainProvider(),
        )
    except PlotcharUnsupportedError as exc:
        assert "not source-mapped" in str(exc), str(exc)
    else:
        raise AssertionError("provider-backed SIZE/address strategy accepted non-source-mapped provider")

    print("✅ Python Plotchar provider-backed SIZE/address strategy guard smoke passed")


if __name__ == "__main__":
    main()
