from pathlib import Path

from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_plotchar(root, text, x, y):
    root.add_child(
        build_text_item(
            text,
            x,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFont": 21,
                "txFontHeightF": 0.045,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
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
    root = HluPrimitive()

    add_plotchar(root, "Plain ABC", 0.08, 0.72)
    add_plotchar(root, "Roman A~R~BC", 0.08, 0.48)

    try:
        bad = HluPrimitive()
        add_plotchar(bad, "Greek A~G~BC", 0.08, 0.24)
        save_svg(
            bad,
            Path("outputs/figures/demo_plotchar_g_should_guard.svg"),
            width=1000,
            height=300,
            background="white",
        )
    except PlotcharUnsupportedError as exc:
        print("G remains guarded:", exc)
    else:
        raise AssertionError("Plotchar G Greek command should remain guarded")

    out = Path("outputs/figures/demo_plotchar_r_roman_svg_runtime.svg")
    save_svg(root, out, width=1000, height=500, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
