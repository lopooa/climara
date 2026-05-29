from __future__ import annotations

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateTransformProvider,
    build_mapped_coordinate_request,
)
from climara.graphics._plotchar_mapped_runtime_strategy import (
    MappedCoordinateRuntimeStrategy,
    compute_mapped_coordinate_with_strategy,
    mapped_coordinate_runtime_strategy_boundary,
    validate_source_mapped_runtime_strategy,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class SourceMappedTransformProvider(MappedCoordinateTransformProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"

    def user_to_plotchar(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        return point

    def plotchar_to_user(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        return point

    def extent_to_user(
        self,
        *,
        origin: MappedCoordinatePoint,
        extent: MappedCoordinateExtent,
    ) -> MappedCoordinateExtent:
        return extent


class PlainStrategy(MappedCoordinateRuntimeStrategy):
    pass


class SourceMappedButNotRuntimeStrategy(MappedCoordinateRuntimeStrategy):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"


class RuntimeDeclaredButStillBaseStrategy(MappedCoordinateRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def request(strategy=None):
    state = mapped_state()
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return build_mapped_coordinate_request(
        chrs=f"{code}A{code}ABC",
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        transform_provider=SourceMappedTransformProvider(),
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
    boundary = mapped_coordinate_runtime_strategy_boundary()
    assert boundary.implemented is False

    assert_guarded(
        "runtime strategy is missing",
        lambda: compute_mapped_coordinate_with_strategy(request(None)),
    )

    plain = PlainStrategy()
    assert_guarded(
        "not source-mapped",
        lambda: validate_source_mapped_runtime_strategy(plain),
    )
    assert_guarded(
        "not source-mapped",
        lambda: compute_mapped_coordinate_with_strategy(request(plain)),
    )

    no_runtime = SourceMappedButNotRuntimeStrategy()
    assert_guarded(
        "has no implemented runtime",
        lambda: validate_source_mapped_runtime_strategy(no_runtime),
    )
    assert_guarded(
        "has no implemented runtime",
        lambda: compute_mapped_coordinate_with_strategy(request(no_runtime)),
    )

    declared = RuntimeDeclaredButStillBaseStrategy()
    validate_source_mapped_runtime_strategy(declared)
    assert_guarded(
        "runtime strategy compute is not implemented",
        lambda: compute_mapped_coordinate_with_strategy(request(declared)),
    )

    print("✅ Python Plotchar mapped-coordinate runtime strategy smoke passed")


if __name__ == "__main__":
    main()
