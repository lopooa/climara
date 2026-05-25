from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_semantics import TITLE_POSITION_LEFT, TITLE_POSITION_TOP


def almost_equal(value, expected, tol=1e-9):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    rect = (0.1, 0.9, 0.2, 0.8)

    no_title = HluLabelBar(
        rect=rect,
        resources={
            "lbOrientation": "Vertical",
            "lbBoxCount": 4,
        },
    ).compute_geometry()

    assert no_title.title_on is False
    assert no_title.title_area == no_title.adj_perim
    almost_equal(no_title.bar.t, no_title.adj_perim.t)

    top_title = HluLabelBar(
        rect=rect,
        resources={
            "lbOrientation": "Vertical",
            "lbBoxCount": 4,
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Top",
        },
    ).compute_geometry()

    assert top_title.title_on is True
    assert top_title.title_position == TITLE_POSITION_TOP
    almost_equal(top_title.title_area.t, top_title.adj_perim.t)
    almost_equal(top_title.title_area.b, top_title.adj_perim.t - 0.15 * top_title.adj_perim.height)
    almost_equal(top_title.title_offset_ndc, 0.03 * top_title.adj_perim.height)
    almost_equal(
        top_title.bar.t,
        top_title.adj_perim.t - 0.15 * top_title.adj_perim.height - 0.03 * top_title.adj_perim.height,
    )

    left_title = HluLabelBar(
        rect=rect,
        resources={
            "lbOrientation": "Vertical",
            "lbBoxCount": 4,
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Left",
        },
    ).compute_geometry()

    assert left_title.title_on is True
    assert left_title.title_position == TITLE_POSITION_LEFT
    almost_equal(left_title.title_area.l, left_title.adj_perim.l)
    almost_equal(left_title.title_area.r, left_title.adj_perim.l + 0.15 * left_title.adj_perim.width)
    almost_equal(left_title.title_offset_ndc, 0.03 * left_title.adj_perim.width)
    almost_equal(left_title.bar.l, left_title.title_area.r + left_title.title_offset_ndc)

    horizontal_top = HluLabelBar(
        rect=(0.1, 0.9, 0.8, 0.2),
        resources={
            "lbOrientation": "Horizontal",
            "lbBoxCount": 4,
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Top",
        },
    ).compute_geometry()

    almost_equal(horizontal_top.title_area.t, horizontal_top.adj_perim.t)
    almost_equal(horizontal_top.title_area.b, horizontal_top.adj_perim.t - 0.15 * horizontal_top.adj_perim.height)
    almost_equal(horizontal_top.title_offset_ndc, 0.03 * horizontal_top.adj_perim.height)
    almost_equal(horizontal_top.bar.t, horizontal_top.title_area.b - horizontal_top.title_offset_ndc)

    print("✅ LabelBar title geometry semantics smoke passed")


if __name__ == "__main__":
    main()
