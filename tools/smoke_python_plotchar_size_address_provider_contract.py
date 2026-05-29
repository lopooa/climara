from __future__ import annotations

from climara.graphics._plotchar_size_address_provider import (
    SizeAddressScaleProvider,
    default_size_address_scale_provider,
    require_size_address_scale_provider,
    size_address_scale_provider_boundary,
    validate_fractional_core_size,
    validate_source_mapped_size_address_scale_provider,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


class PlainProvider(SizeAddressScaleProvider):
    pass


class SourceMappedProvider(SizeAddressScaleProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_size_address_formula_audit.md"


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main() -> None:
    boundary = size_address_scale_provider_boundary()
    assert boundary.implemented is False

    guarded = default_size_address_scale_provider()
    assert_guarded("SIZE", lambda: guarded.fractional_core_size(type("R", (), {"size": 1.0})()))

    assert_guarded("scale provider is missing", lambda: require_size_address_scale_provider(None))
    assert require_size_address_scale_provider(guarded) is guarded

    plain = PlainProvider()
    assert_guarded("not source-mapped", lambda: validate_source_mapped_size_address_scale_provider(plain))

    mapped = SourceMappedProvider()
    validate_source_mapped_size_address_scale_provider(mapped)

    validate_fractional_core_size(0.03)
    assert_guarded("0 < core SIZE < 1", lambda: validate_fractional_core_size(1.0))
    assert_guarded("0 < core SIZE < 1", lambda: validate_fractional_core_size(0.0))

    print("✅ Python Plotchar SIZE/address scale-provider contract smoke passed")


if __name__ == "__main__":
    main()
