from pathlib import Path
from tempfile import TemporaryDirectory

from climara.graphics import HluLabelBar, PlotcharExtentMetrics
from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_plotchar_metrics_bundle import LabelBarPlotcharMetricsBundle
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine


def main():
    labelbar = HluLabelBar(
        name="hlu_labelbar_adjusted_methods",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Object API title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "~",
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
            "lbJustification": "CenterCenter",
        },
    )

    title_metrics = PlotcharExtentMetrics(
        dl=0.12,
        dr=0.18,
        db=0.03,
        dt=0.07,
    )

    label_metrics = PlotcharExtentMetrics(
        dl=0.02,
        dr=0.02,
        db=0.01,
        dt=0.02,
    )

    bundle = labelbar.build_uniform_plotchar_metrics_bundle(
        title=title_metrics,
        label=label_metrics,
    )

    assert isinstance(bundle, LabelBarPlotcharMetricsBundle)
    assert labelbar.validate_plotchar_metrics_bundle(bundle) is bundle

    pipeline = labelbar.build_adjust_pipeline_from_plotchar_metrics_bundle(bundle)
    assert pipeline.source_object is labelbar
    assert isinstance(pipeline.geometry, LabelBarGeometry)

    geometry = labelbar.compute_adjusted_geometry_from_plotchar_metrics_bundle(bundle)
    assert isinstance(geometry, LabelBarGeometry)
    assert geometry.box_locs == pipeline.geometry.box_locs
    assert geometry.label_locs == pipeline.geometry.label_locs
    assert geometry.label_text_positions == pipeline.geometry.label_text_positions

    svg = labelbar.render_adjusted_svg_from_plotchar_metrics_bundle(
        bundle,
        width=800,
        height=300,
    )

    assert svg.startswith("<svg ")
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg
    assert "Object API title" in svg
    assert "<polygon " in svg
    assert "<line " in svg
    assert "<text " in svg

    explicit_bundle = labelbar.build_plotchar_metrics_bundle(
        title=title_metrics,
        labels=bundle.labels,
    )

    assert labelbar.validate_plotchar_metrics_bundle(explicit_bundle) is explicit_bundle

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "object_api_adjusted_labelbar.svg"
        output = labelbar.save_adjusted_svg_from_plotchar_metrics_bundle(
            bundle,
            path,
            width=800,
            height=300,
        )

        assert output == path
        assert output.exists()
        assert output.read_text(encoding="utf-8") == svg

    assert isinstance(has_plotchar_metrics_engine(), bool)
    assert isinstance(has_text_bbox_engine(), bool)
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ HluLabelBar object-oriented adjusted methods smoke passed")


if __name__ == "__main__":
    main()
