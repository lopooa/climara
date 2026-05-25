from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._labelbar_adjust_pipeline import (
    LabelBarSuppliedMetricsAdjustPipeline,
    build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics,
    compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import (
    PlotcharExtentMetrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._text_bbox import has_text_bbox_engine

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    assert_finite_bbox,
    make_labelbar,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_rect_matches_bbox(rect, box):
    almost_equal(rect.l, box.l)
    almost_equal(rect.r, box.r)
    almost_equal(rect.b, box.b)
    almost_equal(rect.t, box.t)


def main():
    labelbar = make_labelbar("adjust_pipeline")
    requests = build_labelbar_text_bbox_requests(labelbar)

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

    pipeline = build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert isinstance(pipeline, LabelBarSuppliedMetricsAdjustPipeline)
    assert pipeline.source_object is labelbar
    assert isinstance(pipeline.geometry, LabelBarGeometry)

    assert pipeline.adjust_result.request is pipeline.supplied_metrics_request.adjust_request
    assert pipeline.materialized.source_geometry is pipeline.supplied_metrics_request.adjust_request.geometry
    assert pipeline.geometry is not pipeline.materialized.source_geometry

    assert_adjust_result(pipeline.adjust_result)

    assert_rect_matches_bbox(
        pipeline.geometry.perim,
        pipeline.materialized.nominal_perim_bbox,
    )
    assert_rect_matches_bbox(
        pipeline.geometry.adj_bar,
        pipeline.materialized.adjusted_bar_bbox,
    )

    assert pipeline.geometry.box_locs == pipeline.materialized.final_box_locs
    assert pipeline.geometry.label_locs == pipeline.materialized.final_label_locs
    assert pipeline.geometry.label_text_positions == pipeline.materialized.final_label_text_positions
    assert pipeline.geometry.title_text_position == pipeline.materialized.final_title_text_position
    assert pipeline.geometry.title_text_item == pipeline.materialized.final_title_text_item

    assert_finite_bbox(pipeline.adjust_result.final_view_bbox)
    assert_finite_bbox(pipeline.materialized.external_view_bbox)
    assert_finite_bbox(pipeline.materialized.nominal_perim_bbox)
    assert_finite_bbox(pipeline.materialized.adjusted_bar_bbox)

    geometry_only = compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert isinstance(geometry_only, LabelBarGeometry)
    assert geometry_only.box_locs == pipeline.geometry.box_locs
    assert geometry_only.label_locs == pipeline.geometry.label_locs
    assert geometry_only.label_const_pos == pipeline.geometry.label_const_pos
    assert geometry_only.label_text_positions == pipeline.geometry.label_text_positions
    assert geometry_only.title_text_position == pipeline.geometry.title_text_position
    assert geometry_only.title_text_item == pipeline.geometry.title_text_item

    orientation = str(pipeline.geometry.multi_text_orientation).strip().lower()

    for loc, placement in zip(pipeline.geometry.label_locs, pipeline.geometry.label_text_positions):
        if orientation in {"yconst", "nhlmtextyconst"}:
            almost_equal(placement.x, loc)
            almost_equal(placement.y, pipeline.geometry.label_const_pos)
        elif orientation in {"xconst", "nhlmtextxconst"}:
            almost_equal(placement.x, pipeline.geometry.label_const_pos)
            almost_equal(placement.y, loc)
        else:
            raise AssertionError(
                f"unexpected MultiText orientation: {pipeline.geometry.multi_text_orientation!r}"
            )

    assert has_plotchar_metrics_engine() is False
    assert has_text_bbox_engine() is False
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ LabelBar supplied-metrics AdjustGeometry pipeline smoke passed")


if __name__ == "__main__":
    main()
