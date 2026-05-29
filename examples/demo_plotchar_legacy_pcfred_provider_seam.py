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
from climara.graphics._plotchar_legacy_idda_decoder import LegacyIddaGlyphDecoder
from climara.graphics._plotchar_legacy_pcfred_provider import LegacyPcfredDataProvider
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class DemoSourceMappedPcfredBackend:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_pcfred_source_map.md"

    def __init__(self):
        self.requests = []

    def read_record(self, request):
        self.requests.append(request)

        return LegacyDigitizationRecord(
            inda_index=int(request.inda_index),
            raw_inda_value=10000 + int(request.inda_index),
            raw_idda_values=(11, 22, 33, 44),
            source_note="demo PCFRED record only; not decoded NCL glyph data",
        )


class BadPcfredBackend:
    source_mapped = False
    source_map_reference = ""

    def read_record(self, request):
        raise AssertionError("bad backend should not be called")


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

    no_backend_provider = LegacyPcfredDataProvider()

    try:
        no_backend_provider.record_for_inda_index(step.inda_index)
    except PlotcharUnsupportedError as exc:
        print()
        print("missing PCFRED backend guarded:")
        print(exc)
    else:
        raise AssertionError("missing PCFRED backend should be guarded")

    bad_backend_provider = LegacyPcfredDataProvider(
        backend=BadPcfredBackend(),
    )

    try:
        bad_backend_provider.record_for_inda_index(step.inda_index)
    except PlotcharUnsupportedError as exc:
        print()
        print("bad PCFRED backend guarded:")
        print(exc)
    else:
        raise AssertionError("non-source-mapped PCFRED backend should be guarded")

    backend = DemoSourceMappedPcfredBackend()
    decoder = DemoSourceMappedIddaDecoder()

    pcfred_provider = LegacyPcfredDataProvider(
        backend=backend,
    )

    glyph_provider = LegacyDataBackedGlyphProvider(
        data_provider=pcfred_provider,
        glyph_decoder=decoder,
    )

    result = glyph_provider.glyph_for_step(
        LegacyGlyphRequest(
            step=step,
            size=0.035,
            angle=360.0,
            cntr=-1.0,
        )
    )

    if len(backend.requests) != 1:
        raise AssertionError("PCFRED backend should be called exactly once")

    if len(decoder.requests) != 1:
        raise AssertionError("IDDA decoder should be called exactly once")

    if result.advance <= 0.0:
        raise AssertionError("decoded demo glyph should have positive advance")

    print()
    print("PCFRED request INDA:", backend.requests[0].inda_index)
    print("decoder record raw_inda_value:", decoder.requests[0].record.raw_inda_value)
    print("demo glyph advance:", result.advance)
    print("✅ legacy PCFRED provider seam demo passed")


if __name__ == "__main__":
    main()
