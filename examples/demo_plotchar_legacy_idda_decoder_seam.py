from climara.graphics._plotchar_legacy_data_backed_glyph import (
    LegacyDataBackedGlyphProvider,
)
from climara.graphics._plotchar_legacy_data_provider import (
    LegacyDigitizationRecord,
)
from climara.graphics._plotchar_legacy_digitization_trace import (
    trace_legacy_digitization_steps,
)
from climara.graphics._plotchar_legacy_glyph_provider import (
    LegacyGlyphPolyline,
    LegacyGlyphRequest,
    LegacyGlyphResult,
)
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
            raw_inda_value=321,
            raw_idda_values=(10, 20, 30, 40),
            source_note="demo raw parcel record only",
        )


class DemoSourceMappedIddaDecoder:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_idda_parcel_decoder_source_map.md"

    def __init__(self):
        self.requests = []

    def decode_record(self, request):
        self.requests.append(request)

        width = 0.035
        height = 0.055

        return LegacyGlyphResult(
            polylines=(
                LegacyGlyphPolyline(
                    points=(
                        (0.0, 0.0),
                        (width * 0.5, height),
                        (width, 0.0),
                    )
                ),
            ),
            advance=width * 1.25,
            dl=0.0,
            dr=width,
            db=0.0,
            dt=height,
        )


class BadIddaDecoder:
    source_mapped = False
    source_map_reference = ""

    def decode_record(self, request):
        raise AssertionError("bad decoder should not be called")


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


def main():
    step = first_greek_step()

    print(
        f"selected step: char={step.char!r} font={step.font_family} "
        f"size={step.size_level} case={step.case_mode} INDA={step.inda_index}"
    )

    data_provider = DemoSourceMappedDataProvider()

    no_decoder_provider = LegacyDataBackedGlyphProvider(
        data_provider=data_provider,
    )

    try:
        no_decoder_provider.glyph_for_step(
            LegacyGlyphRequest(
                step=step,
                size=0.035,
                angle=360.0,
                cntr=-1.0,
            )
        )
    except PlotcharUnsupportedError as exc:
        print()
        print("no decoder guarded:")
        print(exc)
    else:
        raise AssertionError("missing IDDA decoder should remain guarded")

    bad_decoder_provider = LegacyDataBackedGlyphProvider(
        data_provider=data_provider,
        glyph_decoder=BadIddaDecoder(),
    )

    try:
        bad_decoder_provider.glyph_for_step(
            LegacyGlyphRequest(
                step=step,
                size=0.035,
                angle=360.0,
                cntr=-1.0,
            )
        )
    except PlotcharUnsupportedError as exc:
        print()
        print("bad decoder guarded:")
        print(exc)
    else:
        raise AssertionError("non-source-mapped decoder should remain guarded")

    decoder = DemoSourceMappedIddaDecoder()
    good_provider = LegacyDataBackedGlyphProvider(
        data_provider=data_provider,
        glyph_decoder=decoder,
    )

    result = good_provider.glyph_for_step(
        LegacyGlyphRequest(
            step=step,
            size=0.035,
            angle=360.0,
            cntr=-1.0,
        )
    )

    if not data_provider.indices:
        raise AssertionError("data provider was not called")

    if not decoder.requests:
        raise AssertionError("decoder was not called")

    if result.advance <= 0.0:
        raise AssertionError("decoded demo glyph should have positive advance")

    print()
    print("data provider indices:", data_provider.indices)
    print("decoder request count:", len(decoder.requests))
    print("demo glyph advance:", result.advance)
    print("demo glyph polylines:", len(result.polylines))
    print("✅ legacy IDDA decoder seam demo passed")


if __name__ == "__main__":
    main()
