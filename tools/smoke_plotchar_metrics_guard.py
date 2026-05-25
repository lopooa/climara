from climara.graphics._plotchar_metrics import (
    PlotcharMetricsNotImplementedError,
    build_plotchar_extent_metrics,
    build_plotchar_metrics_request,
    compute_plotchar_extent_metrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_text_item_semantics(
        "Demo",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=-45,
        font=21,
        font_color="black",
        font_height=0.025,
    )

    request = build_plotchar_metrics_request(
        semantics,
        x=0.5,
        y=0.5,
    )

    assert has_plotchar_metrics_engine() is False
    assert request.semantics.real_string == "~A~Demo"
    almost_equal(request.x, 0.5)
    almost_equal(request.y, 0.5)
    almost_equal(request.size, 0.025)
    almost_equal(request.angle, 315.0)

    extents = build_plotchar_extent_metrics(
        dl=-0.1,
        dr=0.2,
        db=-0.05,
        dt=0.1,
    )

    almost_equal(extents.dl, -0.1)
    almost_equal(extents.dr, 0.2)
    almost_equal(extents.db, -0.05)
    almost_equal(extents.dt, 0.1)
    almost_equal(extents.width, 0.3)
    almost_equal(extents.height, 0.15)

    try:
        build_plotchar_extent_metrics(dl=0.2, dr=-0.1, db=0.0, dt=0.1)
    except ValueError as exc:
        assert "dr >= dl" in str(exc)
    else:
        raise AssertionError("invalid Plotchar horizontal extents should fail")

    try:
        compute_plotchar_extent_metrics(request)
    except PlotcharMetricsNotImplementedError as exc:
        message = str(exc)
        assert "NCL Plotchar extent metrics are not implemented" in message
        assert "c_plchhq / c_pcgetr DL, DR, DB, DT" in message
        assert "do not replace this with fixed-width or SVG text-size heuristics" in message
    else:
        raise AssertionError("Plotchar metrics must remain guarded")

    print("✅ Plotchar metrics guard smoke passed")


if __name__ == "__main__":
    main()
