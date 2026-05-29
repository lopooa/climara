from climara.graphics._plotchar_legacy_data_backed_glyph import (
    LegacyDataBackedGlyphProvider,
)
from climara.graphics._plotchar_legacy_data_provider import (
    LegacyDigitizationRecord,
)
from climara.graphics._plotchar_legacy_digitization_trace import (
    trace_legacy_digitization_steps,
)
from climara.graphics._plotchar_legacy_glyph_provider import LegacyGlyphRequest
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class DemoSourceMappedDataProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_pcfrd_indda_idda_source_map.md"

    def __init__(self):
        self.indices = []

    def record_for_inda_index(self, inda_index):
        self.indices.append(int(inda_index))
        return LegacyDigitizationRecord(
            inda_index=int(inda_index),
            raw_inda_value=12345,
            raw_idda_values=(1, 2, 3, 4),
            source_note="demo record only; not decoded as NCL glyph",
        )


class BadDataProvider:
    source_mapped = False
    source_map_reference = ""

    def record_for_inda_index(self, inda_index):
        raise AssertionError("bad provider should not be called")


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


def main():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    steps = trace_legacy_digitization_steps(
        real_string(st, f"A{code}G{code}BC"),
        st,
    )

    print("traced INDA indices:")
    for step in steps:
        print(
            f"  char={step.char!r} font={step.font_family} "
            f"size={step.size_level} case={step.case_mode} INDA={step.inda_index}"
        )

    data_provider = DemoSourceMappedDataProvider()
    glyph_provider = LegacyDataBackedGlyphProvider(
        data_provider=data_provider,
    )

    try:
        glyph_provider.glyph_for_step(
            LegacyGlyphRequest(
                step=steps[1],
                size=0.035,
                angle=360.0,
                cntr=-1.0,
            )
        )
    except PlotcharUnsupportedError as exc:
        print()
        print("data-backed glyph decode guarded:")
        print(exc)
    else:
        raise AssertionError("raw INDA/IDDA decoding should remain guarded")

    if data_provider.indices != [steps[1].inda_index]:
        raise AssertionError("data provider did not receive the expected INDA index")

    bad_glyph_provider = LegacyDataBackedGlyphProvider(
        data_provider=BadDataProvider(),
    )

    try:
        bad_glyph_provider.glyph_for_step(
            LegacyGlyphRequest(
                step=steps[1],
                size=0.035,
                angle=360.0,
                cntr=-1.0,
            )
        )
    except PlotcharUnsupportedError as exc:
        print()
        print("bad data provider guarded:")
        print(exc)
    else:
        raise AssertionError("non-source-mapped data provider should be guarded")

    print()
    print("provider indices:", data_provider.indices)
    print("✅ legacy INDA/IDDA data provider seam demo passed")


if __name__ == "__main__":
    main()
