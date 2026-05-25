from climara.graphics._labelbar_object import HluLabelBar


def almost_equal(value, expected, tol=1e-9):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    off_geom = HluLabelBar().compute_geometry()
    assert off_geom.title_text_position is None

    default_string_geom = HluLabelBar(
        name="my_labelbar",
        resources={
            "lbTitleOn": True,
            "lbTitleExtentF": 0.15,
        },
    ).compute_geometry()

    assert default_string_geom.title_text_position is not None
    assert default_string_geom.title_text_position.text == "my_labelbar"

    almost_equal(
        default_string_geom.title_text_position.x,
        default_string_geom.title_area.l + default_string_geom.title_area.width / 2.0,
    )
    almost_equal(
        default_string_geom.title_text_position.y,
        default_string_geom.title_area.b + default_string_geom.title_area.height / 2.0,
    )
    assert default_string_geom.title_just == "CenterCenter"

    top_right_geom = HluLabelBar(
        name="named_labelbar",
        resources={
            "lbTitleString": "Demo title",
            "lbTitleJust": "TopRight",
            "lbTitleAngleF": -45,
        },
    ).compute_geometry()

    assert top_right_geom.title_text_position is not None
    assert top_right_geom.title_text_position.text == "Demo title"
    assert top_right_geom.title_just == "TopRight"
    assert top_right_geom.title_angle == 315.0
    almost_equal(top_right_geom.title_text_position.x, top_right_geom.title_area.r)
    almost_equal(top_right_geom.title_text_position.y, top_right_geom.title_area.t)

    bottom_left_geom = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitleJust": "NhlBottomLeft",
        },
    ).compute_geometry()

    assert bottom_left_geom.title_text_position is not None
    assert bottom_left_geom.title_just == "BottomLeft"
    almost_equal(bottom_left_geom.title_text_position.x, bottom_left_geom.title_area.l)
    almost_equal(bottom_left_geom.title_text_position.y, bottom_left_geom.title_area.b)

    print("✅ LabelBar title text geometry semantics smoke passed")


if __name__ == "__main__":
    main()
