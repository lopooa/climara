from pathlib import Path
import math

from climara.graphics._plotchar_size_address_provider import NclSourceMappedSizeAddressScaleProvider
from climara.graphics._plotchar_size_runtime_strategy import ProviderBackedSizeAddressRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines
from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg


ADDRESS_RESOLUTION = 1023.0
REFERENCE_FRACTIONAL_SIZE = 0.035


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


def equivalent_negative_size(st: PlotcharState, fractional_size: float) -> float:
    # Match NCL SIZM:
    # fractional: SIZM = SIZE / WPIC(1)
    # SIZE <= 0: SIZM = ABS(SIZE) / 1023
    # therefore ABS(SIZE_NEG) = fractional_size * 1023 / WPIC(1)
    return -float(fractional_size) * ADDRESS_RESOLUTION / float(st.wpic[0])


def equivalent_address_size(fractional_size: float) -> float:
    # Match NCL SIZM:
    # fractional: SIZM = SIZE / WPIC(1)
    # SIZE >= 1: SIZM = (SIZE / RSLN) / WPIC(1)
    # therefore SIZE_ADDR = fractional_size * RSLN
    return float(fractional_size) * ADDRESS_RESOLUTION


def add_anchor(root, x, y, size=0.014):
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


def add_plchhq(root, label, x, y, size, *, angle=360.0):
    st = state()
    provider = NclSourceMappedSizeAddressScaleProvider(
        address_resolution=ADDRESS_RESOLUTION
    )

    result = render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, label),
        state=st,
        xpos=x,
        ypos=y,
        size=size,
        angle=angle,
        cntr=-1.0,
        size_address_runtime_strategy=ProviderBackedSizeAddressRuntimeStrategy(),
        size_address_scale_provider=provider,
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
    st = state()

    frac_size = REFERENCE_FRACTIONAL_SIZE
    neg_size = equivalent_negative_size(st, frac_size)
    addr_size = equivalent_address_size(frac_size)

    print(f"WPIC(1) = {float(st.wpic[0]):.6f}")
    print(f"fractional SIZE = {frac_size:.6f}")
    print(f"equivalent SIZE <= 0 = {neg_size:.6f}")
    print(f"equivalent SIZE >= 1 = {addr_size:.6f}")

    add_plchhq(root, f"fractional {frac_size:.3f}", 0.08, 0.78, frac_size)
    add_plchhq(root, f"negative {neg_size:.3f}", 0.08, 0.56, neg_size)
    add_plchhq(root, f"address {addr_size:.1f}", 0.08, 0.34, addr_size)
    add_plchhq(root, f"address {addr_size:.1f} ANG45", 0.48, 0.20, addr_size, angle=45.0)

    out = Path("outputs/figures/demo_plotchar_size_address_svg_draw.svg")
    save_svg(root, out, width=1200, height=760, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
