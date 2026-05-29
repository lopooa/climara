from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_mapped_label_resolution.md"


def fontcap_dir() -> Path:
    import os

    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def assert_mapped_still_guarded() -> None:
    state = mapped_state()

    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(state),
            state=state,
            xpos=0.5,
            ypos=0.5,
            size=0.03,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
        )
    except PlotcharUnsupportedError as exc:
        assert "IMAP == 0" in str(exc), str(exc)
    else:
        raise AssertionError("IMAP != 0 must remain guarded")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_mapped_label_resolution.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "NCL Plotchar Mapped Branch Label Resolution",
        "Resolution decision",
        "Labels previously reported as missing",
        "Rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Mapped label resolution report missing required sections: "
            + ", ".join(missing)
        )

    assert_mapped_still_guarded()

    print("✅ NCL Plotchar mapped label-resolution smoke passed")


if __name__ == "__main__":
    main()
