from __future__ import annotations

import os
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
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise RuntimeError("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running this example.")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def verified_direction_contract() -> NclCoordinateTransformDirectionContract:
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


def window_viewport_state() -> NclWindowViewportState:
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


def plotchar_state(*, mapped: bool) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1 if mapped else 0)
    return state


def real_string(state: PlotcharState, text: str = "ABC") -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def main() -> None:
    config = build_ncl_linear_mapped_backend_config(
        window_viewport_state=window_viewport_state(),
        direction_contract=verified_direction_contract(),
    )

    mapped_state = plotchar_state(mapped=True)
    mapped_result = compute_plchhq_with_ncl_linear_mapping(
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

    core_state = plotchar_state(mapped=False)
    core_result = compute_plchhq_fontcap_text_extent(
        chrs=real_string(core_state),
        state=core_state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )

    print("Mapped opt-in result:")
    print(f"  text: {mapped_result.text}")
    print(f"  font_number: {mapped_result.font_number}")
    print(f"  glyph_count: {mapped_result.glyph_count}")
    print(
        "  metrics: "
        f"dl={mapped_result.metrics.dl:.12g}, "
        f"dr={mapped_result.metrics.dr:.12g}, "
        f"db={mapped_result.metrics.db:.12g}, "
        f"dt={mapped_result.metrics.dt:.12g}"
    )

    print("Unmapped core reference:")
    print(
        "  metrics: "
        f"dl={core_result.metrics.dl:.12g}, "
        f"dr={core_result.metrics.dr:.12g}, "
        f"db={core_result.metrics.db:.12g}, "
        f"dt={core_result.metrics.dt:.12g}"
    )


if __name__ == "__main__":
    main()
