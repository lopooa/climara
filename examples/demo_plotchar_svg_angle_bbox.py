from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_text(root, text, x, y, angle, bbox_source, color):
    root.add_child(
        build_text_item(
            text,
            x,
            y,
            resources={
                "txJust": "CenterCenter",
                "txFont": 21,
                "txFontHeightF": 0.040,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "txAngleF": angle,
                "climaraTextEngine": "plotchar",
                "climaraPlotcharFillOn": False,
                "climaraPlotcharOutlineOn": True,
                "climaraPlotcharBBoxOn": True,
                "climaraPlotcharBBoxSource": bbox_source,
                "climaraPlotcharBBoxColor": color,
                "climaraPlotcharBBoxThicknessF": 0.9,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_text(root, "Metrics 0", 0.20, 0.75, 0.0, "metrics", "red")
    add_text(root, "Metrics 45", 0.52, 0.55, 45.0, "metrics", "red")
    add_text(root, "Metrics 90", 0.78, 0.35, 90.0, "metrics", "red")
    add_text(root, "Rendered 45", 0.28, 0.30, 45.0, "rendered", "blue")

    out = Path("outputs/figures/demo_plotchar_svg_angle_bbox.svg")
    save_svg(root, out, width=1000, height=760, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
