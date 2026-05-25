from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


def main():
    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Down title",
            "lbTitlePosition": "Left",
        },
    )

    primitives = labelbar_to_svg_primitives(labelbar, 900, 500)

    assert len(primitives.title_texts) == 1
    assert primitives.title_texts[0].direction == "Down"
    assert primitives.title_texts[0].real_string == "~D~Down title"

    try:
        save_svg(labelbar, Path("outputs/smoke/svg_labelbar_title_down_direction_guard.svg"), width=900, height=500)
    except NotImplementedError as exc:
        message = str(exc)
        assert "TextItem direction 'Down'" in message
        assert "will not draw unsupported Plotchar vertical text" in message
    else:
        raise AssertionError("Down-direction title should not be rendered as fake horizontal SVG text")

    print("✅ SVG LabelBar title Down-direction guard smoke passed")


if __name__ == "__main__":
    main()
