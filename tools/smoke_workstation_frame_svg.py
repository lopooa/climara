from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class HluPolyline:
    x: list[float]
    y: list[float]
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


@dataclass
class HluTextItem:
    text: str
    x: float
    y: float
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "wks_frame_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 900,
            "wkHeight": 620,
            "wkBackgroundColor": "white",
        },
    )

    wks.add_child(
        HluPolyline(
            x=[0.10, 0.25, 0.40, 0.60, 0.80, 0.92],
            y=[0.20, 0.55, 0.35, 0.72, 0.42, 0.80],
            resources={
                "gsLineColor": "#0055aa",
                "gsLineThicknessF": 2.2,
            },
        )
    )

    wks.add_child(
        HluTextItem(
            text="gsn_open_wks -> frame -> SVG",
            x=0.50,
            y=0.92,
            resources={
                "txFontHeightF": 0.030,
                "txFontColor": "#111111",
                "txJust": "CenterCenter",
            },
        )
    )

    output = cgr.frame(wks)

    if not output.exists():
        raise RuntimeError(f"Frame output was not created: {output}")

    text = output.read_text(encoding="utf-8")
    required = ["<svg", "<polyline", "<text", "gsn_open_wks"]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"Frame SVG missing required content: {missing}")

    print(f"✅ workstation frame smoke passed: {output}")
    print(f"✅ frame_count: {wks.frame_count}")
    print(f"✅ last_output: {wks.last_output}")


if __name__ == "__main__":
    main()
