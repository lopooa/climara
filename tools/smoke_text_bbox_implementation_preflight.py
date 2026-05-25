import subprocess
import sys


def main():
    result = subprocess.run(
        [
            sys.executable,
            "tools/run_text_bbox_implementation_preflight.py",
            "--allow-missing",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    out = result.stdout

    assert "TextBBox implementation preflight" in out
    assert "ni/src/lib/hlu/TextItem.c" in out
    assert "ni/src/lib/hlu/MultiText.c" in out
    assert "ni/src/lib/hlu/LabelBar.c" in out

    assert "FigureAndSetTextBBInfo" in out
    assert "TextItemDraw" in out
    assert "c_plchhq" in out
    assert "c_pcgetr" in out
    assert "GetMaxTextLength" in out
    assert "SetDrawFlags" in out
    assert "AdjustGeometry" in out
    assert "NhlGetBB" in out

    assert "NCL_SRC_ROOT" in out or "READY:" in out

    print("✅ TextBBox implementation preflight smoke passed")


if __name__ == "__main__":
    main()
