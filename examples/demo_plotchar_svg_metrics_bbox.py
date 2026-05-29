from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_text(root, text, y, bbox_source):
    root.add_child(
        build_text_item(
            text,
            0.08,
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
                "climaraPlotcharBBoxSource": bbox_source,
                "climaraPlotcharBBoxColor": "red" if bbox_source == "metrics" else "blue",
                "climaraPlotcharBBoxThicknessF": 0.9,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_text(root, "Metrics bbox: H~B~2~N~O", 0.72, "metrics")
    add_text(root, "Rendered bbox: H~B~2~N~O", 0.48, "rendered")
    add_text(root, "Metrics bbox: x~S~2~N~ + y~S~2~N~", 0.24, "metrics")

    out = Path("outputs/figures/demo_plotchar_svg_metrics_bbox.svg")
    save_svg(root, out, width=1000, height=600, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
