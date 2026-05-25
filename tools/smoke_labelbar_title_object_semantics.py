from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_semantics import (
    NCL_LABELBAR_DEFAULT_TITLE,
    TITLE_DIRECTION_ACROSS,
    TITLE_DIRECTION_DOWN,
    TITLE_POSITION_LEFT,
    TITLE_POSITION_TOP,
)


def main():
    default_lb = HluLabelBar()
    assert default_lb.title_string == NCL_LABELBAR_DEFAULT_TITLE
    assert default_lb.title_on is False
    assert default_lb.title_position == TITLE_POSITION_TOP
    assert default_lb.title_direction == TITLE_DIRECTION_ACROSS
    assert default_lb.title_extent == 0.15
    assert default_lb.title_offset == 0.03
    assert default_lb.title_angle == 0.0
    assert default_lb.resources["lbTitleOn"] is False

    string_lb = HluLabelBar(resources={"lbTitleString": "Demo title"})
    assert string_lb.title_string == "Demo title"
    assert string_lb.title_on is True
    assert string_lb.title_position == TITLE_POSITION_TOP
    assert string_lb.title_direction == TITLE_DIRECTION_ACROSS

    left_lb = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "NhlLeft",
        }
    )
    assert left_lb.title_position == TITLE_POSITION_LEFT
    assert left_lb.title_direction == TITLE_DIRECTION_DOWN

    explicit_off_lb = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitleOn": "False",
        }
    )
    assert explicit_off_lb.title_on is False
    assert explicit_off_lb.resources["lbTitleOn"] is False

    explicit_on_default_string_lb = HluLabelBar(resources={"lbTitleOn": True})
    assert explicit_on_default_string_lb.title_on is True
    assert explicit_on_default_string_lb.title_string == NCL_LABELBAR_DEFAULT_TITLE

    explicit_on_default_string_lb.compute_geometry()

    print("✅ LabelBar title object semantics smoke passed")


if __name__ == "__main__":
    main()
