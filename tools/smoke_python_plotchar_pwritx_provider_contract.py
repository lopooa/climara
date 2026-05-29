from __future__ import annotations

from climara.graphics._plotchar_pwritx_provider import (
    PwritxMetricsProvider,
    default_pwritx_metrics_provider,
    pwritx_metrics_provider_boundary,
    require_pwritx_metrics_provider,
    validate_source_mapped_pwritx_metrics_provider,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


class PlainProvider(PwritxMetricsProvider):
    pass


class SourceMappedProvider(PwritxMetricsProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main() -> None:
    boundary = pwritx_metrics_provider_boundary()
    assert boundary.implemented is False

    guarded = default_pwritx_metrics_provider()
    assert_guarded("PWRITX/font0/non-fontcap", lambda: guarded.metrics_for_request(object()))

    assert_guarded("metrics provider is missing", lambda: require_pwritx_metrics_provider(None))
    assert require_pwritx_metrics_provider(guarded) is guarded

    plain = PlainProvider()
    assert_guarded("not source-mapped", lambda: validate_source_mapped_pwritx_metrics_provider(plain))

    mapped = SourceMappedProvider()
    validate_source_mapped_pwritx_metrics_provider(mapped)

    print("✅ Python Plotchar PWRITX metrics-provider contract smoke passed")


if __name__ == "__main__":
    main()
