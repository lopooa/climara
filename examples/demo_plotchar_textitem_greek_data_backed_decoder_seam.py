from pathlib import Path

from climara.graphics._plotchar_legacy_data_backed_glyph import (
    LegacyDataBackedGlyphProvider,
)
from climara.graphics._plotchar_legacy_data_provider import (
    LegacyDigitizationRecord,
)
from climara.graphics._plotchar_legacy_glyph_provider import (
    LegacyGlyphPolyline,
    LegacyGlyphResult,
)
from climara.graphics._plotchar_legacy_trace_draw import LegacyTraceDrawProvider
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


class DemoSourceMappedDataProvider:
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
            source_note="demo record only; not NCL decoded glyph data",
        )


class DemoSourceMappedIddaDecoder:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_idda_parcel_decoder_source_map.md"

    def __init__(self):
        self.requests = []

    def decode_record(self, request):
        self.requests.append(request)

        # Demo glyph only. This is not the real NCL INDA/IDDA decoded shape.
        width = 0.035
        height = 0.055

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


def add_text(root, text, y, greek_provider):
    root.add_child(
        build_text_item(
            text,
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
    )


def main():
    data_provider = DemoSourceMappedDataProvider()
    decoder = DemoSourceMappedIddaDecoder()

    glyph_provider = LegacyDataBackedGlyphProvider(
        data_provider=data_provider,
        glyph_decoder=decoder,
    )

    greek_provider = LegacyTraceDrawProvider(
        glyph_provider=glyph_provider,
    )

    root = HluPrimitive()

    add_text(
        root,
        "TextItem data-backed Greek seam: A~G~BC~R~D",
        0.58,
        greek_provider,
    )

    out = Path("outputs/figures/demo_plotchar_textitem_greek_data_backed_decoder_seam.svg")
    save_svg(root, out, width=1100, height=420, background="white")

    print("data provider indices:")
    for index in data_provider.indices:
        print(f"  INDA={index}")

    print("decoder requests:")
    for request in decoder.requests:
        step = request.step
        print(
            f"  char={step.char!r} "
            f"font={step.font_family} "
            f"size={step.size_level} "
            f"case={step.case_mode} "
            f"INDA={step.inda_index}"
        )

    print(f"wrote {out}")
    print("✅ TextItem Greek data-backed decoder seam demo passed")


if __name__ == "__main__":
    main()
