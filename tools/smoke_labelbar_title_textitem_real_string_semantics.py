from climara.graphics._labelbar_object import HluLabelBar


def main():
    default_across = HluLabelBar(
        name="my_labelbar",
        resources={
            "lbTitleOn": True,
            "lbTitlePosition": "Top",
        },
    ).compute_geometry()

    item = default_across.title_text_item
    assert item is not None
    assert item.text == "my_labelbar"
    assert item.func_code == "~"
    assert item.direction == "Across"
    assert item.real_string == "~A~my_labelbar"

    default_down = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Left",
        },
    ).compute_geometry()

    item = default_down.title_text_item
    assert item is not None
    assert item.text == "Demo title"
    assert item.func_code == "~"
    assert item.direction == "Down"
    assert item.real_string == "~D~Demo title"

    custom_func_code = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Left",
            "lbTitleFuncCode": "@",
        },
    ).compute_geometry()

    item = custom_func_code.title_text_item
    assert item is not None
    assert item.func_code == "@"
    assert item.direction == "Down"
    assert item.real_string == "@D@Demo title"

    empty_func_code = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitleFuncCode": "",
        },
    ).compute_geometry()

    item = empty_func_code.title_text_item
    assert item is not None
    assert item.func_code == "~"
    assert item.real_string == "~A~Demo title"

    print("✅ LabelBar title TextItem real_string semantics smoke passed")


if __name__ == "__main__":
    main()
