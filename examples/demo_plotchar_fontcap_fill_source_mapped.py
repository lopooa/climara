from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_plotchar(root, text, x, y, *, fill_on, outline_on):
    root.add_child(
        build_text_item(
            text,
            x,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFont": 21,
                "txFontHeightF": 0.070,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
                "climaraPlotcharFillOn": fill_on,
                "climaraPlotcharOutlineOn": outline_on,
                "climaraPlotcharBBoxOn": True,
                "climaraPlotcharBBoxSource": "metrics",
                "climaraPlotcharBBoxColor": "blue",
                "climaraPlotcharBBoxThicknessF": 0.8,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_plotchar(root, "outline ABC", 0.08, 0.72, fill_on=False, outline_on=True)
    add_plotchar(root, "fill+outline ABC", 0.08, 0.46, fill_on=True, outline_on=True)
    add_plotchar(root, "fill only ABC", 0.08, 0.20, fill_on=True, outline_on=False)

    out = Path("outputs/figures/demo_plotchar_fontcap_fill_source_mapped.svg")
    save_svg(root, out, width=1200, height=700, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
