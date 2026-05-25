from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives


def _primitive_texts(resources):
    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Plain title",
            "lbTitlePosition": "Top",
            **resources,
        },
    )

    primitives = labelbar_to_svg_primitives(labelbar, 900, 500)
    assert primitives.texts
    return primitives.texts


def _assert_real_strings(texts, direction, func_code):
    dir_code = "D" if direction == "Down" else "A"

    for text in texts:
        assert text.direction == direction, (text.text, text.direction)
        assert text.func_code == func_code, (text.text, text.func_code)
        expected = f"{func_code}{dir_code}{func_code}{text.text}"
        assert text.real_string == expected, (text.text, text.real_string, expected)


def main():
    across = _primitive_texts(
        {
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
        }
    )
    assert [text.text for text in across[:4]] == ["A", "B", "C", "D"]
    _assert_real_strings(across, "Across", "~")

    down = _primitive_texts(
        {
            "lbLabelDirection": "Down",
            "lbLabelFuncCode": "~",
        }
    )
    assert [text.text for text in down[:4]] == ["A", "B", "C", "D"]
    _assert_real_strings(down, "Down", "~")

    custom = _primitive_texts(
        {
            "lbLabelDirection": "NhlAcross",
            "lbLabelFuncCode": "@",
        }
    )
    assert [text.text for text in custom[:4]] == ["A", "B", "C", "D"]
    _assert_real_strings(custom, "Across", "@")

    print("✅ LabelBar label TextItem real_string semantics smoke passed")


if __name__ == "__main__":
    main()
