from dataclasses import fields
from pathlib import Path

from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


def almost_equal(value, expected, tol=1e-9):
    assert abs(value - expected) <= tol, (value, expected)


def _labelbar(labels=None, **resources):
    if labels is None:
        labels = ["A", "B", "C", "D"]

    merged = {
        "lbTitleOn": False,
        "lbLabelDirection": "Across",
        "lbLabelFuncCode": "~",
    }
    merged.update(resources)

    return HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=labels,
        resources=merged,
    )


def _must_raise_not_implemented(labelbar, filename, required_parts):
    try:
        save_svg(labelbar, Path("outputs/smoke") / filename, width=900, height=500)
    except NotImplementedError as exc:
        message = str(exc)
        for part in required_parts:
            assert part in message, message
    else:
        raise AssertionError("expected NotImplementedError")


def _assert_label_textitem(text, *, direction, func_code):
    dir_code = "D" if direction == "Down" else "A"

    assert text.direction == direction
    assert text.func_code == func_code
    assert text.real_string == f"{func_code}{dir_code}{func_code}{text.text}"


def main():
    geometry_fields = {field.name for field in fields(LabelBarGeometry)}

    forbidden_geometry_fields = {
        "label_func_code",
        "label_direction",
        "label_font",
        "label_font_aspect",
        "label_font_thickness",
        "label_font_quality",
        "label_quality_index",
        "label_constant_spacing",
    }

    assert geometry_fields.isdisjoint(forbidden_geometry_fields), geometry_fields

    default_lb = _labelbar()
    default_primitives = labelbar_to_svg_primitives(default_lb, 900, 500)

    assert default_primitives.texts
    assert [text.text for text in default_primitives.texts[:4]] == ["A", "B", "C", "D"]

    for text in default_primitives.texts:
        _assert_label_textitem(text, direction="Across", func_code="~")
        assert text.just == "CenterCenter"
        assert text.font == 21
        almost_equal(text.font_height, 0.02)
        almost_equal(text.font_aspect, 1.3125)
        almost_equal(text.font_thickness, 1.0)
        assert text.font_quality == "High"
        assert text.quality_index == 0
        almost_equal(text.constant_spacing, 0.0)

    out = Path("outputs/smoke/svg_labelbar_label_textitem_contract_across.svg")
    save_svg(default_lb, out, width=900, height=500)
    svg = out.read_text(encoding="utf-8")
    assert ">A<" in svg

    custom_lb = _labelbar(
        lbLabelJust="TopRight",
        lbLabelFont=25,
        lbLabelFontHeightF=0.04,
        lbLabelFontAspectF=1.1,
        lbLabelFontThicknessF=2.0,
        lbLabelFontQuality="Medium",
        lbLabelConstantSpacingF=0.2,
        lbLabelFuncCode="@",
    )

    custom_primitives = labelbar_to_svg_primitives(custom_lb, 900, 500)

    assert custom_primitives.texts
    for text in custom_primitives.texts:
        _assert_label_textitem(text, direction="Across", func_code="@")
        assert text.just == "TopRight"
        assert text.font == 25
        almost_equal(text.font_height, 0.04)
        almost_equal(text.font_aspect, 1.1)
        almost_equal(text.font_thickness, 2.0)
        assert text.font_quality == "Medium"
        assert text.quality_index == 1
        almost_equal(text.constant_spacing, 0.2)

    down_lb = _labelbar(lbLabelDirection="Down")
    down_primitives = labelbar_to_svg_primitives(down_lb, 900, 500)

    assert down_primitives.texts
    for text in down_primitives.texts:
        _assert_label_textitem(text, direction="Down", func_code="~")

    _must_raise_not_implemented(
        down_lb,
        "svg_labelbar_label_textitem_contract_down.svg",
        ("TextItem direction 'Down'", "Plotchar vertical text"),
    )

    func_code_lb = _labelbar(labels=["A", "B ~S~2~N~", "C", "D"])
    func_code_primitives = labelbar_to_svg_primitives(func_code_lb, 900, 500)

    assert any(text.text == "B ~S~2~N~" for text in func_code_primitives.texts)

    _must_raise_not_implemented(
        func_code_lb,
        "svg_labelbar_label_textitem_contract_func_code.svg",
        ("Plotchar function-code sequences", "plain SVG text"),
    )

    low_quality_lb = _labelbar(
        lbLabelFontQuality="NhlLow",
        lbLabelConstantSpacingF=-1.0,
    )

    low_quality_primitives = labelbar_to_svg_primitives(low_quality_lb, 900, 500)
    assert low_quality_primitives.texts
    assert low_quality_primitives.texts[0].quality_index == 2
    almost_equal(low_quality_primitives.texts[0].constant_spacing, 0.0)

    print("✅ LabelBar label TextItem contract smoke passed")


if __name__ == "__main__":
    main()
