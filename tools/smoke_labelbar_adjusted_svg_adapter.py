from climara.graphics._labelbar_adjust_pipeline import (
    compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_geometry import LabelBarGeometry
from climara.graphics._labelbar_svg_adapter import (
    SvgLabelBarPrimitives,
    labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics,
    labelbar_to_svg_primitives,
)
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine

from _smoke_labelbar_adjust_helpers import make_labelbar


def main():
    labelbar = make_labelbar("adjusted_svg_adapter")
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

    adjusted_geometry = compute_labelbar_adjusted_geometry_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert isinstance(adjusted_geometry, LabelBarGeometry)

    default_primitives = labelbar_to_svg_primitives(
        labelbar,
        800,
        300,
    )

    adjusted_primitives = labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics(
        labelbar,
        800,
        300,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert isinstance(default_primitives, SvgLabelBarPrimitives)
    assert isinstance(adjusted_primitives, SvgLabelBarPrimitives)

    assert adjusted_primitives.polygons
    assert adjusted_primitives.lines
    assert adjusted_primitives.texts

    assert len(adjusted_primitives.polygons) == len(default_primitives.polygons)
    assert len(adjusted_primitives.texts) == len(default_primitives.texts)

    assert adjusted_primitives.orientation == adjusted_geometry.orientation
    assert adjusted_primitives.label_alignment == adjusted_geometry.label_alignment
    assert adjusted_primitives.label_position == adjusted_geometry.label_position

    adjusted_text_points = tuple((item.x, item.y) for item in adjusted_primitives.texts)
    default_text_points = tuple((item.x, item.y) for item in default_primitives.texts)

    assert adjusted_text_points != default_text_points

    for item in adjusted_primitives.texts:
        assert item.real_string is not None
        assert item.func_code is not None
        assert item.direction in {"Across", "Down"}

    assert isinstance(has_plotchar_metrics_engine(), bool)
    assert isinstance(has_text_bbox_engine(), bool)
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ explicit adjusted LabelBar SVG adapter smoke passed")


if __name__ == "__main__":
    main()
