from pathlib import Path
from tempfile import TemporaryDirectory

from climara.graphics import (
    HluLabelBar,
    LabelBarPlotcharMetricsBundle,
    build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle,
    build_labelbar_plotchar_metrics_bundle,
    build_uniform_labelbar_plotchar_metrics_bundle,
    compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle,
    render_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
    render_adjusted_labelbar_svg_from_supplied_plotchar_metrics,
    save_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
    save_adjusted_labelbar_svg_from_supplied_plotchar_metrics,
    validate_labelbar_plotchar_metrics_bundle,
)
from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine


def main():
    labelbar = HluLabelBar(
        name="public_api_adjusted_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Public API title",
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
            "lbJustification": "CenterCenter",
        },
    )

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

    uniform_bundle = build_uniform_labelbar_plotchar_metrics_bundle(
        labelbar,
        title=title_metrics,
        label=PlotcharExtentMetrics(
            dl=0.02,
            dr=0.02,
            db=0.01,
            dt=0.02,
        ),
    )

    assert len(uniform_bundle.labels) == len(label_metrics)

    pipeline = build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
    )

    assert pipeline.source_object is labelbar
    assert isinstance(pipeline.geometry, LabelBarGeometry)

    geometry = compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
    )

    assert isinstance(geometry, LabelBarGeometry)
    assert geometry.box_locs == pipeline.geometry.box_locs
    assert geometry.label_locs == pipeline.geometry.label_locs
    assert geometry.label_text_positions == pipeline.geometry.label_text_positions

    svg_from_bundle = render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
        width=800,
        height=300,
    )

    svg_from_supplied = render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        width=800,
        height=300,
    )

    assert svg_from_bundle == svg_from_supplied
    assert svg_from_bundle.startswith("<svg ")
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg_from_bundle
    assert "Public API title" in svg_from_bundle
    assert "<polygon " in svg_from_bundle
    assert "<line " in svg_from_bundle
    assert "<text " in svg_from_bundle

    with TemporaryDirectory() as tmp:
        bundle_path = Path(tmp) / "bundle.svg"
        supplied_path = Path(tmp) / "supplied.svg"

        bundle_out = save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
            labelbar,
            bundle,
            bundle_path,
            width=800,
            height=300,
        )

        supplied_out = save_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
            labelbar,
            supplied_path,
            title_metrics=title_metrics,
            label_metrics=label_metrics,
            width=800,
            height=300,
        )

        assert bundle_out == bundle_path
        assert supplied_out == supplied_path
        assert bundle_out.exists()
        assert supplied_out.exists()
        assert bundle_out.read_text(encoding="utf-8") == supplied_out.read_text(encoding="utf-8")

    assert has_plotchar_metrics_engine() is False
    assert has_text_bbox_engine() is False
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ adjusted LabelBar public API smoke passed")


if __name__ == "__main__":
    main()
