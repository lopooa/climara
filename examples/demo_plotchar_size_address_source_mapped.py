from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_size_address_provider import NclSourceMappedSizeAddressScaleProvider
from climara.graphics._plotchar_size_runtime_strategy import ProviderBackedSizeAddressRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st: PlotcharState, text: str) -> str:
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def fontcap_dir() -> Path:
    return Path("/mnt/d/Projects/NCL/common/src/fontcap")


def run_size(size: float, provider=None):
    st = state()

    return compute_plchhq_fontcap_text_extent(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=size,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
        size_address_runtime_strategy=ProviderBackedSizeAddressRuntimeStrategy(),
        size_address_scale_provider=provider,
    )


def main() -> None:
    print("NCL source-mapped SIZE/address provider demo")
    print("Provider branch is explicit opt-in, not default TextItem runtime.")
    print()

    provider = NclSourceMappedSizeAddressScaleProvider(address_resolution=1023.0)

    for size in [0.03, -12.0, 12.0, 128.0]:
        result = run_size(size, provider=provider)
        m = result.metrics
        print(
            f"SIZE={size:8.3f} "
            f"DL={m.dl:.6f} DR={m.dr:.6f} DB={m.db:.6f} DT={m.dt:.6f}"
        )

    try:
        run_size(12.0, provider=None)
    except PlotcharUnsupportedError as exc:
        print()
        print("default without provider remains guarded:")
        print(exc)
    else:
        raise AssertionError("SIZE/address should remain guarded without explicit source-mapped provider")


if __name__ == "__main__":
    main()
