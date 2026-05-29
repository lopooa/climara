from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateTransformProvider,
)
from climara.graphics._plotchar_mapped_runtime_strategy import (
    ProviderBackedMappedCoordinateRuntimeStrategy,
)
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
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


def fontcap_dir() -> Path:
    import os

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")
    return Path(ncl_root) / "common" / "src" / "fontcap"


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    state = mapped_state()

    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(state),
            state=state,
            xpos=0.5,
            ypos=0.5,
            size=0.03,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
            mapped_transform_provider=IdentityButNotSourceMappedProvider(),
            mapped_runtime_strategy=ProviderBackedMappedCoordinateRuntimeStrategy(),
        )
    except PlotcharUnsupportedError as exc:
        assert "not source-mapped" in str(exc), str(exc)
    else:
        raise AssertionError("provider-backed strategy must reject non-source-mapped provider")

    print("✅ Python Plotchar provider-backed mapped-coordinate strategy guard smoke passed")


if __name__ == "__main__":
    main()
