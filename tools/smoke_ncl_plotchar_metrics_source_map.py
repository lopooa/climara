from __future__ import annotations

import subprocess
import sys

from climara.graphics._plotchar_source_requirements import (
    plotchar_source_requirements_report,
    plotchar_source_symbols,
    required_plotchar_source_files,
)


def main():
    files = required_plotchar_source_files()
    symbols = plotchar_source_symbols()
    report = plotchar_source_requirements_report()

    assert "ni/src/lib/hlu/TextItem.c" in files
    assert "ncarg2d/src/libncarg/plotchar/plchhq.f" in files
    assert "ncarg2d/src/libncarg/plotchar/pcgetr.f" in files
    assert "ncarg2d/src/libncarg/plotchar/pcsetr.f" in files
    assert "ncarg2d/src/libncarg/plotcharC/c_pcsetc.c" in files
    assert "ncarg2d/src/libncarg/plotcharC/c_pcsetr.c" in files
    assert "ncarg2d/src/libncarg/plotcharC/c_pcseti.c" in files
    assert "ncarg2d/src/libncarg/plotchar/pcsetc.f" in files
    assert "ncarg2d/src/libncarg/plotchar/pcseti.f" in files
    assert "ncarg2d/src/libncarg/plotchar/pcrset.f" in files
    assert "ncarg2d/src/libncarg/plotchar/pcblda.f" in files
    assert "ncarg2d/src/libncarg/plotcharC/c_plchhq.c" in files
    assert "ncarg2d/src/libncarg/plotcharC/c_pcgetr.c" in files

    assert "FigureAndSetTextBBInfo" in symbols
    assert "SUBROUTINE PLCHHQ" in symbols
    assert "SUBROUTINE PCGETR" in symbols
    assert "SUBROUTINE PCSETR" in symbols
    assert "void c_pcsetc" in symbols
    assert "void c_pcsetr" in symbols
    assert "void c_pcseti" in symbols
    assert "SUBROUTINE PCSETC" in symbols
    assert "SUBROUTINE PCSETI" in symbols
    assert "SUBROUTINE PCRSET" in symbols
    assert "c_plchhq" in symbols
    assert "c_pcgetr" in symbols
    assert 'c_pcgetr ("DL - DISTANCE LEFT  ",' in symbols

    assert "DSTL / DSTR / DSTB / DSTT" in report
    assert "ANGD=360" in report
    assert "Do not implement live Plotchar metrics from fixed-width text heuristics" in report

    result = subprocess.run(
        [
            sys.executable,
            "tools/report_ncl_plotchar_metrics_source_map.py",
            "--allow-missing",
            "--max-lines-per-file",
            "20",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    out = result.stdout
    assert "NCL Plotchar metrics source requirements" in out
    assert "Local NCL source availability" in out
    assert "SUBROUTINE PLCHHQ" in out
    assert "SUBROUTINE PCGETR" in out
    assert "c_pcgetr" in out
    assert "NCL_SRC_ROOT" in out or "READY:" in out

    print("✅ NCL Plotchar metrics source map smoke passed")


if __name__ == "__main__":
    main()
