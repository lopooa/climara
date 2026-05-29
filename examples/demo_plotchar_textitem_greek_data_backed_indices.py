from climara.graphics._plotchar_legacy_data_backed_glyph import (
    LegacyDataBackedGlyphProvider,
)
from climara.graphics._plotchar_legacy_data_provider import LegacyDigitizationRecord
from climara.graphics._plotchar_legacy_digitization import (
    ASCII_TO_DPC_INDEX,
    IFGR,
    IFRO,
    ICSU,
    ISZP,
)
from climara.graphics._plotchar_legacy_glyph_provider import (
    LegacyGlyphPolyline,
    LegacyGlyphResult,
)
from climara.graphics._plotchar_legacy_trace_draw import LegacyTraceDrawProvider
from climara.graphics._plotchar_state import PlotcharState
from climara.graphics._plotchar_svg_runtime import render_text_semantics_to_ndc_polylines


class RecordingDataProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_pcfrd_indda_idda_source_map.md"

    def __init__(self):
        self.indices = []

    def record_for_inda_index(self, inda_index):
        self.indices.append(int(inda_index))
        return LegacyDigitizationRecord(
            inda_index=int(inda_index),
            raw_inda_value=1000 + int(inda_index),
            raw_idda_values=(10, 20, 30, 40),
            source_note="demo record only",
        )


class RecordingDecoder:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_idda_parcel_decoder_source_map.md"

    def __init__(self):
        self.steps = []

    def decode_record(self, request):
        self.steps.append(request.step)

        width = 0.020
        height = 0.035

        return LegacyGlyphResult(
            polylines=(
                LegacyGlyphPolyline(
                    points=(
                        (0.0, 0.0),
                        (width, 0.0),
                        (width, height),
                        (0.0, height),
                        (0.0, 0.0),
                    )
                ),
            ),
            advance=width * 1.25,
            dl=0.0,
            dr=width,
            db=0.0,
            dt=height,
        )


def expected_roman(char):
    return IFRO + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord(char)]


def expected_greek(char):
    return IFGR + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord(char)]


def main():
    data_provider = RecordingDataProvider()
    decoder = RecordingDecoder()

    glyph_provider = LegacyDataBackedGlyphProvider(
        data_provider=data_provider,
        glyph_decoder=decoder,
    )

    greek_provider = LegacyTraceDrawProvider(
        glyph_provider=glyph_provider,
    )

    result = render_text_semantics_to_ndc_polylines(
        text="A~G~BC~R~D",
        x=0.1,
        y=0.5,
        just="CenterLeft",
        func_code="~",
        font=21,
        font_height=0.05,
        greek_draw_provider=greek_provider,
    )

    expected = [
        expected_roman("A"),
        expected_greek("B"),
        expected_greek("C"),
        expected_roman("D"),
    ]

    print("expected INDA:", expected)
    print("actual INDA:  ", data_provider.indices)

    print()
    print("decoded steps:")
    for step in decoder.steps:
        print(
            f"  char={step.char!r} "
            f"font={step.font_family} "
            f"size={step.size_level} "
            f"case={step.case_mode} "
            f"INDA={step.inda_index}"
        )

    if data_provider.indices != expected:
        raise AssertionError(
            f"INDA sequence mismatch: expected {expected}, got {data_provider.indices}"
        )

    if result.text != "ABCD":
        raise AssertionError(f"Expected result text 'ABCD', got {result.text!r}")

    if result.glyph_count != 4:
        raise AssertionError(f"Expected 4 glyphs, got {result.glyph_count}")

    print()
    print("result metrics:", result.metrics)
    print("result glyph_count:", result.glyph_count)
    print("✅ TextItem Greek data-backed INDA sequence demo passed")


if __name__ == "__main__":
    main()
