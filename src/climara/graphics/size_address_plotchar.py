from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from ._plotchar_size_address_provider import (
    SizeAddressScaleProvider,
    size_address_scale_provider_boundary,
    validate_source_mapped_size_address_scale_provider,
)
from ._plotchar_size_address_unit import (
    size_address_unit_boundary,
    size_address_unit_requested,
)
from ._plotchar_size_runtime_strategy import (
    ProviderBackedSizeAddressRuntimeStrategy,
    size_address_runtime_strategy_boundary,
)
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class SizeAddressProviderBackendConfig:
    scale_provider: SizeAddressScaleProvider
    source_map_reference: str


def validate_size_address_provider_backend_config(
    config: SizeAddressProviderBackendConfig,
) -> None:
    validate_source_mapped_size_address_scale_provider(config.scale_provider)

    provider_reference = str(getattr(config.scale_provider, "source_map_reference", "")).strip()
    config_reference = str(config.source_map_reference).strip()

    if not config_reference:
        raise PlotcharUnsupportedError(
            "SIZE/address provider backend config requires source_map_reference."
        )

    if provider_reference != config_reference:
        raise PlotcharUnsupportedError(
            "SIZE/address provider backend config source_map_reference does not match "
            "the scale provider source_map_reference."
        )


def build_size_address_provider_backend_config(
    *,
    scale_provider: SizeAddressScaleProvider,
) -> SizeAddressProviderBackendConfig:
    validate_source_mapped_size_address_scale_provider(scale_provider)

    return SizeAddressProviderBackendConfig(
        scale_provider=scale_provider,
        source_map_reference=str(scale_provider.source_map_reference),
    )


def compute_plchhq_with_size_address_provider(
    *,
    chrs: str,
    state: Any,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    config: SizeAddressProviderBackendConfig,
    fontcap_dir: str | Path | None = None,
):
    """Explicit opt-in provider-backed address-unit SIZE backend.

    This function is not a default NCL implementation. The caller must provide
    a source-mapped scale provider. Fractional SIZE requests should use the
    existing mainline directly.
    """

    validate_size_address_provider_backend_config(config)

    if not size_address_unit_requested(size):
        raise PlotcharUnsupportedError(
            "Explicit SIZE/address provider backend received fractional SIZE. "
            "Use the existing 0 < SIZE < 1 Plotchar mainline for this request."
        )

    return compute_plchhq_fontcap_text_extent(
        chrs=chrs,
        state=state,
        xpos=xpos,
        ypos=ypos,
        size=size,
        angle=angle,
        cntr=cntr,
        fontcap_dir=fontcap_dir,
        size_address_runtime_strategy=ProviderBackedSizeAddressRuntimeStrategy(),
        size_address_scale_provider=config.scale_provider,
    )


__all__ = [
    "ProviderBackedSizeAddressRuntimeStrategy",
    "SizeAddressProviderBackendConfig",
    "SizeAddressScaleProvider",
    "build_size_address_provider_backend_config",
    "compute_plchhq_with_size_address_provider",
    "size_address_runtime_strategy_boundary",
    "size_address_scale_provider_boundary",
    "size_address_unit_boundary",
    "validate_size_address_provider_backend_config",
]
