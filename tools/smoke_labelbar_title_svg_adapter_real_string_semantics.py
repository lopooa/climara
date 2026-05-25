from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives


def main():
    across_title = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Top",
            "lbTitleFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(across_title, 900, 500)

    assert len(primitives.title_texts) == 1
    title = primitives.title_texts[0]
    assert title.text == "Demo title"
    assert title.real_string == "~A~Demo title"
    assert title.func_code == "~"

    down_title = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Left",
            "lbTitleFuncCode": "@",
        },
    )

    primitives = labelbar_to_svg_primitives(down_title, 900, 500)

    assert len(primitives.title_texts) == 1
    title = primitives.title_texts[0]
    assert title.text == "Demo title"
    assert title.real_string == "@D@Demo title"
    assert title.func_code == "@"

    print("✅ LabelBar title SVG adapter real_string semantics smoke passed")


if __name__ == "__main__":
    main()
