from climara.graphics._plotchar_legacy_digitization import (
    IFGR,
    IFRO,
    ICSL,
    ICSU,
    ISZC,
    ISZI,
    ISZP,
    ASCII_TO_DPC_INDEX,
)
from climara.graphics._plotchar_legacy_digitization_trace import (
    trace_legacy_digitization_steps,
)
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


def show(label, body):
    st = state()
    steps = trace_legacy_digitization_steps(real_string(st, body), st)

    print()
    print(label)
    print("-" * len(label))

    for step in steps:
        print(
            f"{step.char!r} "
            f"font={step.font_family:5s} "
            f"size={step.size_level:11s} "
            f"case={step.case_mode:5s} "
            f"INDA={step.inda_index}"
        )

    return steps


def main():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    plain = show("plain roman", "ABC")
    greek = show("greek after G", f"A{code}G{code}BC")
    mixed_font = show("G then R", f"A{code}G{code}B{code}R{code}C")
    size_mix = show("P/I/K size mix", f"A{code}I{code}B{code}K{code}C{code}P{code}D")
    case_mix = show("U/L counted case", f"{code}L3{code}ABCDEF")

    assert plain[0].inda_index == IFRO + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord("A")]
    assert greek[1].inda_index == IFGR + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord("B")]
    assert mixed_font[1].font_family == "greek"
    assert mixed_font[2].font_family == "roman"
    assert size_mix[1].inda_index == IFRO + ISZI + ICSU + ASCII_TO_DPC_INDEX[ord("B")]
    assert size_mix[2].inda_index == IFRO + ISZC + ICSU + ASCII_TO_DPC_INDEX[ord("C")]
    assert size_mix[3].inda_index == IFRO + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord("D")]
    assert case_mix[0].inda_index == IFRO + ISZP + ICSL + ASCII_TO_DPC_INDEX[ord("a")]

    try:
        show("unsupported command guard", f"A{code}B{code}C")
    except PlotcharUnsupportedError as exc:
        print()
        print("unsupported command guarded:", exc)
    else:
        raise AssertionError("unsupported command should be guarded in legacy trace stage")

    print()
    print("✅ legacy digitization trace demo passed")


if __name__ == "__main__":
    main()
