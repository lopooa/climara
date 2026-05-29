from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]


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


def compute(size: float):
    st = state()
    return compute_plchhq_fontcap_text_extent(
        chrs=real_string(st),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=size,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )


def assert_source_handoff_exists() -> None:
    source = (ROOT / "src" / "climara" / "graphics" / "_plotchar_plchhq_extent.py").read_text(encoding="utf-8")
    assert "size_address_unit_requested(size)" in source
    assert "build_size_address_unit_request" in source
    assert "compute_size_address_unit_extent(request)" in source


def assert_size_guarded(size: float) -> None:
    try:
        compute(size)
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert "address-unit SIZE is not implemented" in message, message
        assert "0 < SIZE < 1" in message, message
        assert "ncl_plotchar_size_address_exact_branch_packet.md" in message, message
    else:
        raise AssertionError(f"SIZE={size!r} unexpectedly bypassed SIZE/address handoff guard")


def main() -> None:
    assert_source_handoff_exists()

    fractional = compute(0.03)
    assert fractional.metrics.width > 0.0
    assert fractional.metrics.height > 0.0

    assert_size_guarded(1.0)
    assert_size_guarded(0.0)
    assert_size_guarded(-1.0)

    print("✅ Python Plotchar SIZE/address runtime handoff smoke passed")


if __name__ == "__main__":
    main()
