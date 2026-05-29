from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st, body):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{body}"


def compute(body):
    st = state()
    return compute_plchhq_fontcap_text_extent(
        chrs=real_string(st, body),
        state=st,
        xpos=0.5,
        ypos=0.5,
        size=0.045,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=Path("/mnt/d/Projects/NCL/common/src/fontcap"),
    )


def width(metrics):
    return metrics.dl + metrics.dr


def height(metrics):
    return metrics.db + metrics.dt


def main():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    cases = [
        ("plain", "ABC"),
        ("hmove", f"A{code}H15{code}BC"),
        ("vmove", f"A{code}V10{code}BC"),
        ("xzoom", f"A{code}X130{code}BC"),
        ("yzoom", f"A{code}Y80{code}BC"),
        ("zzoom", f"A{code}Z130{code}BC"),
        ("carriage", f"Line1{code}C{code}Line2"),
    ]

    results = {}

    for name, body in cases:
        result = compute(body)
        results[name] = result
        m = result.metrics
        print(
            f"{name:10s} text={result.text!r} "
            f"DL={m.dl:.6f} DR={m.dr:.6f} DB={m.db:.6f} DT={m.dt:.6f} "
            f"W={width(m):.6f} H={height(m):.6f}"
        )

    if width(results["xzoom"].metrics) <= width(results["plain"].metrics):
        raise AssertionError("X130 should increase width relative to plain")

    if height(results["zzoom"].metrics) <= height(results["plain"].metrics):
        raise AssertionError("Z130 should increase height relative to plain")

    if height(results["carriage"].metrics) <= height(results["plain"].metrics):
        raise AssertionError("carriage return should increase vertical extent")

    print()
    print("✅ H/V/X/Y/Z/C metrics demo passed")


if __name__ == "__main__":
    main()
