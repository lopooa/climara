from __future__ import annotations

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateTransformProvider,
    build_mapped_coordinate_request,
    compute_mapped_coordinate_extent,
    validate_source_mapped_transform_provider,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class IdentityButNotSourceMappedProvider(MappedCoordinateTransformProvider):
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


class DeclaredButReferenceMissingProvider(IdentityButNotSourceMappedProvider):
    source_mapped = True


class DeclaredSourceMappedProbeProvider(IdentityButNotSourceMappedProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def request(provider):
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
        transform_provider=provider,
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
    plain = IdentityButNotSourceMappedProvider()
    assert_guarded(
        "not source-mapped",
        lambda: validate_source_mapped_transform_provider(plain),
    )
    assert_guarded(
        "not source-mapped",
        lambda: compute_mapped_coordinate_extent(request(plain)),
    )

    missing_reference = DeclaredButReferenceMissingProvider()
    assert_guarded(
        "source_map_reference",
        lambda: validate_source_mapped_transform_provider(missing_reference),
    )
    assert_guarded(
        "source_map_reference",
        lambda: compute_mapped_coordinate_extent(request(missing_reference)),
    )

    declared = DeclaredSourceMappedProbeProvider()
    validate_source_mapped_transform_provider(declared)

    # Even declared providers cannot make runtime pass yet. This prevents the
    # provider contract from becoming a backdoor fake implementation.
    assert_guarded(
        "mapped-coordinate branch is not implemented",
        lambda: compute_mapped_coordinate_extent(request(declared)),
    )

    print("✅ Python Plotchar mapped-coordinate source-mapped provider contract smoke passed")


if __name__ == "__main__":
    main()
