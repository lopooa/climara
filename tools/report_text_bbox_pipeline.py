from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_plotchar_metrics import (
    build_labelbar_plotchar_metrics_requests,
)
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine


def _fmt_request(name, request):
    if request is None:
        print(f"{name}: None")
        return

    sem = request.semantics
    print(f"{name}:")
    print(f"  text: {sem.text}")
    print(f"  real_string: {sem.real_string}")
    print(f"  direction: {sem.direction}")
    print(f"  func_code: {sem.func_code}")
    print(f"  x: {request.x}")
    print(f"  y: {request.y}")
    print(f"  coordinate_space: {getattr(request, 'coordinate_space', 'N/A')}")


def _fmt_plotchar_request(name, request):
    if request is None:
        print(f"{name}: None")
        return

    sem = request.semantics
    print(f"{name}:")
    print(f"  text: {sem.text}")
    print(f"  real_string: {sem.real_string}")
    print(f"  size: {request.size}")
    print(f"  angle: {request.angle}")
    print(f"  x: {request.x}")
    print(f"  y: {request.y}")


def main():
    labelbar = HluLabelBar(
        name="pipeline_status_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Pipeline title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "@",
            "lbTitleFontHeightF": 0.04,
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "%",
            "lbLabelFontHeightF": 0.03,
        },
    )

    text_requests = build_labelbar_text_bbox_requests(labelbar)
    plotchar_requests = build_labelbar_plotchar_metrics_requests(labelbar)

    print("climara TextBBox / Plotchar pipeline status")
    print("=" * 46)
    print()

    print("Engine flags")
    print("-" * 12)
    print(f"text_bbox_engine: {has_text_bbox_engine()}")
    print(f"plotchar_metrics_engine: {has_plotchar_metrics_engine()}")
    print(f"labelbar_adjust_geometry_engine: {has_labelbar_adjust_geometry_engine()}")
    print()

    print("LabelBar TextBBox requests")
    print("-" * 26)
    _fmt_request("title_text_bbox_request", text_requests.title)
    print(f"label_text_bbox_request_count: {len(text_requests.labels.items)}")
    if text_requests.labels.items:
        _fmt_request("first_label_text_bbox_request", text_requests.labels.items[0])
    print()

    print("LabelBar Plotchar metrics requests")
    print("-" * 34)
    _fmt_plotchar_request("title_plotchar_metrics_request", plotchar_requests.title)
    print(f"label_plotchar_metrics_request_count: {len(plotchar_requests.labels)}")
    if plotchar_requests.labels:
        _fmt_plotchar_request(
            "first_label_plotchar_metrics_request",
            plotchar_requests.labels[0],
        )

    print()
    print("Current boundary")
    print("-" * 16)
    print("TextBBox requests are available.")
    print("TextItem bbox semantics from supplied Plotchar metrics are available.")
    print("MultiText bbox semantics from supplied child Plotchar metrics are available.")
    print("LabelBar text bbox semantics from supplied title/label Plotchar metrics are available.")
    print("LabelBar AdjustGeometry requests from supplied text bboxes are available.")
    print("LabelBar AdjustGeometry supplied-bbox box semantics are available.")
    print("Plotchar metrics requests are available.")
    print("Plotchar DL / DR / DB / DT metrics are still guarded.")
    print("TextItem / MultiText bbox engines are still guarded.")
    print("LabelBar AdjustGeometry / AutoManage is still guarded.")


if __name__ == "__main__":
    main()
