from pathlib import Path
from tempfile import TemporaryDirectory

from climara.graphics import (
    HluLabelBar,
    PlotcharExtentMetrics,
    StaticPlotcharMetricsProvider,
    build_labelbar_adjust_pipeline_from_plotchar_metrics_provider,
    build_labelbar_plotchar_metrics_bundle_from_provider,
    build_static_plotchar_metrics_provider,
    compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider,
    render_adjusted_labelbar_svg_from_plotchar_metrics_provider,
    save_adjusted_labelbar_svg_from_plotchar_metrics_provider,
)
from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_plotchar_metrics import build_labelbar_plotchar_metrics_requests
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._plotchar_metrics_provider import PlotcharMetricsProviderError

from _smoke_labelbar_adjust_helpers import assert_adjust_result, make_labelbar


def main():
    labelbar = make_labelbar("metrics_provider")
    requests = build_labelbar_plotchar_metrics_requests(labelbar)

    title_metrics = PlotcharExtentMetrics(dl=0.12, dr=0.18, db=0.03, dt=0.07)
    label_metrics = PlotcharExtentMetrics(dl=0.02, dr=0.02, db=0.01, dt=0.02)

    provider = build_static_plotchar_metrics_provider(
        by_real_string={
            requests.title.semantics.real_string: title_metrics,
        },
        default=label_metrics,
    )

    assert isinstance(provider, StaticPlotcharMetricsProvider)

    bundle = build_labelbar_plotchar_metrics_bundle_from_provider(
        labelbar,
        provider,
    )

    assert bundle.title is title_metrics
    assert len(bundle.labels) == len(requests.labels)
    assert all(item is label_metrics for item in bundle.labels)

    pipeline = build_labelbar_adjust_pipeline_from_plotchar_metrics_provider(
        labelbar,
        provider,
    )

    assert pipeline.source_object is labelbar
    assert isinstance(pipeline.geometry, LabelBarGeometry)
    assert_adjust_result(pipeline.adjust_result)

    geometry = compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider(
        labelbar,
        provider,
    )

    assert isinstance(geometry, LabelBarGeometry)
    assert geometry.box_locs == pipeline.geometry.box_locs
    assert geometry.label_locs == pipeline.geometry.label_locs

    svg = render_adjusted_labelbar_svg_from_plotchar_metrics_provider(
        labelbar,
        provider,
        width=800,
        height=300,
    )

    assert svg.startswith("<svg ")
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg
    assert "<polygon " in svg
    assert "<line " in svg
    assert "<text " in svg

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "provider_adjusted_labelbar.svg"
        output = save_adjusted_labelbar_svg_from_plotchar_metrics_provider(
            labelbar,
            provider,
            path,
            width=800,
            height=300,
        )

        assert output == path
        assert output.exists()
        assert output.read_text(encoding="utf-8") == svg

    title_real_string = requests.title.semantics.real_string

    def callable_provider(request):
        if request.semantics.real_string == title_real_string:
            return title_metrics
        return label_metrics

    callable_bundle = build_labelbar_plotchar_metrics_bundle_from_provider(
        labelbar,
        callable_provider,
    )

    assert callable_bundle.title is title_metrics
    assert len(callable_bundle.labels) == len(requests.labels)

    missing = build_static_plotchar_metrics_provider(
        by_real_string={},
        default=None,
    )

    try:
        build_labelbar_plotchar_metrics_bundle_from_provider(
            labelbar,
            missing,
        )
    except PlotcharMetricsProviderError as exc:
        assert "No Plotchar metrics available" in str(exc)
    else:
        raise AssertionError("missing provider metrics should fail")

    assert has_plotchar_metrics_engine() is False
    assert has_text_bbox_engine() is False
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ LabelBar Plotchar metrics provider smoke passed")


if __name__ == "__main__":
    main()
