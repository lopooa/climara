from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
    has_labelbar_adjust_geometry_engine,
)

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = make_labelbar("adjust_geometry_execution")
    geometry = labelbar.compute_geometry()
    bundle = make_supplied_metrics_bundle(labelbar)

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)

    assert result.request is bundle.adjust_request
    assert result.writeback_semantics.final_view_bbox is result.final_view_bbox
    assert len(result.final_box_locs) == len(geometry.box_locs)
    assert len(result.final_label_locs) == len(geometry.label_locs)

    for original, final in zip(geometry.box_locs, result.final_box_locs):
        almost_equal(final, original - result.major_offset)

    for original, final in zip(geometry.label_locs, result.final_label_locs):
        almost_equal(final, original - result.major_offset)

    assert result.final_label_const_pos is not None
    assert result.final_title_x is not None
    assert result.final_title_y is not None
    assert has_labelbar_adjust_geometry_engine() is False

    assert_adjust_result(result)

    print("✅ LabelBar AdjustGeometry supplied-bbox execution smoke passed")


if __name__ == "__main__":
    main()
