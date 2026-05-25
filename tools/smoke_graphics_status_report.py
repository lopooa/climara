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
    assert "no Matplotlib runtime" in out
    assert "shared TextItem semantics helper" in out
    assert "LabelBar text bbox request builder" in out
    assert "Plotchar metrics request boundary" in out
    assert "TextItem bbox semantics from supplied Plotchar metrics" in out
    assert "MultiText bbox semantics from supplied child Plotchar metrics" in out
    assert "LabelBar Plotchar metrics request builder" in out
    assert "LabelBar text bbox semantics from supplied Plotchar metrics" in out
    assert "LabelBar AdjustGeometry request bridge from supplied text bboxes" in out
    assert "LabelBar AdjustGeometry supplied-bbox box semantics" in out
    assert "LabelBar AdjustGeometry write-back into LabelBarGeometry / child objects" in out
    assert "LabelBar AdjustGeometry execution from supplied text bboxes" in out

    assert "TextItem bbox engine using live Plotchar metrics" in out
    assert "NCL Plotchar DL / DR / DB / DT metrics engine" in out
    assert "LabelBar AdjustGeometry implementation" in out
    assert "Text bbox feedback into LabelBar geometry / AdjustGeometry" in out

    assert "text_bbox_engine: False" in out
    assert "plotchar_metrics_engine: False" in out
    assert "labelbar_adjust_geometry_engine: False" in out

    assert "PYTHONPATH=src python tools/run_core_smokes.py" in out

    print("✅ graphics status report smoke passed")


if __name__ == "__main__":
    main()
