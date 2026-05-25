from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class HluRoot:
    children: list[Any] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)

    def add_child(self, item: Any):
        self.children.append(item)
        return item


@dataclass
class HluPolyline:
    x: list[float]
    y: list[float]
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


@dataclass
class HluPolygon:
    x: list[float]
    y: list[float]
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


@dataclass
class HluMarker:
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

    out_dir = Path("outputs") / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "svg_backend_smoke.svg"

    root = HluRoot()

    root.add_child(
        HluPolygon(
            x=[0.10, 0.90, 0.90, 0.10],
            y=[0.15, 0.15, 0.85, 0.85],
            resources={
                "gsFillColor": "#f6f6f6",
                "gsLineColor": "#222222",
                "gsLineThicknessF": 1.2,
            },
        )
    )

    root.add_child(
        HluPolyline(
            x=[0.15, 0.30, 0.45, 0.60, 0.75, 0.85],
            y=[0.25, 0.58, 0.40, 0.70, 0.45, 0.78],
            resources={
                "gsLineColor": "#004c99",
                "gsLineThicknessF": 2.0,
            },
        )
    )

    root.add_child(
        HluMarker(
            x=[0.30, 0.45, 0.60, 0.75],
            y=[0.58, 0.40, 0.70, 0.45],
            resources={
                "gsMarkerColor": "#cc3300",
                "gsMarkerSizeF": 0.010,
            },
        )
    )

    root.add_child(
        HluTextItem(
            text="climara SVG backend smoke",
            x=0.50,
            y=0.92,
            resources={
                "txFontColor": "#111111",
                "txFontHeightF": 0.026,
                "txJust": "CenterCenter",
            },
        )
    )

    svg_text = cgr.render_svg(
        root,
        path=out_file,
        width=900,
        height=650,
        background="white",
    )

    required = ["<svg", "<polygon", "<polyline", "<circle", "<text"]
    missing = [item for item in required if item not in svg_text]
    if missing:
        raise RuntimeError(f"SVG smoke output missing elements: {missing}")

    print(f"✅ SVG smoke passed: {out_file}")
    print(f"✅ public exports loaded: {len(cgr.__all__)}")

    failed = getattr(cgr, "_FAILED_IMPORTS", {})
    if failed:
        print("⚠️ Some optional graphics exports were skipped:")
        for key, value in failed.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
