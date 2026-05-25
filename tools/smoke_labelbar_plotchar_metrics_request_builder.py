from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_plotchar_metrics import (
    build_labelbar_plotchar_metrics_requests,
)
from climara.graphics._plotchar_metrics import (
    PlotcharMetricsNotImplementedError,
    compute_plotchar_extent_metrics,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = HluLabelBar(
        name="plotchar_metrics_request_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Plotchar title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleAngleF": -45,
            "lbTitleFontHeightF": 0.04,
            "lbTitleFuncCode": "@",
            "lbLabelDirection": "Across",
            "lbLabelAngleF": -30,
            "lbLabelFontHeightF": 0.03,
            "lbLabelFuncCode": "%",
        },
    )

    requests = build_labelbar_plotchar_metrics_requests(labelbar)

    assert requests.title is not None
    assert requests.title.semantics.text == "Plotchar title"
    assert requests.title.semantics.real_string == "@A@Plotchar title"
    almost_equal(requests.title.size, 0.04)
    almost_equal(requests.title.angle, 315.0)

    assert requests.labels
    assert requests.labels[0].semantics.text == "A"
    assert requests.labels[0].semantics.real_string == "%A%A"
    almost_equal(requests.labels[0].size, 0.03)
    almost_equal(requests.labels[0].angle, 330.0)

    try:
        compute_plotchar_extent_metrics(requests.title)
    except PlotcharMetricsNotImplementedError as exc:
        message = str(exc)
        assert "Plotchar extent metrics are not implemented" in message
        assert "c_plchhq / c_pcgetr DL, DR, DB, DT" in message
    else:
        raise AssertionError("Plotchar metrics must remain guarded")

    no_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
        },
    )

    no_title_requests = build_labelbar_plotchar_metrics_requests(no_title)

    assert no_title_requests.title is None
    assert no_title_requests.labels

    print("✅ LabelBar Plotchar metrics request builder smoke passed")


if __name__ == "__main__":
    main()
