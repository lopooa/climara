from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


def _must_raise(labelbar, filename):
    try:
        save_svg(labelbar, Path("outputs/smoke") / filename, width=900, height=500)
    except NotImplementedError as exc:
        message = str(exc)
        assert "Plotchar function-code sequences" in message
        assert "will not draw function-code text as plain SVG text" in message
    else:
        raise AssertionError("Label Plotchar function-code text should not be rendered as plain SVG text")


def main():
    plain_labels = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbLabelFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(plain_labels, 900, 500)

    assert primitives.texts
    assert all(text.func_code == "~" for text in primitives.texts)

    save_svg(
        plain_labels,
        Path("outputs/smoke/svg_labelbar_plain_label_plotchar_guard.svg"),
        width=900,
        height=500,
    )

    default_func_code_label = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B ~S~2~N~", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbLabelFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(default_func_code_label, 900, 500)

    assert any(text.text == "B ~S~2~N~" for text in primitives.texts)
    assert all(text.func_code == "~" for text in primitives.texts)

    _must_raise(
        default_func_code_label,
        "svg_labelbar_default_label_func_code_guard.svg",
    )

    custom_func_code_label = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B @S@2@N@", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbLabelFuncCode": "@",
        },
    )

    primitives = labelbar_to_svg_primitives(custom_func_code_label, 900, 500)

    assert any(text.text == "B @S@2@N@" for text in primitives.texts)
    assert all(text.func_code == "@" for text in primitives.texts)

    _must_raise(
        custom_func_code_label,
        "svg_labelbar_custom_label_func_code_guard.svg",
    )

    print("✅ LabelBar label Plotchar guard smoke passed")


if __name__ == "__main__":
    main()
