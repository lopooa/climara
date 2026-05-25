from math import isfinite

from climara.graphics._labelbar_adjust import (
    LabelBarAdjustGeometryNotImplementedError,
    adjust_labelbar_geometry_for_text,
)
from climara.graphics._labelbar_adjust_bridge import (
    build_labelbar_adjust_request_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_adjust_writeback_semantics import (
    compute_labelbar_adjust_writeback_semantics,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = HluLabelBar(
        name="adjust_writeback_semantics",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Writeback title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": 0,
            "lbTitleFuncCode": "@",
            "lbTitleFontHeightF": 0.04,
            "lbLabelDirection": "Across",
            "lbLabelJust": "CenterCenter",
            "lbLabelAngleF": 0,
            "lbLabelFuncCode": "%",
            "lbLabelFontHeightF": 0.03,
        },
    )

    geometry = labelbar.compute_geometry()
    requests = build_labelbar_text_bbox_requests(labelbar)

    assert requests.title is not None
    assert requests.labels.items

    title_metrics = PlotcharExtentMetrics(
        dl=0.12,
        dr=0.18,
        db=0.03,
        dt=0.07,
    )

    label_metrics = tuple(
        PlotcharExtentMetrics(
            dl=0.02,
            dr=0.02,
            db=0.01,
            dt=0.02,
        )
        for _ in requests.labels.items
    )

    bundle = build_labelbar_adjust_request_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    semantics = compute_labelbar_adjust_writeback_semantics(
        bundle.adjust_request,
        justification="CenterCenter",
    )

    perim = semantics.perimeter_semantics

    assert semantics.final_view_bbox.coordinate_space == TEXT_BBOX_COORD_NDC
    assert semantics.final_view_bbox.width >= 0.0
    assert semantics.final_view_bbox.height >= 0.0

    assert len(semantics.final_box_locs) == len(geometry.box_locs)
    assert len(semantics.final_label_locs) == len(geometry.label_locs)

    for original, final in zip(geometry.box_locs, semantics.final_box_locs):
        almost_equal(final, original - perim.major_offset)

    for original, final in zip(geometry.label_locs, semantics.final_label_locs):
        almost_equal(final, original - perim.major_offset)

    assert semantics.final_label_const_pos is not None
    almost_equal(
        semantics.final_label_const_pos,
        geometry.label_const_pos
        + perim.box_semantics.label_pos_offset
        - perim.minor_offset,
    )

    assert semantics.final_title_x is not None
    assert semantics.final_title_y is not None
    almost_equal(
        semantics.final_title_x,
        perim.box_semantics.title_x - perim.x_offset,
    )
    almost_equal(
        semantics.final_title_y,
        perim.box_semantics.title_y - perim.y_offset,
    )

    for value in (
        *semantics.final_box_locs,
        *semantics.final_label_locs,
        semantics.final_label_const_pos,
        semantics.final_title_x,
        semantics.final_title_y,
        semantics.final_view_bbox.l,
        semantics.final_view_bbox.r,
        semantics.final_view_bbox.b,
        semantics.final_view_bbox.t,
    ):
        assert isfinite(value), value

    try:
        adjust_labelbar_geometry_for_text(bundle.adjust_request)
    except LabelBarAdjustGeometryNotImplementedError:
        pass
    else:
        raise AssertionError("live LabelBar AdjustGeometry must remain guarded")

    print("✅ LabelBar AdjustGeometry write-back semantics smoke passed")


if __name__ == "__main__":
    main()
