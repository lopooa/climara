from climara.graphics._multitext_semantics import build_multitext_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    multi = build_multitext_semantics(
        ["A", "B", "C"],
        direction="NhlDown",
        func_code="@",
        just="NhlBottomLeft",
        angle=-30,
        font=26,
        font_color="blue",
        font_height=0.03,
        font_aspect=1.2,
        font_thickness=1.5,
        font_quality="NhlLow",
        constant_spacing=0.1,
    )

    assert len(multi) == 3
    assert multi.texts == ("A", "B", "C")
    assert multi.real_strings == ("@D@A", "@D@B", "@D@C")

    first = multi.items[0]
    assert first.text == "A"
    assert first.direction == "Down"
    assert first.real_string == "@D@A"
    assert first.func_code == "@"
    assert first.just == "BottomLeft"
    assert first.angle == 330.0
    assert first.font == 26
    assert first.font_color == "blue"
    almost_equal(first.font_height, 0.03)
    almost_equal(first.font_aspect, 1.2)
    almost_equal(first.font_thickness, 1.5)
    assert first.font_quality == "Low"
    assert first.quality_index == 2
    almost_equal(first.constant_spacing, 0.1)

    empty = build_multitext_semantics([])
    assert len(empty) == 0
    assert empty.texts == ()
    assert empty.real_strings == ()

    print("✅ MultiText semantics smoke passed")


if __name__ == "__main__":
    main()
