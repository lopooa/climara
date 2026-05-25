from pathlib import Path

from climara.graphics._labelbar_object import build_hlu_labelbar
from climara.graphics._render_svg import save_svg


def main():
    out = Path("outputs/figures/labelbar_labels_off_full_render_smoke.svg")
    out.parent.mkdir(parents=True, exist_ok=True)

    labelbar = build_hlu_labelbar(
        rect=(0.15, 0.82, 0.70, 0.18),
        colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62"),
        labels=("A", "B", "C"),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbLabelsOn": False,
            "lbBoxLinesOn": True,
            "lbBoxSeparatorLinesOn": True,
            "lbBoxLineColor": "black",
        },
    )

    geom = labelbar.compute_geometry()
    assert geom.label_draw_count == 0
    assert geom.visible_label_strings == ()
    assert geom.label_locs == ()
    assert geom.label_text_positions == ()

    save_svg(labelbar, out, width=900, height=500)

    text = out.read_text(encoding="utf-8")

    if "<svg" not in text:
        raise RuntimeError("full-render labels-off smoke did not produce SVG")

    polygon_count = text.count("<polygon")
    line_count = text.count("<line")
    text_count = text.count("<text")

    if polygon_count < 4:
        raise RuntimeError(f"expected box polygons even when labels are off, got {polygon_count}")

    if line_count < 4:
        raise RuntimeError(f"expected box lines even when labels are off, got {line_count}")

    if text_count != 0:
        raise RuntimeError(f"lbLabelsOn=False should suppress LabelBar text nodes, got {text_count}")

    for label in ("A", "B", "C"):
        if f">{label}</text>" in text:
            raise RuntimeError(f"lbLabelsOn=False leaked label text into SVG: {label}")

    print(f"✅ LabelBar labels-off full-render smoke passed: {out}")
    print("✅ save_svg(...) keeps boxes/lines but suppresses SVG text when lbLabelsOn=False")
    print(f"✅ polygon_count={polygon_count}, line_count={line_count}, text_count={text_count}")


if __name__ == "__main__":
    main()
