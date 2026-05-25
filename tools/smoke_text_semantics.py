from climara.graphics._text_semantics import (
    TEXT_DIRECTION_ACROSS,
    TEXT_DIRECTION_DOWN,
    TEXT_JUST_BOTTOM_LEFT,
    TEXT_JUST_CENTER_CENTER,
    TEXT_JUST_TOP_RIGHT,
    TEXT_QUALITY_HIGH,
    TEXT_QUALITY_LOW,
    TEXT_QUALITY_MEDIUM,
    TEXT_QUALITY_WORKSTATION,
    build_text_item_semantics,
    normalize_func_code,
    normalize_text_angle,
    normalize_text_direction,
    normalize_text_just,
    normalize_text_quality,
    non_negative_text_float,
    text_quality_index,
    text_real_string,
    text_uses_func_code,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    assert normalize_text_direction(None) == TEXT_DIRECTION_ACROSS
    assert normalize_text_direction("Across") == TEXT_DIRECTION_ACROSS
    assert normalize_text_direction("NhlAcross") == TEXT_DIRECTION_ACROSS
    assert normalize_text_direction("Down") == TEXT_DIRECTION_DOWN
    assert normalize_text_direction("NhlDown") == TEXT_DIRECTION_DOWN

    assert normalize_text_just(None) == TEXT_JUST_CENTER_CENTER
    assert normalize_text_just("NhlBottomLeft") == TEXT_JUST_BOTTOM_LEFT
    assert normalize_text_just("TopRight") == TEXT_JUST_TOP_RIGHT

    assert normalize_text_quality(None) == TEXT_QUALITY_HIGH
    assert normalize_text_quality("High") == TEXT_QUALITY_HIGH
    assert normalize_text_quality("NhlMedium") == TEXT_QUALITY_MEDIUM
    assert normalize_text_quality("Low") == TEXT_QUALITY_LOW
    assert normalize_text_quality("NhlWorkstation") == TEXT_QUALITY_WORKSTATION

    assert text_quality_index("High") == 0
    assert text_quality_index("Medium") == 1
    assert text_quality_index("Low") == 2
    assert text_quality_index("Workstation") == 3

    assert normalize_func_code(None) == "~"
    assert normalize_func_code("") == "~"
    assert normalize_func_code("@@") == "@"

    assert text_real_string("Demo", "Across", "~") == "~A~Demo"
    assert text_real_string("Demo", "Down", "~") == "~D~Demo"
    assert text_real_string("Demo", "NhlDown", "@") == "@D@Demo"

    assert text_uses_func_code("Speed ~S~2~N~", "~")
    assert not text_uses_func_code("Speed plain", "~")

    assert normalize_text_angle(None) == 0.0
    assert normalize_text_angle(30) == 30.0
    assert normalize_text_angle(-45) == 315.0

    almost_equal(non_negative_text_float(None, 0.1), 0.1)
    almost_equal(non_negative_text_float(0.2, 0.1), 0.2)
    almost_equal(non_negative_text_float(-1.0, 0.1), 0.0)

    item = build_text_item_semantics(
        "Demo",
        direction="NhlDown",
        func_code="@",
        just="NhlTopRight",
        angle=-45,
        font=25,
        font_color="red",
        font_height=0.04,
        font_aspect=1.1,
        font_thickness=2.0,
        font_quality="NhlMedium",
        constant_spacing=0.2,
    )

    assert item.text == "Demo"
    assert item.direction == TEXT_DIRECTION_DOWN
    assert item.real_string == "@D@Demo"
    assert item.func_code == "@"
    assert item.just == TEXT_JUST_TOP_RIGHT
    assert item.angle == 315.0
    assert item.font == 25
    assert item.font_color == "red"
    almost_equal(item.font_height, 0.04)
    almost_equal(item.font_aspect, 1.1)
    almost_equal(item.font_thickness, 2.0)
    assert item.font_quality == TEXT_QUALITY_MEDIUM
    assert item.quality_index == 1
    almost_equal(item.constant_spacing, 0.2)

    negative = build_text_item_semantics(
        "Demo",
        font_height=-1.0,
        constant_spacing=-1.0,
    )

    almost_equal(negative.font_height, 0.0)
    almost_equal(negative.constant_spacing, 0.0)

    print("✅ TextItem semantics smoke passed")


if __name__ == "__main__":
    main()
