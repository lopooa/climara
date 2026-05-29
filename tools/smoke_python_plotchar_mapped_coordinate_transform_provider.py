from __future__ import annotations

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateTransformProvider,
    build_mapped_coordinate_request,
    default_mapped_coordinate_transform_provider,
    require_mapped_coordinate_transform_provider,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class IdentityProbeProvider(MappedCoordinateTransformProvider):
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


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def main() -> None:
    point = MappedCoordinatePoint(0.25, 0.75)
    extent = MappedCoordinateExtent(dl=0.01, dr=0.02, db=0.03, dt=0.04)

    guarded = default_mapped_coordinate_transform_provider()

    try:
        guarded.user_to_plotchar(point)
    except PlotcharUnsupportedError as exc:
        assert "mapped-coordinate branch is not implemented" in str(exc)
    else:
        raise AssertionError("default mapped-coordinate provider must remain guarded")

    try:
        require_mapped_coordinate_transform_provider(None)
    except PlotcharUnsupportedError as exc:
        assert "mapped-coordinate branch is not implemented" in str(exc)
    else:
        raise AssertionError("missing provider must remain guarded")

    provider = IdentityProbeProvider()
    assert require_mapped_coordinate_transform_provider(provider) is provider
    assert provider.user_to_plotchar(point) == point
    assert provider.plotchar_to_user(point) == point
    assert provider.extent_to_user(origin=point, extent=extent) == extent

    state = mapped_state()
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    request = build_mapped_coordinate_request(
        chrs=f"{code}A{code}ABC",
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        transform_provider=provider,
    )

    assert request.transform_provider is provider
    assert request.snapshot.imap == 1

    print("✅ Python Plotchar mapped-coordinate transform provider smoke passed")


if __name__ == "__main__":
    main()
