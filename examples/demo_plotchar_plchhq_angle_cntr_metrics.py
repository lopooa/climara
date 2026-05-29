from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise RuntimeError("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st: PlotcharState, text: str) -> str:
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def main() -> None:
    print("Python PLCHHQ fontcap extent: ANGD/CNTR demo")
    print("This is metrics parity work, not SVG draw-angle rendering.")

    cases = [
        (360.0, -1.0),
        (360.0, 0.0),
        (360.0, 1.0),
        (0.0, -1.0),
        (45.0, -1.0),
        (90.0, -1.0),
    ]

    for angle, cntr in cases:
        st = state()
        result = compute_plchhq_fontcap_text_extent(
            chrs=real_string(st, "ABC"),
            state=st,
            xpos=0.5,
            ypos=0.5,
            size=0.03,
            angle=angle,
            cntr=cntr,
            fontcap_dir=fontcap_dir(),
        )

        m = result.metrics
        print(
            f"ANGD={angle:6.1f} CNTR={cntr:4.1f} "
            f"DL={m.dl:.6f} DR={m.dr:.6f} DB={m.db:.6f} DT={m.dt:.6f}"
        )

    for bad_cntr in (-2.0, 2.0):
        try:
            st = state()
            compute_plchhq_fontcap_text_extent(
                chrs=real_string(st, "ABC"),
                state=st,
                xpos=0.5,
                ypos=0.5,
                size=0.03,
                angle=360.0,
                cntr=bad_cntr,
                fontcap_dir=fontcap_dir(),
            )
        except PlotcharUnsupportedError as exc:
            print(f"guarded CNTR={bad_cntr}: {exc}")
        else:
            raise AssertionError(f"CNTR={bad_cntr} should remain guarded")


if __name__ == "__main__":
    main()
