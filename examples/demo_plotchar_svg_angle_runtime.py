from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_text(root, text, x, y, angle):
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
                "climaraPlotcharBBoxOn": False,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_text(root, "ANGD 0", 0.20, 0.75, 0.0)
    add_text(root, "ANGD 45", 0.50, 0.55, 45.0)
    add_text(root, "ANGD 90", 0.75, 0.35, 90.0)
    add_text(root, "H~B~2~N~O 45", 0.30, 0.35, 45.0)

    out = Path("outputs/figures/demo_plotchar_svg_angle_runtime.svg")
    save_svg(root, out, width=900, height=700, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
