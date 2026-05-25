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
    assert "Plotchar DL / DR / DB / DT metrics are still guarded." in out
    assert "LabelBar AdjustGeometry / AutoManage is still guarded." in out

    print("✅ TextBBox pipeline report smoke passed")


if __name__ == "__main__":
    main()
