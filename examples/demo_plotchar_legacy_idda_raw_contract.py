from climara.graphics._plotchar_legacy_data_backed_glyph import (
    LegacyDataBackedGlyphProvider,
)
from climara.graphics._plotchar_legacy_data_provider import LegacyDigitizationRecord
from climara.graphics._plotchar_legacy_digitization_trace import (
    trace_legacy_digitization_steps,
)
from climara.graphics._plotchar_legacy_glyph_provider import (
    LegacyGlyphPolyline,
    LegacyGlyphRequest,
    LegacyGlyphResult,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class DataProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_pcfrd_indda_idda_source_map.md"

    def __init__(self, record):
        self.record = record

    def record_for_inda_index(self, inda_index):
        return self.record


class Decoder:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_idda_parcel_decoder_source_map.md"

    def decode_record(self, request):
        return LegacyGlyphResult(
            polylines=(
                LegacyGlyphPolyline(
                    points=((0.0, 0.0), (0.02, 0.04), (0.04, 0.0)),
                ),
            ),
            advance=0.05,
            dl=0.0,
            dr=0.04,
            db=0.0,
            dt=0.04,
        )


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


def first_greek_step():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    steps = trace_legacy_digitization_steps(
        real_string(st, f"A{code}G{code}BC"),
        st,
    )

    for step in steps:
        if step.font_family == "greek":
            return step

    raise AssertionError("No Greek step found")


def expect_guard(label, record, step):
    provider = LegacyDataBackedGlyphProvider(
        data_provider=DataProvider(record),
        glyph_decoder=Decoder(),
    )

    try:
        provider.glyph_for_step(
            LegacyGlyphRequest(
                step=step,
                size=0.035,
                angle=360.0,
                cntr=-1.0,
            )
        )
    except PlotcharUnsupportedError as exc:
        print(f"{label} guarded:")
        print(f"  {exc}")
        return

    raise AssertionError(f"{label} should have been guarded")


def main():
    step = first_greek_step()

    good_record = LegacyDigitizationRecord(
        inda_index=step.inda_index,
        raw_inda_value=123,
        raw_idda_values=(1, 2, 3),
        source_note="demo valid raw contract",
    )

    provider = LegacyDataBackedGlyphProvider(
        data_provider=DataProvider(good_record),
        glyph_decoder=Decoder(),
    )

    result = provider.glyph_for_step(
        LegacyGlyphRequest(
            step=step,
            size=0.035,
            angle=360.0,
            cntr=-1.0,
        )
    )

    if result.advance <= 0.0:
        raise AssertionError("valid raw contract should reach decoder")

    expect_guard(
        "missing raw_inda_value",
        LegacyDigitizationRecord(
            inda_index=step.inda_index,
            raw_inda_value=None,
            raw_idda_values=(1, 2, 3),
        ),
        step,
    )

    expect_guard(
        "empty raw_idda_values",
        LegacyDigitizationRecord(
            inda_index=step.inda_index,
            raw_inda_value=123,
            raw_idda_values=(),
        ),
        step,
    )

    expect_guard(
        "wrong INDA index",
        LegacyDigitizationRecord(
            inda_index=step.inda_index + 1,
            raw_inda_value=123,
            raw_idda_values=(1, 2, 3),
        ),
        step,
    )

    expect_guard(
        "non-int IDDA value",
        LegacyDigitizationRecord(
            inda_index=step.inda_index,
            raw_inda_value=123,
            raw_idda_values=(1, "bad", 3),
        ),
        step,
    )

    print()
    print("valid demo glyph advance:", result.advance)
    print("✅ legacy IDDA raw contract demo passed")


if __name__ == "__main__":
    main()
