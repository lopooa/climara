from climara.graphics import HluLabelBar, PlotcharExtentMetrics, build_static_plotchar_metrics_provider
from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_plotchar_metrics import build_labelbar_plotchar_metrics_requests
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine


def main():
    labelbar = HluLabelBar(
        name="hlu_provider_methods",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Provider method title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "~",
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
        },
    )

    requests = build_labelbar_plotchar_metrics_requests(labelbar)

    title_metrics = PlotcharExtentMetrics(dl=0.12, dr=0.18, db=0.03, dt=0.07)
    label_metrics = PlotcharExtentMetrics(dl=0.02, dr=0.02, db=0.01, dt=0.02)

    provider = build_static_plotchar_metrics_provider(
        by_real_string={
            requests.title.semantics.real_string: title_metrics,
        },
        default=label_metrics,
    )

    bundle = labelbar.build_plotchar_metrics_bundle_from_provider(provider)
    assert bundle.title is title_metrics
    assert len(bundle.labels) == len(requests.labels)

    pipeline = labelbar.build_adjust_pipeline_from_plotchar_metrics_provider(provider)
    assert pipeline.source_object is labelbar
    assert isinstance(pipeline.geometry, LabelBarGeometry)

    geometry = labelbar.compute_adjusted_geometry_from_plotchar_metrics_provider(provider)
    assert isinstance(geometry, LabelBarGeometry)
    assert geometry.box_locs == pipeline.geometry.box_locs
    assert geometry.label_locs == pipeline.geometry.label_locs

    svg = labelbar.render_adjusted_svg_from_plotchar_metrics_provider(
        provider,
        width=800,
        height=300,
    )

    assert svg.startswith("<svg ")
    assert "Provider method title" in svg
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg

    assert isinstance(has_plotchar_metrics_engine(), bool)
    assert isinstance(has_text_bbox_engine(), bool)
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ HluLabelBar Plotchar metrics provider methods smoke passed")


if __name__ == "__main__":
    main()
