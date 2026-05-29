from __future__ import annotations

from climara.graphics._plotchar_pwritx_nonfontcap import build_pwritx_nonfontcap_request
from climara.graphics._plotchar_pwritx_runtime_strategy import (
    PwritxRuntimeStrategy,
    compute_pwritx_with_strategy,
    pwritx_runtime_strategy_boundary,
    validate_source_mapped_pwritx_runtime_strategy,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class PlainStrategy(PwritxRuntimeStrategy):
    pass


class SourceMappedButNotRuntimeStrategy(PwritxRuntimeStrategy):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"


class RuntimeDeclaredButStillBaseStrategy(PwritxRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
    out.pcseti("MA", 0)
    return out


def request(strategy=None):
    return build_pwritx_nonfontcap_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=0.03,
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
    boundary = pwritx_runtime_strategy_boundary()
    assert boundary.implemented is False

    assert_guarded("runtime strategy is missing", lambda: compute_pwritx_with_strategy(request(None)))

    plain = PlainStrategy()
    assert_guarded("not source-mapped", lambda: validate_source_mapped_pwritx_runtime_strategy(plain))
    assert_guarded("not source-mapped", lambda: compute_pwritx_with_strategy(request(plain)))

    no_runtime = SourceMappedButNotRuntimeStrategy()
    assert_guarded("has no implemented runtime", lambda: validate_source_mapped_pwritx_runtime_strategy(no_runtime))
    assert_guarded("has no implemented runtime", lambda: compute_pwritx_with_strategy(request(no_runtime)))

    declared = RuntimeDeclaredButStillBaseStrategy()
    validate_source_mapped_pwritx_runtime_strategy(declared)
    assert_guarded("runtime strategy compute is not implemented", lambda: compute_pwritx_with_strategy(request(declared)))

    print("✅ Python Plotchar PWRITX runtime strategy smoke passed")


if __name__ == "__main__":
    main()
