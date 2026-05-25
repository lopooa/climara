import subprocess
import sys


def main():
    result = subprocess.run(
        [sys.executable, "tools/report_ncl_source_availability.py"],
        check=True,
        text=True,
        capture_output=True,
    )

    out = result.stdout

    assert "NCL source availability report" in out
    assert "ni/src/lib/hlu/TextItem.c" in out
    assert "ni/src/lib/hlu/MultiText.c" in out
    assert "ni/src/lib/hlu/LabelBar.c" in out
    assert "NCL_SRC_ROOT" in out or "All required NCL source files are available." in out

    print("✅ NCL source availability report smoke passed")


if __name__ == "__main__":
    main()
