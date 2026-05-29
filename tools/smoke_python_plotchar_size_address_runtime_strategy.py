from __future__ import annotations

from climara.graphics._plotchar_size_address_unit import build_size_address_unit_request
from climara.graphics._plotchar_size_runtime_strategy import (
    SizeAddressRuntimeStrategy,
    compute_size_address_with_strategy,
    size_address_runtime_strategy_boundary,
    validate_source_mapped_size_address_runtime_strategy,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class PlainStrategy(SizeAddressRuntimeStrategy):
    pass


class SourceMappedButNotRuntimeStrategy(SizeAddressRuntimeStrategy):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_size_address_exact_branch_packet.md"


class RuntimeDeclaredButStillBaseStrategy(SizeAddressRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_size_address_exact_branch_packet.md"


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def request(strategy=None):
    return build_size_address_unit_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=1.0,
        angle=360.0,
        cntr=-1.0,
        runtime_strategy=strategy,
    )


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main() -> None:
    boundary = size_address_runtime_strategy_boundary()
    assert boundary.implemented is False

    assert_guarded(
        "runtime strategy is missing",
        lambda: compute_size_address_with_strategy(request(None)),
    )

    plain = PlainStrategy()
    assert_guarded(
        "not source-mapped",
        lambda: validate_source_mapped_size_address_runtime_strategy(plain),
    )
    assert_guarded(
        "not source-mapped",
        lambda: compute_size_address_with_strategy(request(plain)),
    )

    no_runtime = SourceMappedButNotRuntimeStrategy()
    assert_guarded(
        "has no implemented runtime",
        lambda: validate_source_mapped_size_address_runtime_strategy(no_runtime),
    )
    assert_guarded(
        "has no implemented runtime",
        lambda: compute_size_address_with_strategy(request(no_runtime)),
    )

    declared = RuntimeDeclaredButStillBaseStrategy()
    validate_source_mapped_size_address_runtime_strategy(declared)
    assert_guarded(
        "runtime strategy compute is not implemented",
        lambda: compute_size_address_with_strategy(request(declared)),
    )

    print("✅ Python Plotchar SIZE/address runtime strategy smoke passed")


if __name__ == "__main__":
    main()
