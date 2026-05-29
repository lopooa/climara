from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


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
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=Path("/mnt/d/Projects/NCL/common/src/fontcap"),
    )


def main():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    plain = compute("ABC")
    roman = compute(f"A{code}R{code}BC")

    print("plain:", plain.text, plain.metrics)
    print("roman:", roman.text, roman.metrics)

    if plain.text != roman.text:
        raise AssertionError("R Roman command should not change rendered text in Roman subset")

    if plain.metrics != roman.metrics:
        raise AssertionError("R Roman command should preserve metrics in Roman subset")

    try:
        compute(f"A{code}G{code}BC")
    except PlotcharUnsupportedError as exc:
        print("G guarded:", exc)
    else:
        raise AssertionError("G Greek command should remain guarded")

    print("✅ Plotchar R Roman command demo passed")


if __name__ == "__main__":
    main()
