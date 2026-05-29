from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._plotchar_mapped_coordinate import mapped_coordinate_requested
from ._plotchar_mapped_runtime_strategy import ProviderBackedMappedCoordinateRuntimeStrategy
from ._plotchar_mapped_transform_ncl import (
    NclCoordinateTransformDirectionContract,
    NclLinearWindowViewportTransformProvider,
    NclWindowViewportState,
    validate_ncl_coordinate_transform_direction_contract,
)
from ._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class NclLinearMappedPlotcharBackendConfig:
    window_viewport_state: NclWindowViewportState
    direction_contract: NclCoordinateTransformDirectionContract
    source_map_reference: str


def validate_ncl_linear_mapped_backend_config(
    config: NclLinearMappedPlotcharBackendConfig,
) -> None:
    validate_ncl_coordinate_transform_direction_contract(config.direction_contract)

    if config.direction_contract.source_map_reference != config.source_map_reference:
        raise PlotcharUnsupportedError(
            "NCL linear mapped Plotchar backend config source_map_reference does not "
            "match the direction contract source_map_reference."
        )


def build_ncl_linear_mapped_backend_config(
    *,
    window_viewport_state: NclWindowViewportState,
    direction_contract: NclCoordinateTransformDirectionContract,
) -> NclLinearMappedPlotcharBackendConfig:
    validate_ncl_coordinate_transform_direction_contract(direction_contract)

    return NclLinearMappedPlotcharBackendConfig(
        window_viewport_state=window_viewport_state,
        direction_contract=direction_contract,
        source_map_reference=direction_contract.source_map_reference,
    )


def compute_plchhq_with_ncl_linear_mapping(
    *,
    chrs: str,
    state: Any,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    config: NclLinearMappedPlotcharBackendConfig,
    fontcap_dir: str | Path | None = None,
):
    """Explicit opt-in IMAP != 0 linear window/viewport backend.

    This is not a default path. The caller must provide a manually verified
    direction contract and explicit GETSET/SET-like window/viewport state.
    """

    validate_ncl_linear_mapped_backend_config(config)

    if not mapped_coordinate_requested(state):
        raise PlotcharUnsupportedError(
            "Explicit NCL linear mapped Plotchar backend received IMAP == 0. "
            "Use the existing unmapped fontcap mainline for this request."
        )

    provider = NclLinearWindowViewportTransformProvider(
        state=config.window_viewport_state,
        direction_contract=config.direction_contract,
    )
    strategy = ProviderBackedMappedCoordinateRuntimeStrategy()

    return compute_plchhq_fontcap_text_extent(
        chrs=chrs,
        state=state,
        xpos=xpos,
        ypos=ypos,
        size=size,
        angle=angle,
        cntr=cntr,
        fontcap_dir=fontcap_dir,
        mapped_transform_provider=provider,
        mapped_runtime_strategy=strategy,
    )


__all__ = [
    "NclLinearMappedPlotcharBackendConfig",
    "build_ncl_linear_mapped_backend_config",
    "compute_plchhq_with_ncl_linear_mapping",
    "validate_ncl_linear_mapped_backend_config",
]
