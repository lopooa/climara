from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


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


def fontcap_dir() -> Path:
    return Path("/mnt/d/Projects/NCL/common/src/fontcap")


def main() -> None:
    print("SIZE/address-unit boundary demo")
    print("This is not full NCL SIZE/address parity.")
    print()

    for size in [0.03, 1.0, -12.0]:
        st = state()

        try:
            result = compute_plchhq_fontcap_text_extent(
                chrs=real_string(st, "ABC"),
                state=st,
                xpos=0.5,
                ypos=0.5,
                size=size,
                angle=360.0,
                cntr=-1.0,
                fontcap_dir=fontcap_dir(),
            )

            m = result.metrics
            print(
                f"SIZE={size:7.3f} OK "
                f"DL={m.dl:.6f} DR={m.dr:.6f} DB={m.db:.6f} DT={m.dt:.6f}"
            )

        except PlotcharUnsupportedError as exc:
            print(f"SIZE={size:7.3f} guarded: {exc}")


if __name__ == "__main__":
    main()
