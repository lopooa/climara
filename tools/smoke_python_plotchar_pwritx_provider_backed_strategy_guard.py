from __future__ import annotations

from climara.graphics._plotchar_pwritx_nonfontcap import (
    build_pwritx_nonfontcap_request,
    compute_pwritx_nonfontcap_extent,
)
from climara.graphics._plotchar_pwritx_provider import PwritxMetricsProvider
from climara.graphics._plotchar_pwritx_runtime_strategy import ProviderBackedPwritxRuntimeStrategy
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


class PlainProvider(PwritxMetricsProvider):
    pass


def state() -> PlotcharState:
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
    out.pcseti("MA", 0)
    return out


def main() -> None:
    request = build_pwritx_nonfontcap_request(
        chrs=":A:ABC",
        state=state(),
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        runtime_strategy=ProviderBackedPwritxRuntimeStrategy(),
        metrics_provider=PlainProvider(),
    )

    try:
        compute_pwritx_nonfontcap_extent(request)
    except PlotcharUnsupportedError as exc:
        assert "not source-mapped" in str(exc), str(exc)
    else:
        raise AssertionError("provider-backed PWRITX strategy accepted non-source-mapped provider")

    print("✅ Python Plotchar provider-backed PWRITX strategy guard smoke passed")


if __name__ == "__main__":
    main()
