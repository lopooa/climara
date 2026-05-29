from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Any, Mapping

from ._plotchar_metrics import (
    PlotcharExtentMetrics,
    PlotcharMetricsRequest,
    build_plotchar_extent_metrics,
)
from ._plotchar_metrics_provider import PlotcharMetricsProviderError
from ._text_semantics import TextItemSemantics, plotchar_real_size_from_text_semantics


class NclPlotcharMeasurementContractError(PlotcharMetricsProviderError):
    pass


@dataclass(frozen=True)
class NclPlotcharTextItemState:
    text_extent_flag: int
    constant_spacing: float
    func_code: str
    principle_height: float
    principle_width: float
    quality_index: int
    font: int
    effective_font: int
    font_aspect: float
    font_aspect_was_sanitized: bool
    real_size: float


@dataclass(frozen=True)
class NclPlotcharTextItemMeasurementCall:
    xpos: float
    ypos: float
    chrs: str
    size: float
    angd: float
    cntr: float
    state: NclPlotcharTextItemState


def _normalize_font(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise NclPlotcharMeasurementContractError(
            "NCL TextItem Plotchar measurement requires an integer txFont value "
            f"before calling PCSETI('FN', ...); got {value!r}"
        ) from exc


def ncl_textitem_principle_dimensions(font_aspect: float) -> tuple[float, float, bool]:
    aspect = float(font_aspect)
    sanitized = False

    if aspect <= 0.0:
        aspect = 1.3125
        sanitized = True

    if aspect <= 1.0:
        real_ph_height = 21.0 * aspect
        real_ph_width = 21.0
    else:
        real_ph_height = 21.0
        real_ph_width = 21.0 / aspect

    return real_ph_height, real_ph_width, sanitized


def build_ncl_plotchar_textitem_state(
    semantics: TextItemSemantics,
) -> NclPlotcharTextItemState:
    quality_index = int(semantics.quality_index)

    if quality_index >= 3:
        raise NclPlotcharMeasurementContractError(
            "NCL TextItem.c handles txFontQuality=Workstation with workstation-specific "
            "PS/PDF/GKS logic. That branch is not part of this Plotchar measurement "
            "contract boundary yet. Do not approximate it."
        )

    font = _normalize_font(semantics.font)
    effective_font = 1 if quality_index == 2 else font
    real_ph_height, real_ph_width, sanitized = ncl_textitem_principle_dimensions(
        semantics.font_aspect
    )

    return NclPlotcharTextItemState(
        text_extent_flag=1,
        constant_spacing=float(semantics.constant_spacing),
        func_code=str(semantics.func_code)[0],
        principle_height=real_ph_height,
        principle_width=real_ph_width,
        quality_index=quality_index,
        font=font,
        effective_font=effective_font,
        font_aspect=1.3125 if sanitized else float(semantics.font_aspect),
        font_aspect_was_sanitized=sanitized,
        real_size=plotchar_real_size_from_text_semantics(semantics),
    )


def validate_ncl_textitem_measurement_request(
    request: PlotcharMetricsRequest,
    *,
    tol: float = 1e-12,
) -> None:
    expected_size = plotchar_real_size_from_text_semantics(request.semantics)

    checks = (
        ("x", request.x, 0.5),
        ("y", request.y, 0.5),
        ("size", request.size, expected_size),
        ("angle", request.angle, 360.0),
        ("cntr", request.cntr, -1.0),
    )

    bad = []
    for name, value, expected in checks:
        if not isclose(float(value), float(expected), rel_tol=0.0, abs_tol=tol):
            bad.append(f"{name}={value!r}, expected {expected!r}")

    if bad:
        raise NclPlotcharMeasurementContractError(
            "Plotchar metrics request does not match TextItem.c::FigureAndSetTextBBInfo "
            "measurement contract: " + "; ".join(bad)
        )


def build_ncl_plotchar_textitem_measurement_call(
    request: PlotcharMetricsRequest,
) -> NclPlotcharTextItemMeasurementCall:
    validate_ncl_textitem_measurement_request(request)
    state = build_ncl_plotchar_textitem_state(request.semantics)

    return NclPlotcharTextItemMeasurementCall(
        xpos=0.5,
        ypos=0.5,
        chrs=request.semantics.real_string,
        size=state.real_size,
        angd=360.0,
        cntr=-1.0,
        state=state,
    )


def _metrics_from_mapping(value: Mapping[str, Any]) -> PlotcharExtentMetrics:
    keys = {str(key).lower(): item for key, item in value.items()}
    required = ("dl", "dr", "db", "dt")
    missing = [key for key in required if key not in keys]
    if missing:
        raise KeyError(
            "NCL Plotchar backend mapping is missing required metrics: "
            + ", ".join(missing)
        )

    return build_plotchar_extent_metrics(
        dl=keys["dl"],
        dr=keys["dr"],
        db=keys["db"],
        dt=keys["dt"],
    )


def normalize_backend_plotchar_metrics(value: Any) -> PlotcharExtentMetrics:
    if isinstance(value, PlotcharExtentMetrics):
        return value

    if isinstance(value, Mapping):
        return _metrics_from_mapping(value)

    raise TypeError(
        "NCL Plotchar backend must return PlotcharExtentMetrics or a mapping "
        "with dl/dr/db/dt values"
    )


@dataclass(frozen=True)
class NclPlotcharMetricsProvider:
    backend: Any | None = None

    def metrics_for_request(
        self,
        request: PlotcharMetricsRequest,
    ) -> PlotcharExtentMetrics:
        call = build_ncl_plotchar_textitem_measurement_call(request)

        if self.backend is None:
            raise PlotcharMetricsProviderError(
                "No live NCL Plotchar backend is configured. The provider boundary is "
                "source-mapped to TextItem.c -> PCSETI/PCSETR/PCSETC -> "
                "PLCHHQ(0.5,0.5,real_string,real_size,360.0,-1.0) -> "
                "PCGETR(DL/DR/DB/DT). climara must not replace that with fixed-width "
                "or SVG text-size heuristics."
            )

        if hasattr(self.backend, "metrics_for_call"):
            raw = self.backend.metrics_for_call(call)
        elif callable(self.backend):
            raw = self.backend(call)
        else:
            raise TypeError(
                "NCL Plotchar backend must define metrics_for_call(call) or be callable"
            )

        return normalize_backend_plotchar_metrics(raw)


def build_ncl_plotchar_metrics_provider(
    backend: Any | None = None,
) -> NclPlotcharMetricsProvider:
    return NclPlotcharMetricsProvider(backend=backend)


__all__ = [
    "NclPlotcharMeasurementContractError",
    "NclPlotcharMetricsProvider",
    "NclPlotcharTextItemMeasurementCall",
    "NclPlotcharTextItemState",
    "build_ncl_plotchar_metrics_provider",
    "build_ncl_plotchar_textitem_measurement_call",
    "build_ncl_plotchar_textitem_state",
    "ncl_textitem_principle_dimensions",
    "normalize_backend_plotchar_metrics",
    "validate_ncl_textitem_measurement_request",
]
