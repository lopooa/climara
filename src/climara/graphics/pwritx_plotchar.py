from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._plotchar_pwritx_nonfontcap import (
    build_pwritx_nonfontcap_request,
    compute_pwritx_nonfontcap_extent,
    pwritx_nonfontcap_boundary,
)
from ._plotchar_pwritx_provider import (
    PwritxMetricsProvider,
    pwritx_metrics_provider_boundary,
    validate_source_mapped_pwritx_metrics_provider,
)
from ._plotchar_pwritx_runtime_strategy import (
    ProviderBackedPwritxRuntimeStrategy,
    pwritx_runtime_strategy_boundary,
)
from ._plotchar_state import PlotcharUnsupportedError


@dataclass(frozen=True)
class PwritxProviderBackendConfig:
    metrics_provider: PwritxMetricsProvider
    source_map_reference: str


def validate_pwritx_provider_backend_config(config: PwritxProviderBackendConfig) -> None:
    validate_source_mapped_pwritx_metrics_provider(config.metrics_provider)

    provider_reference = str(getattr(config.metrics_provider, "source_map_reference", "")).strip()
    config_reference = str(config.source_map_reference).strip()

    if not config_reference:
        raise PlotcharUnsupportedError(
            "PWRITX/font0 provider backend config requires source_map_reference."
        )

    if provider_reference != config_reference:
        raise PlotcharUnsupportedError(
            "PWRITX/font0 provider backend config source_map_reference does not match "
            "the metrics provider source_map_reference."
        )


def build_pwritx_provider_backend_config(
    *,
    metrics_provider: PwritxMetricsProvider,
) -> PwritxProviderBackendConfig:
    validate_source_mapped_pwritx_metrics_provider(metrics_provider)

    return PwritxProviderBackendConfig(
        metrics_provider=metrics_provider,
        source_map_reference=str(metrics_provider.source_map_reference),
    )


def compute_plchhq_with_pwritx_provider(
    *,
    chrs: str,
    state: Any,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    config: PwritxProviderBackendConfig,
    fontcap_dir: str | Path | None = None,
):
    validate_pwritx_provider_backend_config(config)

    request = build_pwritx_nonfontcap_request(
        chrs=chrs,
        state=state,
        xpos=xpos,
        ypos=ypos,
        size=size,
        angle=angle,
        cntr=cntr,
        fontcap_dir=fontcap_dir,
        runtime_strategy=ProviderBackedPwritxRuntimeStrategy(),
        metrics_provider=config.metrics_provider,
    )

    return compute_pwritx_nonfontcap_extent(request)


__all__ = [
    "ProviderBackedPwritxRuntimeStrategy",
    "PwritxMetricsProvider",
    "PwritxProviderBackendConfig",
    "build_pwritx_provider_backend_config",
    "compute_plchhq_with_pwritx_provider",
    "pwritx_metrics_provider_boundary",
    "pwritx_nonfontcap_boundary",
    "pwritx_runtime_strategy_boundary",
    "validate_pwritx_provider_backend_config",
]
