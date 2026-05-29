from __future__ import annotations

from pathlib import Path

from climara.graphics.mapped_plotchar import (
    NclCoordinateTransformDirectionContract,
    NclWindowViewportState,
    build_ncl_linear_mapped_backend_config,
    compute_plchhq_with_ncl_linear_mapping,
)
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState


def fontcap_dir() -> Path:
    import os

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")
    return Path(ncl_root) / "common" / "src" / "fontcap"


def contract() -> NclCoordinateTransformDirectionContract:
    return NclCoordinateTransformDirectionContract(
        cfux="user-to-fractional-x",
        cfuy="user-to-fractional-y",
        cufx="fractional-to-user-x",
        cufy="fractional-to-user-y",
        getset="viewport-window-read",
        set_call="viewport-window-write",
        source_map_reference="docs/ncl_coordinate_transform_formula_audit.md",
        manually_verified=True,
    )


def viewport() -> NclWindowViewportState:
    return NclWindowViewportState(
        viewport_left=0.2,
        viewport_right=0.8,
        viewport_bottom=0.1,
        viewport_top=0.9,
        window_left=0.0,
        window_right=10.0,
        window_bottom=100.0,
        window_top=200.0,
        log_scaling_flag=1,
    )


def state_with_ma(value: int) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", value)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    config = build_ncl_linear_mapped_backend_config(
        window_viewport_state=viewport(),
        direction_contract=contract(),
    )

    mapped_state = state_with_ma(1)

    mapped = compute_plchhq_with_ncl_linear_mapping(
        chrs=real_string(mapped_state),
        state=mapped_state,
        xpos=5.0,
        ypos=150.0,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        config=config,
        fontcap_dir=fontcap_dir(),
    )

    core_state = state_with_ma(0)
    core = compute_plchhq_fontcap_text_extent(
        chrs=real_string(core_state),
        state=core_state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )

    assert mapped.text == core.text
    assert mapped.font_number == core.font_number
    assert mapped.glyph_count == core.glyph_count

    assert abs(mapped.metrics.dl - core.metrics.dl * (10.0 / 0.6)) < 1e-10
    assert abs(mapped.metrics.dr - core.metrics.dr * (10.0 / 0.6)) < 1e-10
    assert abs(mapped.metrics.db - core.metrics.db * (100.0 / 0.8)) < 1e-10
    assert abs(mapped.metrics.dt - core.metrics.dt * (100.0 / 0.8)) < 1e-10

    print("✅ Python Plotchar mapped public facade smoke passed")


if __name__ == "__main__":
    main()
