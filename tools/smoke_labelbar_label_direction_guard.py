from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


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
    across = _base_labelbar(lbLabelDirection="Across")
    primitives = labelbar_to_svg_primitives(across, 900, 500)

    assert primitives.texts
    assert all(text.direction == "Across" for text in primitives.texts)
    assert all(text.func_code == "~" for text in primitives.texts)

    out = Path("outputs/smoke/svg_labelbar_label_direction_across.svg")
    save_svg(across, out, width=900, height=500)
    svg = out.read_text(encoding="utf-8")
    assert ">A<" in svg

    down = _base_labelbar(lbLabelDirection="Down")
    primitives = labelbar_to_svg_primitives(down, 900, 500)

    assert primitives.texts
    assert all(text.direction == "Down" for text in primitives.texts)

    try:
        save_svg(
            down,
            Path("outputs/smoke/svg_labelbar_label_direction_down.svg"),
            width=900,
            height=500,
        )
    except NotImplementedError as exc:
        message = str(exc)
        assert "TextItem direction 'Down'" in message
        assert "Plotchar vertical text" in message
    else:
        raise AssertionError("Down-direction labels should not be rendered as plain SVG text")

    nhl_down = _base_labelbar(lbLabelDirection="NhlDown")
    primitives = labelbar_to_svg_primitives(nhl_down, 900, 500)

    assert primitives.texts
    assert all(text.direction == "Down" for text in primitives.texts)

    print("✅ LabelBar label direction guard smoke passed")


if __name__ == "__main__":
    main()
