from climara.graphics._labelbar_adjust import adjust_labelbar_geometry_for_text
from climara.graphics._labelbar_adjust_apply import (
    adjusted_geometry_from_result,
    apply_labelbar_adjusted_geometry,
)
from climara.graphics._labelbar_adjust_materialize import (
    materialize_labelbar_adjusted_geometry,
)
from climara.graphics._labelbar_geometry import LabelBarGeometry

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_rect_matches_bbox(rect, box):
    almost_equal(rect.l, box.l)
    almost_equal(rect.r, box.r)
    almost_equal(rect.b, box.b)
    almost_equal(rect.t, box.t)


def main():
    labelbar = make_labelbar("adjust_apply_geometry")
    bundle = make_supplied_metrics_bundle(labelbar)

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert_adjust_result(result)

    adjusted = materialize_labelbar_adjusted_geometry(result)
    new_geometry = apply_labelbar_adjusted_geometry(adjusted)
    new_geometry_2 = adjusted_geometry_from_result(result)

    assert isinstance(new_geometry, LabelBarGeometry)
    assert isinstance(new_geometry_2, LabelBarGeometry)

    assert new_geometry is not adjusted.source_geometry
    assert new_geometry_2 is not adjusted.source_geometry

    assert_rect_matches_bbox(new_geometry.perim, adjusted.nominal_perim_bbox)
    assert_rect_matches_bbox(new_geometry.adj_bar, adjusted.adjusted_bar_bbox)

    assert new_geometry.box_locs == adjusted.final_box_locs
    assert new_geometry.label_locs == adjusted.final_label_locs

    if adjusted.final_label_const_pos is not None:
        almost_equal(new_geometry.label_const_pos, adjusted.final_label_const_pos)

    assert new_geometry.label_text_positions == adjusted.final_label_text_positions
    assert new_geometry.title_text_position == adjusted.final_title_text_position
    assert new_geometry.title_text_item == adjusted.final_title_text_item

    assert new_geometry_2.box_locs == new_geometry.box_locs
    assert new_geometry_2.label_locs == new_geometry.label_locs
    assert new_geometry_2.label_const_pos == new_geometry.label_const_pos
    assert new_geometry_2.label_text_positions == new_geometry.label_text_positions
    assert new_geometry_2.title_text_position == new_geometry.title_text_position
    assert new_geometry_2.title_text_item == new_geometry.title_text_item

    orientation = str(new_geometry.multi_text_orientation).strip().lower()

    for loc, placement in zip(new_geometry.label_locs, new_geometry.label_text_positions):
        if orientation in {"yconst", "nhlmtextyconst"}:
            almost_equal(placement.x, loc)
            almost_equal(placement.y, new_geometry.label_const_pos)
        elif orientation in {"xconst", "nhlmtextxconst"}:
            almost_equal(placement.x, new_geometry.label_const_pos)
            almost_equal(placement.y, loc)
        else:
            raise AssertionError(f"unexpected MultiText orientation: {new_geometry.multi_text_orientation!r}")

    print("✅ LabelBar AdjustGeometry apply-to-geometry smoke passed")


if __name__ == "__main__":
    main()
