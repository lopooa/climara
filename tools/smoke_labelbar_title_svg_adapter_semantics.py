from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_semantics import TITLE_DIRECTION_DOWN
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives


def almost_equal(value, expected, tol=1e-9):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    no_title = HluLabelBar()
    no_title_primitives = labelbar_to_svg_primitives(no_title, 1000, 800)
    assert no_title_primitives.title_texts == ()

    title_lb = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Left",
            "lbTitleJust": "TopRight",
            "lbTitleAngleF": -45,
            "lbTitleFont": 25,
            "lbTitleFontColor": "red",
            "lbTitleFontHeightF": 0.04,
        },
    )

    geometry = title_lb.compute_geometry()
    primitives = labelbar_to_svg_primitives(title_lb, 1000, 800)

    assert len(primitives.title_texts) == 1
    title = primitives.title_texts[0]

    assert title.text == "Demo title"
    assert title.fill == "red"
    assert title.angle == 315.0
    assert title.font == 25
    assert title.just == "TopRight"
    assert title.direction == TITLE_DIRECTION_DOWN
    almost_equal(title.font_height, 0.04)

    assert geometry.title_text_item is not None
    almost_equal(title.x, geometry.title_text_item.x * 1000)
    almost_equal(title.y, (1.0 - geometry.title_text_item.y) * 800)

    label_count = len(primitives.texts)
    assert label_count == geometry.label_draw_count

    print("✅ LabelBar title SVG adapter semantics smoke passed")


if __name__ == "__main__":
    main()
