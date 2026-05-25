from climara.graphics._plotchar_metrics import compute_plotchar_extent_metrics, PlotcharMetricsNotImplementedError
from climara.graphics._text_bbox import build_text_item_bbox_request
from climara.graphics._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_text_item_semantics(
        "Bridge",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=-45,
        font=21,
        font_color="black",
        font_height=0.025,
        font_aspect=1.3125,
        font_thickness=1.0,
        font_quality="High",
        constant_spacing=0.0,
    )

    bbox_request = build_text_item_bbox_request(
        semantics,
        x=0.4,
        y=0.6,
    )

    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(
        bbox_request
    )

    assert plotchar_request.semantics is bbox_request.semantics
    assert plotchar_request.semantics.real_string == "~A~Bridge"
    almost_equal(plotchar_request.x, 0.4)
    almost_equal(plotchar_request.y, 0.6)
    almost_equal(plotchar_request.size, 0.025)
    almost_equal(plotchar_request.angle, 315.0)

    try:
        compute_plotchar_extent_metrics(plotchar_request)
    except PlotcharMetricsNotImplementedError as exc:
        message = str(exc)
        assert "Plotchar extent metrics are not implemented" in message
        assert "c_plchhq / c_pcgetr DL, DR, DB, DT" in message
    else:
        raise AssertionError("Plotchar metrics must remain guarded")

    print("✅ TextBBox -> Plotchar metrics bridge smoke passed")


if __name__ == "__main__":
    main()
