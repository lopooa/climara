from math import isfinite

from climara.graphics._labelbar_adjust import adjust_labelbar_geometry_for_text
from climara.graphics._labelbar_adjust_materialize import (
    LabelBarAdjustedGeometry,
    materialize_labelbar_adjusted_geometry,
)
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    assert_finite_bbox,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = make_labelbar("adjust_materialize")
    bundle = make_supplied_metrics_bundle(labelbar)
    geometry = bundle.adjust_request.geometry

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert_adjust_result(result)

    adjusted = materialize_labelbar_adjusted_geometry(result)

    assert isinstance(adjusted, LabelBarAdjustedGeometry)
    assert adjusted.source_geometry is bundle.adjust_request.geometry

    assert adjusted.external_view_bbox is result.final_view_bbox
    assert adjusted.adjusted_bar_bbox is result.final_adjusted_bar_bbox
    assert adjusted.adjusted_label_bbox is result.final_adjusted_label_bbox
    assert adjusted.adjusted_title_bbox is result.final_adjusted_title_bbox

    assert adjusted.external_view_bbox.coordinate_space == TEXT_BBOX_COORD_NDC
    assert_finite_bbox(adjusted.external_view_bbox)
    assert_finite_bbox(adjusted.nominal_perim_bbox)
    assert_finite_bbox(adjusted.adjusted_bar_bbox)

    assert len(adjusted.final_box_locs) == len(geometry.box_locs)
    assert len(adjusted.final_label_locs) == len(geometry.label_locs)
    assert len(adjusted.final_label_text_positions) == len(geometry.label_text_positions)

    for old, new in zip(geometry.box_locs, adjusted.final_box_locs):
        almost_equal(new, old - adjusted.major_offset)

    for old, new in zip(geometry.label_locs, adjusted.final_label_locs):
        almost_equal(new, old - adjusted.major_offset)

    assert adjusted.final_label_const_pos is not None

    orientation = str(geometry.multi_text_orientation).strip().lower()

    for loc, placement in zip(adjusted.final_label_locs, adjusted.final_label_text_positions):
        if orientation in {"yconst", "nhlmtextyconst"}:
            almost_equal(placement.x, loc)
            almost_equal(placement.y, adjusted.final_label_const_pos)
        elif orientation in {"xconst", "nhlmtextxconst"}:
            almost_equal(placement.x, adjusted.final_label_const_pos)
            almost_equal(placement.y, loc)
        else:
            raise AssertionError(f"unexpected MultiText orientation: {geometry.multi_text_orientation!r}")

        assert placement.text

    assert adjusted.final_title_x is not None
    assert adjusted.final_title_y is not None
    assert adjusted.final_title_text_position is not None
    assert adjusted.final_title_text_item is not None

    almost_equal(adjusted.final_title_text_position.x, adjusted.final_title_x)
    almost_equal(adjusted.final_title_text_position.y, adjusted.final_title_y)
    almost_equal(adjusted.final_title_text_item.x, adjusted.final_title_x)
    almost_equal(adjusted.final_title_text_item.y, adjusted.final_title_y)

    for value in (
        *adjusted.final_box_locs,
        *adjusted.final_label_locs,
        adjusted.final_label_const_pos,
        adjusted.final_title_x,
        adjusted.final_title_y,
        adjusted.x_offset,
        adjusted.y_offset,
        adjusted.major_offset,
        adjusted.minor_offset,
    ):
        assert isfinite(value), value

    print("✅ LabelBar AdjustGeometry materialization smoke passed")


if __name__ == "__main__":
    main()
