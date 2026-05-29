from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_size_address_exact_branch_packet.md"


def fontcap_dir() -> Path:
    import os

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")
    return Path(ncl_root) / "common" / "src" / "fontcap"


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st: PlotcharState) -> str:
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def assert_size_guarded(size: float) -> None:
    st = state()

    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(st),
            state=st,
            xpos=0.5,
            ypos=0.5,
            size=size,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
        )
    except PlotcharUnsupportedError as exc:
        assert "SIZE" in str(exc) or "size" in str(exc), str(exc)
    else:
        raise AssertionError(f"address-unit SIZE={size!r} unexpectedly computed")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_size_address_exact_branch.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar SIZE / Address-Unit Exact Branch Packet",
        "Decision",
        "Current Python boundary",
        "Focus windows",
        "Manual implementation checklist",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("SIZE/address exact branch report missing sections: " + ", ".join(missing))

    assert_size_guarded(1.0)
    assert_size_guarded(-1.0)
    assert_size_guarded(0.0)

    print("✅ NCL Plotchar SIZE/address exact branch smoke passed")


if __name__ == "__main__":
    main()
