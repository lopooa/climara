import subprocess
import sys


def main():
    result = subprocess.run(
        [sys.executable, "tools/report_graphics_status.py"],
        check=True,
        text=True,
        capture_output=True,
    )

    out = result.stdout

    assert "climara graphics status" in out

    assert "TextItem bbox semantics from supplied Plotchar metrics" in out
    assert "MultiText bbox semantics from supplied child Plotchar metrics" in out
    assert "LabelBar text bbox semantics from supplied title/label Plotchar metrics" in out

    assert "LabelBar AdjustGeometry request bridge from supplied text bboxes" in out
    assert "LabelBar AdjustGeometry supplied-bbox box semantics" in out
    assert "LabelBar AdjustGeometry perimeter / justification semantics from supplied bboxes" in out
    assert "LabelBar AdjustGeometry write-back semantics from supplied bboxes" in out
    assert "LabelBar AdjustGeometry supplied-bbox execution result" in out
    assert "LabelBar AdjustGeometry materialized snapshot" in out
    assert "LabelBar AdjustGeometry applied LabelBarGeometry snapshot" in out
    assert "LabelBar supplied-metrics AdjustGeometry pipeline" in out

    assert "explicit adjusted LabelBar SVG primitive adapter" in out
    assert "explicit adjusted LabelBar SVG file export" in out

    assert "NCL Plotchar DL / DR / DB / DT metrics engine" in out
    assert "TextItem bbox engine using live Plotchar metrics" in out
    assert "MultiText bbox engine using live child TextItem bbox results" in out
    assert "default renderer integration for adjusted LabelBar geometry" in out

    assert "text_bbox_engine: False" in out
    assert "plotchar_metrics_engine: False" in out
    assert "labelbar_adjust_geometry_engine: False" in out
    assert "supplied-bbox AdjustGeometry execution path is explicit and opt-in" in out

    print("✅ graphics status report smoke passed")


if __name__ == "__main__":
    main()
