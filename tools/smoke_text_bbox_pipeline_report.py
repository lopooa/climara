import subprocess
import sys


def main():
    result = subprocess.run(
        [sys.executable, "tools/report_text_bbox_pipeline.py"],
        check=True,
        text=True,
        capture_output=True,
    )

    out = result.stdout

    assert "climara TextBBox / Plotchar pipeline status" in out
    assert "text_bbox_engine: False" in out
    assert "plotchar_metrics_engine: False" in out
    assert "labelbar_adjust_geometry_engine: False" in out

    assert "title_text_bbox_request" in out
    assert "real_string: @A@Pipeline title" in out
    assert "label_text_bbox_request_count:" in out
    assert "first_label_text_bbox_request" in out
    assert "real_string: %A%A" in out

    assert "title_plotchar_metrics_request" in out
    assert "label_plotchar_metrics_request_count:" in out
    assert "LabelBar text bbox semantics from supplied title/label Plotchar metrics are available." in out
    assert "LabelBar AdjustGeometry requests from supplied text bboxes are available." in out
    assert "LabelBar AdjustGeometry supplied-bbox box semantics are available." in out
    assert "MultiText bbox semantics from supplied child Plotchar metrics are available." in out
    assert "TextItem bbox semantics from supplied Plotchar metrics are available." in out
    assert "Plotchar DL / DR / DB / DT metrics are still guarded." in out
    assert "LabelBar AdjustGeometry / AutoManage is still guarded." in out

    print("✅ TextBBox pipeline report smoke passed")


if __name__ == "__main__":
    main()
