from dataclasses import fields
from pathlib import Path

from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_semantics import NCL_LABELBAR_DEFAULTS
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


def _read_svg(labelbar, filename):
    out = Path("outputs/smoke") / filename
    save_svg(labelbar, out, width=900, height=500)
    return out.read_text(encoding="utf-8")


def _must_raise_not_implemented(labelbar, filename, required):
    try:
        _read_svg(labelbar, filename)
    except NotImplementedError as exc:
        message = str(exc)
        for text in required:
            assert text in message, message
    else:
        raise AssertionError("expected NotImplementedError")


def _base_labelbar(**resources):
    merged = {
        "lbTitleString": "Plain title",
        "lbTitlePosition": "Top",
    }
    merged.update(resources)

    return HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources=merged,
    )


def main():
    geometry_fields = {field.name for field in fields(LabelBarGeometry)}
    assert "label_func_code" not in geometry_fields

    assert NCL_LABELBAR_DEFAULTS["lbLabelFuncCode"] == "~"

    default_label_func_code = _base_labelbar()
    primitives = labelbar_to_svg_primitives(default_label_func_code, 900, 500)
    assert primitives.texts
    assert all(text.func_code == "~" for text in primitives.texts)

    custom_label_func_code = _base_labelbar(lbLabelFuncCode="@")
    primitives = labelbar_to_svg_primitives(custom_label_func_code, 900, 500)
    assert primitives.texts
    assert all(text.func_code == "@" for text in primitives.texts)

    top_svg = _read_svg(
        _base_labelbar(lbTitleString="Top title", lbTitlePosition="Top"),
        "svg_labelbar_contract_top_title.svg",
    )
    assert "Top title" in top_svg
    assert ">A<" in top_svg

    bottom_svg = _read_svg(
        _base_labelbar(lbTitleString="Bottom title", lbTitlePosition="Bottom"),
        "svg_labelbar_contract_bottom_title.svg",
    )
    assert "Bottom title" in bottom_svg
    assert ">A<" in bottom_svg

    left_title = _base_labelbar(lbTitleString="Left title", lbTitlePosition="Left")
    primitives = labelbar_to_svg_primitives(left_title, 900, 500)
    assert primitives.title_texts
    assert primitives.title_texts[0].direction == "Down"
    assert primitives.title_texts[0].real_string == "~D~Left title"

    _must_raise_not_implemented(
        left_title,
        "svg_labelbar_contract_left_title.svg",
        ("TextItem direction 'Down'", "Plotchar vertical text"),
    )

    right_title = _base_labelbar(lbTitleString="Right title", lbTitlePosition="Right")
    primitives = labelbar_to_svg_primitives(right_title, 900, 500)
    assert primitives.title_texts
    assert primitives.title_texts[0].direction == "Down"
    assert primitives.title_texts[0].real_string == "~D~Right title"

    _must_raise_not_implemented(
        right_title,
        "svg_labelbar_contract_right_title.svg",
        ("TextItem direction 'Down'", "Plotchar vertical text"),
    )

    title_with_func_code = _base_labelbar(lbTitleString="Speed ~S~2~N~")
    _must_raise_not_implemented(
        title_with_func_code,
        "svg_labelbar_contract_title_func_code.svg",
        ("Plotchar function-code sequences", "plain SVG text"),
    )

    label_with_func_code = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B ~S~2~N~", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbTitlePosition": "Top",
            "lbLabelFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(label_with_func_code, 900, 500)
    assert primitives.texts
    assert any(text.text == "B ~S~2~N~" for text in primitives.texts)
    assert all(text.func_code == "~" for text in primitives.texts)

    _must_raise_not_implemented(
        label_with_func_code,
        "svg_labelbar_contract_label_func_code.svg",
        ("Plotchar function-code sequences", "plain SVG text"),
    )

    custom_label_with_func_code = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B @S@2@N@", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbTitlePosition": "Top",
            "lbLabelFuncCode": "@",
        },
    )

    primitives = labelbar_to_svg_primitives(custom_label_with_func_code, 900, 500)
    assert primitives.texts
    assert any(text.text == "B @S@2@N@" for text in primitives.texts)
    assert all(text.func_code == "@" for text in primitives.texts)

    _must_raise_not_implemented(
        custom_label_with_func_code,
        "svg_labelbar_contract_custom_label_func_code.svg",
        ("Plotchar function-code sequences", "plain SVG text"),
    )

    print("✅ LabelBar SVG text contract smoke passed")


if __name__ == "__main__":
    main()
