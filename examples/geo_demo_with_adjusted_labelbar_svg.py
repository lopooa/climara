from __future__ import annotations

from html import escape
from math import cos, radians, sin
from pathlib import Path

from climara.graphics import HluLabelBar, PlotcharExtentMetrics, SvgDocument
from climara.graphics import add_adjusted_labelbar_primitives_to_svg_document
from climara.graphics._labelbar_svg_adapter import (
    labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics,
)


WIDTH = 1200
HEIGHT = 780

MAP_X = 70
MAP_Y = 80
MAP_W = 1060
MAP_H = 500


LEVELS = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
COLORS = [
    "#08306b",
    "#2171b5",
    "#6baed6",
    "#c6dbef",
    "#f7f7f7",
    "#fdd0a2",
    "#fd8d3c",
    "#e6550d",
    "#a63603",
]


def lon_to_x(lon: float) -> float:
    return MAP_X + (lon + 180.0) / 360.0 * MAP_W


def lat_to_y(lat: float) -> float:
    return MAP_Y + (90.0 - lat) / 180.0 * MAP_H


def svg_text(x, y, text, size=20, fill="#111827", weight="400", anchor="start"):
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" '
        f'font-family="Arial, Microsoft YaHei, Noto Sans CJK SC, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{escape(str(text))}</text>'
    )


def add(doc: SvgDocument, text: str) -> None:
    doc.add(text)


def synthetic_anomaly(lon: float, lat: float) -> float:
    value = (
        2.0 * sin(radians(lon * 1.4)) * cos(radians(lat * 0.8))
        + 1.3 * sin(radians(lat * 2.1))
        + 0.8 * cos(radians((lon + lat) * 0.7))
    )
    return max(-4.0, min(4.0, value))


def color_for_value(value: float) -> str:
    idx = int(round(value + 4))
    idx = max(0, min(len(COLORS) - 1, idx))
    return COLORS[idx]


def polyline_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    first = points[0]
    parts = [f"M {lon_to_x(first[0]):.2f} {lat_to_y(first[1]):.2f}"]
    for lon, lat in points[1:]:
        parts.append(f"L {lon_to_x(lon):.2f} {lat_to_y(lat):.2f}")
    parts.append("Z")
    return " ".join(parts)


