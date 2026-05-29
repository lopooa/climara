from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_mapped_runtime_strategy import (
    ProviderBackedMappedCoordinateRuntimeStrategy,
)
from climara.graphics._plotchar_mapped_transform_ncl import (
    NclCoordinateTransformDirectionContract,
    NclLinearWindowViewportTransformProvider,
    NclWindowViewportState,
)
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState


def fontcap_dir() -> Path:
    import os

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")
    return Path(ncl_root) / "common" / "src" / "fontcap"


def verified_contract() -> NclCoordinateTransformDirectionContract:
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


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def unmapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 0)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    viewport_state = NclWindowViewportState(
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
    provider = NclLinearWindowViewportTransformProvider(
        state=viewport_state,
        direction_contract=verified_contract(),
    )
    strategy = ProviderBackedMappedCoordinateRuntimeStrategy()

    mapped_state_obj = mapped_state()

    mapped = compute_plchhq_fontcap_text_extent(
        chrs=real_string(mapped_state_obj),
        state=mapped_state_obj,
        xpos=5.0,
        ypos=150.0,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
        mapped_transform_provider=provider,
        mapped_runtime_strategy=strategy,
    )

    core_state = unmapped_state()
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

    # X scale: user span 10 / viewport span 0.6
    # Y scale: user span 100 / viewport span 0.8
    assert abs(mapped.metrics.dl - core.metrics.dl * (10.0 / 0.6)) < 1e-10
    assert abs(mapped.metrics.dr - core.metrics.dr * (10.0 / 0.6)) < 1e-10
    assert abs(mapped.metrics.db - core.metrics.db * (100.0 / 0.8)) < 1e-10
    assert abs(mapped.metrics.dt - core.metrics.dt * (100.0 / 0.8)) < 1e-10

    assert mapped.text == core.text
    assert mapped.font_number == core.font_number
    assert mapped.glyph_count == core.glyph_count

    print("✅ Python Plotchar mapped-coordinate with NCL linear provider smoke passed")


if __name__ == "__main__":
    main()
