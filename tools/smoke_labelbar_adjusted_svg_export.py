from pathlib import Path
from tempfile import TemporaryDirectory

from climara.graphics import (
    render_adjusted_labelbar_svg_from_supplied_plotchar_metrics,
    save_adjusted_labelbar_svg_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import (
    PlotcharExtentMetrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine

from _smoke_labelbar_adjust_helpers import make_labelbar


def main():
    labelbar = make_labelbar("adjusted_svg_export")
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

    svg = render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        width=800,
        height=300,
    )

    assert svg.startswith("<svg ")
    assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg
    assert "<polygon " in svg
    assert "<line " in svg
    assert "<text " in svg
    assert "Adjust title" in svg
    assert 'data-ncl-real-string="@A@Adjust title"' in svg
    assert 'data-ncl-func-code="@"' in svg
    assert 'data-ncl-direction="Across"' in svg

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "adjusted_labelbar.svg"

        output = save_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
            labelbar,
            path,
            title_metrics=title_metrics,
            label_metrics=label_metrics,
            width=800,
            height=300,
        )

        assert output == path
        assert output.exists()
        saved = output.read_text(encoding="utf-8")
        assert saved == svg

    assert has_plotchar_metrics_engine() is False
    assert has_text_bbox_engine() is False
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ adjusted LabelBar SVG export smoke passed")


if __name__ == "__main__":
    main()
