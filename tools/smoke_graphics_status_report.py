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
    assert "TextItem bbox engine" in out
    assert "LabelBar AdjustGeometry implementation" in out
    assert "text_bbox_engine: False" in out
    assert "labelbar_adjust_geometry_engine: False" in out
    assert "PYTHONPATH=src python tools/run_core_smokes.py" in out

    print("✅ graphics status report smoke passed")


if __name__ == "__main__":
    main()
