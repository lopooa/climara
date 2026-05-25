from climara.graphics._labelbar_adjust import adjust_labelbar_geometry_for_text
from climara.graphics._labelbar_adjust_perim_semantics import (
    compute_labelbar_adjust_perimeter_semantics,
)

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    assert_finite_bbox,
    contains,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = make_labelbar("adjust_perim_semantics")
    bundle = make_supplied_metrics_bundle(labelbar)
    semantics = compute_labelbar_adjust_perimeter_semantics(
        bundle.adjust_request,
        justification="CenterCenter",
    )

    assert_finite_bbox(semantics.shifted_labelbar_bbox)
    assert_finite_bbox(semantics.external_perim_bbox)
    assert_finite_bbox(semantics.nominal_perim_bbox)
    assert_finite_bbox(semantics.final_adjusted_bar_bbox)
    assert_finite_bbox(semantics.final_labelbar_view_bbox)
    contains(semantics.external_perim_bbox, semantics.shifted_labelbar_bbox)
    contains(semantics.shifted_labelbar_bbox, semantics.final_adjusted_bar_bbox)

    geometry = labelbar.compute_geometry()
    almost_equal(semantics.nominal_perim_bbox.width, geometry.perim.width)
    almost_equal(semantics.nominal_perim_bbox.height, geometry.perim.height)

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert_adjust_result(result)

    print("✅ LabelBar AdjustGeometry supplied-bbox perimeter semantics smoke passed")


if __name__ == "__main__":
    main()
