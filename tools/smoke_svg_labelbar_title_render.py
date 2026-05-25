from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def _render_to_text(labelbar, filename):
    out = Path("outputs/smoke") / filename
    save_svg(labelbar, out, width=900, height=500)
    return out.read_text(encoding="utf-8")


def main():
    explicit_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Top",
            "lbTitleJust": "CenterCenter",
            "lbTitleFontColor": "black",
            "lbTitleFontHeightF": 0.04,
            "lbLabelsOn": True,
        },
    )

    svg = _render_to_text(explicit_title, "svg_labelbar_title_render.svg")

    assert "Demo title" in svg
    assert ">A<" in svg
    assert 'font-size="20.000"' in svg
    assert 'text-anchor="middle"' in svg
    assert svg.index("Demo title") < svg.index(">A<")

    default_title = HluLabelBar(
        name="my_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": True,
            "lbTitlePosition": "Top",
        },
    )

    svg = _render_to_text(default_title, "svg_labelbar_title_default_name_render.svg")

    assert "my_labelbar" in svg
    assert "NOTHING" not in svg
    assert svg.index("my_labelbar") < svg.index(">A<")

    title_off = HluLabelBar(
        name="hidden_title_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Hidden title",
            "lbTitleOn": False,
        },
    )

    svg = _render_to_text(title_off, "svg_labelbar_title_off_render.svg")

    assert "Hidden title" not in svg
    assert ">A<" in svg

    print("✅ SVG LabelBar title render smoke passed")


if __name__ == "__main__":
    main()