def draw_background(doc: SvgDocument) -> None:
    add(doc, f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>')

    add(
        doc,
        f'<text x="{WIDTH / 2:.1f}" y="42" '
        f'font-family="Arial, Microsoft YaHei, Noto Sans CJK SC, sans-serif" '
        f'font-size="28" font-weight="700" fill="#111827" text-anchor="middle">'
        f'climara no-Matplotlib SVG geo demo</text>',
    )

    add(
        doc,
        f'<text x="{WIDTH / 2:.1f}" y="68" '
        f'font-family="Arial, Microsoft YaHei, Noto Sans CJK SC, sans-serif" '
        f'font-size="16" fill="#4b5563" text-anchor="middle">'
        f'地图主体为合成地理示例场；底部 LabelBar 使用当前 explicit supplied-metrics AdjustGeometry 管线生成</text>',
    )

    add(
        doc,
        f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" rx="18" '
        f'fill="#e0f2fe" stroke="#1e3a8a" stroke-width="2"/>',
    )


def draw_synthetic_field(doc: SvgDocument) -> None:
    lon_step = 10
    lat_step = 10

    for lat in range(-80, 90, lat_step):
        for lon in range(-180, 180, lon_step):
            center_lon = lon + lon_step / 2
            center_lat = lat + lat_step / 2
            value = synthetic_anomaly(center_lon, center_lat)
            color = color_for_value(value)

            x0 = lon_to_x(lon)
            x1 = lon_to_x(lon + lon_step)
            y0 = lat_to_y(lat + lat_step)
            y1 = lat_to_y(lat)

            add(
                doc,
                f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" '
                f'height="{y1 - y0:.2f}" fill="{color}" fill-opacity="0.72" '
                f'stroke="none"/>',
            )


def draw_graticule(doc: SvgDocument) -> None:
    for lon in range(-180, 181, 60):
        x = lon_to_x(lon)
        add(
            doc,
            f'<line x1="{x:.2f}" y1="{MAP_Y}" x2="{x:.2f}" y2="{MAP_Y + MAP_H}" '
            f'stroke="#1e40af" stroke-opacity="0.28" stroke-width="1"/>',
        )
        add(doc, svg_text(x, MAP_Y + MAP_H + 22, f"{lon}°", size=13, fill="#1e3a8a", anchor="middle"))

    for lat in range(-60, 61, 30):
        y = lat_to_y(lat)
        add(
            doc,
            f'<line x1="{MAP_X}" y1="{y:.2f}" x2="{MAP_X + MAP_W}" y2="{y:.2f}" '
            f'stroke="#1e40af" stroke-opacity="0.28" stroke-width="1"/>',
        )
        add(doc, svg_text(MAP_X - 12, y + 5, f"{lat}°", size=13, fill="#1e3a8a", anchor="end"))


def draw_land(doc: SvgDocument) -> None:
    land_polys = [
        # North America
        [(-168, 72), (-130, 72), (-105, 58), (-96, 50), (-80, 48), (-66, 42), (-80, 25), (-100, 18), (-115, 30), (-128, 42), (-150, 56)],
        # South America
        [(-82, 12), (-62, 8), (-48, -10), (-42, -25), (-54, -55), (-70, -48), (-78, -22)],
        # Greenland
        [(-52, 82), (-28, 76), (-22, 62), (-42, 58), (-58, 68)],
        # Eurasia
        [(-10, 70), (30, 72), (70, 62), (120, 58), (150, 48), (140, 30), (100, 22), (70, 8), (42, 22), (18, 36), (-8, 42)],
        # Africa
        [(-18, 35), (20, 34), (42, 12), (36, -28), (18, -36), (-5, -28), (-16, 6)],
        # Australia
        [(112, -12), (154, -18), (148, -40), (118, -38), (106, -28)],
        # Antarctica
        [(-180, -64), (-120, -72), (-60, -68), (0, -76), (60, -68), (120, -72), (180, -64), (180, -90), (-180, -90)],
    ]

    for poly in land_polys:
        d = polyline_path(poly)
        add(
            doc,
            f'<path d="{d}" fill="#f5deb3" fill-opacity="0.50" '
            f'stroke="#374151" stroke-width="1.6" stroke-linejoin="round"/>',
        )


def draw_map_frame(doc: SvgDocument) -> None:
    add(
        doc,
        f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" rx="18" '
        f'fill="none" stroke="#111827" stroke-width="2.2"/>',
    )

    add(doc, svg_text(MAP_X, MAP_Y - 14, "Synthetic surface anomaly field", size=18, fill="#111827", weight="700"))
    add(
        doc,
        svg_text(
            MAP_X + MAP_W,
            MAP_Y - 14,
            "PlateCarree-like SVG panel, no Matplotlib / no Cartopy",
            size=15,
            fill="#4b5563",
            anchor="end",
        ),
    )


def build_labelbar(doc: SvgDocument) -> None:
    labelbar = HluLabelBar(
        name="geo_demo_adjusted_labelbar",
        rect=(0.18, 0.83, 0.64, 0.10),
        colors=COLORS,
        labels=["-4", "-3", "-2", "-1", "0", "1", "2", "3", "4"],
        resources={
            "lbTitleString": "Synthetic anomaly",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": 0,
            "lbTitleFuncCode": "~",
            "lbTitleFontHeightF": 0.030,
            "lbLabelDirection": "Across",
            "lbLabelJust": "CenterCenter",
            "lbLabelAngleF": 0,
            "lbLabelFuncCode": "~",
            "lbLabelFontHeightF": 0.020,
            "lbJustification": "CenterCenter",
            "lbBoxLinesOn": True,
            "lbBoxSeparatorLinesOn": True,
            "lbPerimOn": True,
        },
    )

    bundle = labelbar.build_uniform_plotchar_metrics_bundle(
        title=PlotcharExtentMetrics(
            dl=0.16,
            dr=0.16,
            db=0.030,
            dt=0.055,
        ),
        label=PlotcharExtentMetrics(
            dl=0.018,
            dr=0.018,
            db=0.010,
            dt=0.020,
        ),
    )

    primitives = labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics(
        labelbar,
        WIDTH,
        HEIGHT,
        title_metrics=bundle.title,
        label_metrics=bundle.labels,
        stroke="#111827",
        text_fill="#111827",
    )

    add_adjusted_labelbar_primitives_to_svg_document(
        primitives,
        doc,
        default_label_font_height=0.014,
    )

    add(
        doc,
        svg_text(
            WIDTH / 2,
            748,
            "LabelBar: explicit supplied-metrics → AdjustGeometry → adjusted SVG primitives",
            size=15,
            fill="#4b5563",
            anchor="middle",
        ),
    )


def main() -> Path:
    out_dir = Path("outputs/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = SvgDocument(
        width=WIDTH,
        height=HEIGHT,
        background="white",
    )

    draw_background(doc)
    draw_synthetic_field(doc)
    draw_graticule(doc)
    draw_land(doc)
    draw_map_frame(doc)
    build_labelbar(doc)

    out_path = out_dir / "geo_demo_with_adjusted_labelbar.svg"
    out_path.write_text(doc.tostring(), encoding="utf-8")

    print(out_path)
    return out_path


if __name__ == "__main__":
    main()
