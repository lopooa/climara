from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st, body):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{body}"


def compute(body):
    st = state()
    return compute_plchhq_fontcap_text_extent(
        chrs=real_string(st, body),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=0.045,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=Path("/mnt/d/Projects/NCL/common/src/fontcap"),
    )


def width(metrics):
    return metrics.dl + metrics.dr


def main():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    principal = compute("ABC")
    indexical = compute(f"A{code}I{code}BC")
    cartographic = compute(f"A{code}K{code}BC")
    restored = compute(f"A{code}I{code}BC{code}P{code}DE")

    print("principal text:", principal.text, principal.metrics)
    print("indexical text:", indexical.text, indexical.metrics)
    print("cartographic text:", cartographic.text, cartographic.metrics)
    print("restored text:", restored.text, restored.metrics)
    print()

    print("principal width:", width(principal.metrics))
    print("indexical width:", width(indexical.metrics))
    print("cartographic width:", width(cartographic.metrics))
    print("restored width:", width(restored.metrics))

    if not width(cartographic.metrics) < width(indexical.metrics) < width(principal.metrics):
        raise AssertionError(
            "Expected cartographic width < indexical width < principal width"
        )

    if restored.text != "ABCDE":
        raise AssertionError(f"Expected restored text 'ABCDE', got {restored.text!r}")

    print()
    print("✅ P/I/K size-level metrics demo passed")


if __name__ == "__main__":
    main()
