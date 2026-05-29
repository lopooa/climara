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

    cases = [
        ("plain", "abc ABC", "abc ABC"),
        ("upper persistent", f"{code}U{code}abc ABC", "ABC ABC"),
        ("lower persistent", f"{code}L{code}abc ABC", "abc abc"),
        ("counted upper", f"{code}U3{code}abcdef", "ABCdef"),
        ("counted lower", f"{code}L3{code}ABCDEF", "abcDEF"),
    ]

    for label, body, expected in cases:
        result = compute(body)
        print(f"{label}: {result.text!r}")

        if result.text != expected:
            raise AssertionError(
                f"{label} expected {expected!r}, got {result.text!r}"
            )

    try:
        compute(f"A{code}G{code}BC")
    except PlotcharUnsupportedError as exc:
        print("G guarded:", exc)
    else:
        raise AssertionError("G Greek command should remain guarded")

    print("✅ U/L case metrics parser demo passed")


if __name__ == "__main__":
    main()
