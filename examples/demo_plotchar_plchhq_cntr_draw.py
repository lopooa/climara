from pathlib import Path
import math

from climara.graphics._plotchar_state import PlotcharState
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines
from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st, text):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def add_anchor(root, x, y, size=0.018):
    root.add_child(
        build_polyline(
            [x - size, x + size],
            [y, y],
            resources={"gsLineColor": "red", "gsLineThicknessF": 1.0},
        )
    )
    root.add_child(
        build_polyline(
            [x, x],
            [y - size, y + size],
            resources={"gsLineColor": "red", "gsLineThicknessF": 1.0},
        )
    )


def add_metrics_bbox(root, x, y, metrics, angle):
    if math.isclose(angle, 360.0, abs_tol=1e-12):
        angle = 0.0

    radians = math.radians(angle)
    coso = math.cos(radians)
    sino = math.sin(radians)

    offsets = [
        (-metrics.dl, -metrics.db),
        (+metrics.dr, -metrics.db),
        (+metrics.dr, +metrics.dt),
        (-metrics.dl, +metrics.dt),
        (-metrics.dl, -metrics.db),
    ]

    xs = []
    ys = []
    for u, v in offsets:
        xs.append(x + u * coso - v * sino)
        ys.append(y + u * sino + v * coso)

    root.add_child(
        build_polyline(
            xs,
            ys,
            resources={"gsLineColor": "blue", "gsLineThicknessF": 0.8},
        )
    )


def add_plchhq(root, text, x, y, cntr, angle=360.0):
    st = state()
    result = render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, text),
        state=st,
        xpos=x,
        ypos=y,
        size=0.035,
        angle=angle,
        cntr=cntr,
    )

    add_anchor(root, x, y)
    add_metrics_bbox(root, x, y, result.metrics, angle)

    for poly in result.polylines:
        xs = [point[0] for point in poly.points]
        ys = [point[1] for point in poly.points]
        root.add_child(
            build_polyline(
                xs,
                ys,
                resources={"gsLineColor": "black", "gsLineThicknessF": 1.0},
            )
        )


def main():
    root = HluPrimitive()

    add_plchhq(root, "CNTR -1", 0.20, 0.72, -1.0)
    add_plchhq(root, "CNTR 0", 0.50, 0.72, 0.0)
    add_plchhq(root, "CNTR 1", 0.80, 0.72, 1.0)

    add_plchhq(root, "H~B~2~N~O -1", 0.20, 0.42, -1.0)
    add_plchhq(root, "H~B~2~N~O 0", 0.50, 0.42, 0.0)
    add_plchhq(root, "H~B~2~N~O 1", 0.80, 0.42, 1.0)

    add_plchhq(root, "CNTR 0 ANG 45", 0.42, 0.18, 0.0, angle=45.0)

    out = Path("outputs/figures/demo_plotchar_plchhq_cntr_draw.svg")
    save_svg(root, out, width=1400, height=760, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
