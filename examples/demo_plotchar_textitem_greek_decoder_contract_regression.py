from pathlib import Path

from climara.graphics._plotchar_legacy_data_backed_glyph import (
    LegacyDataBackedGlyphProvider,
)
from climara.graphics._plotchar_legacy_data_provider import LegacyDigitizationRecord
from climara.graphics._plotchar_legacy_glyph_provider import (
    LegacyGlyphPolyline,
    LegacyGlyphResult,
)
from climara.graphics._plotchar_legacy_trace_draw import LegacyTraceDrawProvider
from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


class DataProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_pcfrd_indda_idda_source_map.md"

    def __init__(self):
        self.indices = []

    def record_for_inda_index(self, inda_index):
        self.indices.append(int(inda_index))
        return LegacyDigitizationRecord(
            inda_index=int(inda_index),
            raw_inda_value=1000 + int(inda_index),
            raw_idda_values=(1, 2, 3, 4),
            source_note="demo valid record for TextItem regression",
        )


class GoodDecoder:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_idda_parcel_decoder_source_map.md"

    def __init__(self):
        self.steps = []

    def decode_record(self, request):
        self.steps.append(request.step)

        width = 0.032
        height = 0.052

        if request.step.font_family == "greek":
            polylines = (
                LegacyGlyphPolyline(
                    points=(
                        (0.0, 0.0),
                        (width * 0.5, height),
                        (width, 0.0),
                    )
                ),
                LegacyGlyphPolyline(
                    points=(
                        (width * 0.25, height * 0.35),
                        (width * 0.75, height * 0.35),
                    )
                ),
            )
        else:
            polylines = (
                LegacyGlyphPolyline(
                    points=(
                        (0.0, 0.0),
                        (width, 0.0),
                        (width, height),
                        (0.0, height),
                        (0.0, 0.0),
                    )
                ),
            )

        return LegacyGlyphResult(
            polylines=polylines,
            advance=width * 1.35,
            dl=0.0,
            dr=width,
            db=0.0,
            dt=height,
        )


class BadDecoder:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_idda_parcel_decoder_source_map.md"

    def decode_record(self, request):
        return LegacyGlyphResult(
            polylines=(
                LegacyGlyphPolyline(
                    points=((0.0, 0.0),),
                ),
            ),
            advance=0.05,
            dl=0.0,
            dr=0.04,
            db=0.0,
            dt=0.04,
        )


def make_provider(data_provider, decoder):
    return LegacyTraceDrawProvider(
        glyph_provider=LegacyDataBackedGlyphProvider(
            data_provider=data_provider,
            glyph_decoder=decoder,
        )
    )


def make_text(greek_provider, y=0.55):
    return build_text_item(
        "TextItem decoder contract: A~G~BC~R~D",
        0.10,
        y,
        resources={
            "txJust": "CenterLeft",
            "txFont": 21,
            "txFontHeightF": 0.050,
            "txFontColor": "black",
            "txFuncCode": "~",
            "climaraTextEngine": "plotchar",
            "climaraPlotcharGreekDrawProvider": greek_provider,
            "climaraPlotcharFillOn": False,
            "climaraPlotcharOutlineOn": True,
            "climaraPlotcharBBoxOn": True,
            "climaraPlotcharBBoxSource": "metrics",
            "climaraPlotcharBBoxColor": "blue",
            "climaraPlotcharBBoxThicknessF": 0.8,
        },
    )


def main():
    data_provider = DataProvider()
    decoder = GoodDecoder()
    greek_provider = make_provider(data_provider, decoder)

    root = HluPrimitive()
    root.add_child(make_text(greek_provider))

    out = Path("outputs/figures/demo_plotchar_textitem_greek_decoder_contract_regression.svg")
    save_svg(root, out, width=1200, height=420, background="white")

    if not data_provider.indices:
        raise AssertionError("data provider was not called")

    if not decoder.steps:
        raise AssertionError("decoder was not called")

    bad_root = HluPrimitive()
    bad_root.add_child(make_text(make_provider(DataProvider(), BadDecoder())))

    try:
        save_svg(
            bad_root,
            Path("outputs/figures/_bad_decoder_should_not_render.svg"),
            width=1200,
            height=420,
            background="white",
        )
    except PlotcharUnsupportedError as exc:
        print("bad decoder guarded:")
        print(exc)
    else:
        raise AssertionError("bad decoder output should be guarded")

    print("data provider INDA indices:")
    for index in data_provider.indices:
        print(f"  {index}")

    print("decoder steps:")
    for step in decoder.steps:
        print(
            f"  char={step.char!r} font={step.font_family} "
            f"size={step.size_level} case={step.case_mode} INDA={step.inda_index}"
        )

    print(f"wrote {out}")
    print("✅ TextItem Greek decoder contract regression demo passed")


if __name__ == "__main__":
    main()
