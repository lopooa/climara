from pathlib import Path
from math import isclose

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_size_address_provider import NclSourceMappedSizeAddressScaleProvider
from climara.graphics._plotchar_size_runtime_strategy import ProviderBackedSizeAddressRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState


ADDRESS_RESOLUTION = 1023.0
FRACTIONAL_SIZE = 0.035


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


def equivalent_negative_size(st: PlotcharState, fractional_size: float) -> float:
    return -float(fractional_size) * ADDRESS_RESOLUTION / float(st.wpic[0])


def equivalent_address_size(fractional_size: float) -> float:
    return float(fractional_size) * ADDRESS_RESOLUTION


def compute(size: float):
    st = state()
    provider = NclSourceMappedSizeAddressScaleProvider(
        address_resolution=ADDRESS_RESOLUTION
    )

    return compute_plchhq_fontcap_text_extent(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=size,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=Path("/mnt/d/Projects/NCL/common/src/fontcap"),
        size_address_runtime_strategy=ProviderBackedSizeAddressRuntimeStrategy(),
        size_address_scale_provider=provider,
    ).metrics


def as_tuple(metrics):
    return (metrics.dl, metrics.dr, metrics.db, metrics.dt)


def assert_close(name, got, expected):
    for g, e in zip(as_tuple(got), as_tuple(expected)):
        if not isclose(g, e, rel_tol=1e-10, abs_tol=1e-12):
            raise AssertionError(
                f"{name} differs: got={as_tuple(got)} expected={as_tuple(expected)}"
            )


def main():
    st = state()

    frac = FRACTIONAL_SIZE
    neg = equivalent_negative_size(st, frac)
    addr = equivalent_address_size(frac)

    m_frac = compute(frac)
    m_neg = compute(neg)
    m_addr = compute(addr)

    print(f"WPIC(1): {float(st.wpic[0]):.12f}")
    print(f"fractional SIZE: {frac:.12f}")
    print(f"equivalent SIZE <= 0: {neg:.12f}")
    print(f"equivalent SIZE >= 1: {addr:.12f}")
    print()

    print("fractional:", as_tuple(m_frac))
    print("negative:  ", as_tuple(m_neg))
    print("address:   ", as_tuple(m_addr))

    assert_close("SIZE <= 0 equivalent branch", m_neg, m_frac)
    assert_close("SIZE >= 1 equivalent branch", m_addr, m_frac)

    print()
    print("✅ SIZE/address equivalent metrics match fractional branch")


if __name__ == "__main__":
    main()
