from climara.graphics import (
    HluLabelBar,
    PlotcharExtentMetrics,
    build_plotchar_extent_metrics,
    build_uniform_labelbar_plotchar_metrics_bundle,
    render_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
)
from climara.graphics import (
    has_labelbar_adjust_geometry_engine,
    has_plotchar_metrics_engine,
)
from climara.graphics._text_bbox import has_text_bbox_engine


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    extents = build_plotchar_extent_metrics(
        dl=0.1,
        dr=0.3,
        db=0.05,
        dt=0.15,
    )

    assert isinstance(extents, PlotcharExtentMetrics)
    almost_equal(extents.width, 0.4)
    almost_equal(extents.height, 0.2)

    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Public metrics API",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "~",
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
        },
    )

    bundle = build_uniform_labelbar_plotchar_metrics_bundle(
        labelbar,
        title=PlotcharExtentMetrics(dl=0.12, dr=0.18, db=0.03, dt=0.07),
        label=PlotcharExtentMetrics(dl=0.02, dr=0.02, db=0.01, dt=0.02),
    )

    svg = render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
        labelbar,
        bundle,
        width=800,
        height=300,
    )

    assert svg.startswith("<svg ")
    assert "Public metrics API" in svg
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg

    assert isinstance(has_plotchar_metrics_engine(), bool)
    assert isinstance(has_text_bbox_engine(), bool)
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ public Plotchar metrics API smoke passed")


if __name__ == "__main__":
    main()
