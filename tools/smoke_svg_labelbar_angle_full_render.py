from pathlib import Path
import re

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def main():
    out = Path("outputs/figures/labelbar_angle_full_render_smoke.svg")
    out.parent.mkdir(parents=True, exist_ok=True)

    labelbar = HluLabelBar(
        rect=(0.2, 0.85, 0.2, 0.5),
        colors=("#2166ac", "#f7f7f7", "#b2182b"),
        labels=("Low", "Mid", "High"),
        resources={
            "lbBoxCount": 3,
            "lbOrientation": "Vertical",
            "lbLabelAlignment": "BoxCenters",
            "lbLabelPosition": "Right",
            "lbLabelAngleF": -45.0,
            "lbLabelsOn": True,
        },
    )

    geom = labelbar.compute_geometry()
    assert geom.label_angle == 315.0
    assert geom.multi_text_orientation == "XConst"
    assert tuple(item.text for item in geom.label_text_positions) == ("Low", "Mid", "High")

    save_svg(labelbar, out, width=800, height=600)

    text = out.read_text(encoding="utf-8")

    if "<svg" not in text:
        raise RuntimeError("output is not a valid SVG document")

    if 'rotate(315.000' not in text:
        raise RuntimeError("full render SVG missing normalized lbLabelAngleF rotate transform")

    for label in ("Low", "Mid", "High"):
        if label not in text:
            raise RuntimeError(f"full render SVG missing angled label: {label}")

    transforms = re.findall(r'transform="rotate\(([^"]+)\)"', text)
    if len(transforms) != 3:
        raise RuntimeError(f"expected 3 rotate transforms, got {len(transforms)}")

    polygon_count = text.count("<polygon")
    line_count = text.count("<line")
    text_count = text.count("<text")

    if polygon_count < 3:
        raise RuntimeError(f"expected at least 3 polygons, got {polygon_count}")
    if text_count < 3:
        raise RuntimeError(f"expected at least 3 text nodes, got {text_count}")

    print(f"✅ LabelBar full-render angle smoke passed: {out}")
    print("✅ save_svg(...) emits SVG with normalized lbLabelAngleF rotate transforms")
    print(f"✅ polygon_count={polygon_count}, line_count={line_count}, text_count={text_count}")


if __name__ == "__main__":
    main()
