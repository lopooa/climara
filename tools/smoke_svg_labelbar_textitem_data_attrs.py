from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def main():
    labelbar = HluLabelBar(
        name="data_attr_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Data title",
            "lbTitlePosition": "Top",
            "lbTitleJust": "TopRight",
            "lbTitleFont": 25,
            "lbTitleFontColor": "black",
            "lbTitleFontHeightF": 0.04,
            "lbTitleFontAspectF": 1.1,
            "lbTitleFontThicknessF": 2.0,
            "lbTitleFontQuality": "Medium",
            "lbTitleConstantSpacingF": 0.2,
            "lbTitleFuncCode": "@",
            "lbLabelJust": "BottomLeft",
            "lbLabelFont": 26,
            "lbLabelFontColor": "red",
            "lbLabelFontHeightF": 0.03,
            "lbLabelFontAspectF": 1.2,
            "lbLabelFontThicknessF": 1.5,
            "lbLabelFontQuality": "Low",
            "lbLabelConstantSpacingF": 0.1,
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "%",
        },
    )

    out = Path("outputs/smoke/svg_labelbar_textitem_data_attrs.svg")
    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    assert "Data title" in svg
    assert ">A<" in svg

    assert 'data-ncl-direction="Across"' in svg
    assert 'data-ncl-real-string="@A@Data title"' in svg
    assert 'data-ncl-func-code="@"' in svg
    assert 'data-ncl-just="TopRight"' in svg
    assert 'data-ncl-font="25"' in svg
    assert 'data-ncl-font-height="0.04"' in svg
    assert 'data-ncl-font-aspect="1.1"' in svg
    assert 'data-ncl-font-thickness="2.0"' in svg
    assert 'data-ncl-font-quality="Medium"' in svg
    assert 'data-ncl-quality-index="1"' in svg
    assert 'data-ncl-constant-spacing="0.2"' in svg

    assert 'data-ncl-real-string="%A%A"' in svg
    assert 'data-ncl-func-code="%"' in svg
    assert 'data-ncl-just="BottomLeft"' in svg
    assert 'data-ncl-font="26"' in svg
    assert 'data-ncl-font-height="0.03"' in svg
    assert 'data-ncl-font-aspect="1.2"' in svg
    assert 'data-ncl-font-thickness="1.5"' in svg
    assert 'data-ncl-font-quality="Low"' in svg
    assert 'data-ncl-quality-index="2"' in svg
    assert 'data-ncl-constant-spacing="0.1"' in svg

    print("✅ SVG LabelBar TextItem data attributes smoke passed")


if __name__ == "__main__":
    main()
