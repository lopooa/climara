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

    assert "climara TextBBox / Plotchar / LabelBar pipeline status" in out

    assert "text_bbox_engine: False" in out
    assert "plotchar_metrics_engine: False" in out
    assert "labelbar_adjust_geometry_engine: False" in out

    assert "text_bbox_from_supplied_plotchar_metrics: True" in out
    assert "multitext_bbox_from_supplied_plotchar_metrics: True" in out
    assert "labelbar_bbox_from_supplied_plotchar_metrics: True" in out
    assert "labelbar_adjust_execution_from_supplied_bboxes: True" in out
    assert "labelbar_adjust_pipeline_from_supplied_metrics: True" in out
    assert "explicit_adjusted_labelbar_svg_export: True" in out
    assert "default_renderer_uses_adjusted_labelbar: False" in out

    assert "title_text_bbox_request" in out
    assert "real_string: @A@Pipeline title" in out
    assert "label_text_bbox_request_count:" in out
    assert "first_label_text_bbox_request" in out
    assert "real_string: %A%A" in out

    assert "title_plotchar_metrics_request" in out
    assert "label_plotchar_metrics_request_count:" in out

    assert "LabelBar AdjustGeometry supplied-bbox execution is available." in out
    assert "LabelBar AdjustGeometry materialized snapshots are available." in out
    assert "Adjusted LabelBarGeometry snapshots are available." in out
    assert "Explicit adjusted LabelBar SVG primitive adapter is available." in out
    assert "Explicit adjusted LabelBar SVG export is available." in out

    assert "Plotchar DL / DR / DB / DT live metrics are still guarded." in out
    assert "TextItem / MultiText live bbox engines are still guarded." in out
    assert "Default renderer does not use adjusted LabelBar geometry." in out

    print("✅ TextBBox pipeline report smoke passed")


if __name__ == "__main__":
    main()
