from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def _must_raise(labelbar, filename):
    try:
        save_svg(labelbar, Path("outputs/smoke") / filename, width=900, height=500)
    except NotImplementedError as exc:
        message = str(exc)
        assert "Plotchar function-code sequences" in message
        assert "will not draw function-code text as plain SVG text" in message
    else:
        raise AssertionError("Plotchar function-code title should not be rendered as plain SVG text")


def main():
    plain_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbTitlePosition": "Top",
        },
    )

    save_svg(
        plain_title,
        Path("outputs/smoke/svg_labelbar_title_plain_plotchar_guard.svg"),
        width=900,
        height=500,
    )

    default_func_code_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Speed ~S~2~N~",
            "lbTitlePosition": "Top",
        },
    )

    _must_raise(
        default_func_code_title,
        "svg_labelbar_title_default_func_code_guard.svg",
    )

    custom_func_code_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Speed @S@2@N@",
            "lbTitleFuncCode": "@",
            "lbTitlePosition": "Top",
        },
    )

    _must_raise(
        custom_func_code_title,
        "svg_labelbar_title_custom_func_code_guard.svg",
    )

    print("✅ SVG LabelBar title Plotchar guard smoke passed")


if __name__ == "__main__":
    main()
