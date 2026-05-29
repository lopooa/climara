from pathlib import Path
from tempfile import TemporaryDirectory

from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_plotchar_metrics_bundle import (
    LabelBarPlotcharMetricsBundle,
    build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle,
    build_labelbar_plotchar_metrics_bundle,
    build_uniform_labelbar_plotchar_metrics_bundle,
    compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle,
    render_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
    save_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
    validate_labelbar_plotchar_metrics_bundle,
)
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import (
    PlotcharExtentMetrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine

from _smoke_labelbar_adjust_helpers import assert_adjust_result, make_labelbar


def main():
    labelbar = make_labelbar("metrics_bundle")
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

    bundle = build_labelbar_plotchar_metrics_bundle(
        title=title_metrics,
        labels=label_metrics,
    )

    assert isinstance(bundle, LabelBarPlotcharMetricsBundle)
    assert validate_labelbar_plotchar_metrics_bundle(labelbar, bundle) is bundle

    pipeline = build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
    )

    assert pipeline.source_object is labelbar
    assert_adjust_result(pipeline.adjust_result)
    assert isinstance(pipeline.geometry, LabelBarGeometry)

    geometry = compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
    )

    assert isinstance(geometry, LabelBarGeometry)
    assert geometry.box_locs == pipeline.geometry.box_locs
    assert geometry.label_locs == pipeline.geometry.label_locs
    assert geometry.label_text_positions == pipeline.geometry.label_text_positions

    svg = render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
        width=800,
        height=300,
    )

    assert svg.startswith("<svg ")
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg
    assert "<polygon " in svg
    assert "<line " in svg
    assert "<text " in svg

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle_adjusted_labelbar.svg"
        output = save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
            labelbar,
            bundle,
            path,
            width=800,
            height=300,
        )
        assert output == path
        assert output.exists()
        assert output.read_text(encoding="utf-8") == svg

    uniform_bundle = build_uniform_labelbar_plotchar_metrics_bundle(
        labelbar,
        title=title_metrics,
        label=PlotcharExtentMetrics(dl=0.02, dr=0.02, db=0.01, dt=0.02),
    )

    assert len(uniform_bundle.labels) == len(requests.labels.items)
    validate_labelbar_plotchar_metrics_bundle(labelbar, uniform_bundle)

    try:
        validate_labelbar_plotchar_metrics_bundle(
            labelbar,
            build_labelbar_plotchar_metrics_bundle(
                title=title_metrics,
                labels=label_metrics[:1],
            ),
        )
    except ValueError as exc:
        assert "label count mismatch" in str(exc)
    else:
        raise AssertionError("mismatched label metrics bundle should fail")

    try:
        validate_labelbar_plotchar_metrics_bundle(
            labelbar,
            build_labelbar_plotchar_metrics_bundle(
                title=None,
                labels=label_metrics,
            ),
        )
    except ValueError as exc:
        assert "missing title metrics" in str(exc)
    else:
        raise AssertionError("missing title metrics should fail")

    no_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf"],
        labels=["A", "B"],
        resources={
            "lbTitleOn": False,
        },
    )
    no_title_requests = build_labelbar_text_bbox_requests(no_title)

    no_title_bundle = build_labelbar_plotchar_metrics_bundle(
        labels=tuple(
            PlotcharExtentMetrics(dl=0.01, dr=0.01, db=0.01, dt=0.01)
            for _ in no_title_requests.labels.items
        ),
    )

    validate_labelbar_plotchar_metrics_bundle(no_title, no_title_bundle)

    try:
        validate_labelbar_plotchar_metrics_bundle(
            no_title,
            build_labelbar_plotchar_metrics_bundle(
                title=title_metrics,
                labels=no_title_bundle.labels,
            ),
        )
    except ValueError as exc:
        assert "has no title TextBBox request" in str(exc)
    else:
        raise AssertionError("title metrics for no-title labelbar should fail")

    assert isinstance(has_plotchar_metrics_engine(), bool)
    assert isinstance(has_text_bbox_engine(), bool)
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ LabelBar Plotchar metrics bundle smoke passed")


if __name__ == "__main__":
    main()
