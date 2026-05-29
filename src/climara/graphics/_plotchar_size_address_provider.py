from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_size_address_unit import SizeAddressUnitResult, raise_size_address_unit_guard
from ._plotchar_state import PlotcharUnsupportedError


SIZE_ADDRESS_PROVIDER_DOCS = (
    "docs/ncl_plotchar_size_address_exact_branch_packet.md",
    "docs/ncl_plotchar_size_address_formula_audit.md",
    "docs/ncl_plotchar_extent_alias_source_map.md",
)


@dataclass(frozen=True)
class SizeAddressScaleProviderBoundary:
    implemented: bool
    reason: str
    required_docs: tuple[str, ...]


def size_address_scale_provider_boundary() -> SizeAddressScaleProviderBoundary:
    return SizeAddressScaleProviderBoundary(
        implemented=False,
        reason=(
            "SIZE/address scale provider boundary is available, but no default NCL "
            "address-unit provider is implemented. Address-unit SIZE requires explicit "
            "source-mapped provider injection."
        ),
        required_docs=SIZE_ADDRESS_PROVIDER_DOCS,
    )


class SizeAddressScaleProvider:
    source_mapped = False
    source_map_reference = ""

    def fractional_core_size(self, request) -> float:
        raise_size_address_unit_guard(request.size)

    def result_from_core(self, *, request, core_result) -> SizeAddressUnitResult:
        raise_size_address_unit_guard(request.size)


class GuardedSizeAddressScaleProvider(SizeAddressScaleProvider):
    pass


def default_size_address_scale_provider() -> SizeAddressScaleProvider:
    return GuardedSizeAddressScaleProvider()


def require_size_address_scale_provider(
    provider: SizeAddressScaleProvider | None,
) -> SizeAddressScaleProvider:
    if provider is None:
        raise PlotcharUnsupportedError(
            "SIZE/address scale provider is missing. Address-unit SIZE remains guarded."
        )
    return provider


def validate_source_mapped_size_address_scale_provider(
    provider: SizeAddressScaleProvider,
) -> None:
    if not bool(getattr(provider, "source_mapped", False)):
        raise PlotcharUnsupportedError(
            "SIZE/address scale provider is not source-mapped. "
            "Do not use unsupported address-unit SIZE metrics."
        )

    reference = str(getattr(provider, "source_map_reference", "")).strip()
    if not reference:
        raise PlotcharUnsupportedError(
            "SIZE/address scale provider must declare source_map_reference."
        )


def validate_fractional_core_size(value: float) -> None:
    size = float(value)
    if not (0.0 < size < 1.0):
        raise PlotcharUnsupportedError(
            "SIZE/address provider returned an invalid fractional core size. "
            "The provider-backed strategy requires 0 < core SIZE < 1."
        )


__all__ = [
    "NclSourceMappedSizeAddressScaleProvider",
    "GuardedSizeAddressScaleProvider",
    "SIZE_ADDRESS_PROVIDER_DOCS",
    "SizeAddressScaleProvider",
    "SizeAddressScaleProviderBoundary",
    "default_size_address_scale_provider",
    "require_size_address_scale_provider",
    "size_address_scale_provider_boundary",
    "validate_fractional_core_size",
    "validate_source_mapped_size_address_scale_provider",
]



class NclSourceMappedSizeAddressScaleProvider(SizeAddressScaleProvider):
    """NCL PLCHHQ SIZE/address-unit scale provider for IMAP <= 0.

    Source-mapped branch:

    - SIZE <= 0: SIZM = ABS(SIZE) / 1023
    - 0 < SIZE < 1: SIZM = SIZE / WPIC(1)
    - SIZE >= 1: SIZM = (SIZE / RSLN) / WPIC(1)
    - high quality: SIZM = SIZA * SIZM, handled by the existing fractional core

    This provider returns the equivalent fractional core SIZE expected by the
    existing Python fontcap extent core. It does not enable mapped IMAP > 0.
    """

    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_size_address_exact_branch_packet.md"

    def __init__(self, *, address_resolution: float):
        self.address_resolution = float(address_resolution)

        if self.address_resolution <= 0.0:
            raise ValueError("address_resolution must be positive")

    def fractional_core_size(self, request) -> float:
        size = float(request.size)
        state = request.state

        imap = int(getattr(state, "imap", 0))
        if imap > 0:
            raise_size_address_unit_guard(
                size,
                extra=(
                    "Mapped IMAP > 0 SIZE/address branch remains guarded. "
                    "Current NCL source-mapped provider only implements IMAP <= 0."
                ),
            )

        wpic1 = float(state.wpic[0])
        if wpic1 == 0.0:
            raise_size_address_unit_guard(
                size,
                extra="WPIC(1) is zero; cannot map NCL SIZM to fractional core size.",
            )

        if size <= 0.0:
            # NCL: SIZM = ABS(SIZE) / 1023.
            # Existing fractional core computes SIZM = core_size / WPIC(1).
            # Therefore core_size = ABS(SIZE) * WPIC(1) / 1023.
            core_size = abs(size) * wpic1 / 1023.0
        elif size < 1.0:
            core_size = size
        else:
            # NCL: SIZM = (SIZE / RSLN) / WPIC(1).
            # Existing fractional core computes SIZM = core_size / WPIC(1).
            # Therefore core_size = SIZE / RSLN.
            core_size = size / self.address_resolution

        validate_fractional_core_size(core_size)
        return core_size

    def result_from_core(self, *, request, core_result):
        return SizeAddressUnitResult(
            metrics=core_result.metrics,
            state=core_result.state,
            text=core_result.text,
            font_number=core_result.font_number,
            glyph_count=core_result.glyph_count,
        )
