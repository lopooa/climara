from __future__ import annotations

from html import escape
from pathlib import Path


W = 1600
H = 1100


def svg_text(
    x,
    y,
    text,
    size=24,
    fill="#1f2937",
    weight="400",
    anchor="start",
    family="Arial, 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif",
):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
        f'{escape(str(text))}</text>'
    )


def svg_multiline(x, y, lines, size=22, fill="#1f2937", weight="400", line_gap=32):
    out = []
    for i, line in enumerate(lines):
        out.append(svg_text(x, y + i * line_gap, line, size=size, fill=fill, weight=weight))
    return "\n".join(out)


def rounded_rect(x, y, w, h, fill, stroke="#d1d5db", sw=2, rx=18):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def circle(x, y, r, fill, stroke="none", sw=0):
    return (
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"/>'
    )


def line(x1, y1, x2, y2, stroke="#2563eb", sw=3, dash=None):
    dash_attr = "" if dash is None else f' stroke-dasharray="{dash}"'
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{dash_attr}/>'
    )


def arrow_down(x, y1, y2, stroke="#1d4ed8"):
    return "\n".join(
        [
            line(x, y1, x, y2 - 10, stroke=stroke, sw=3),
            f'<path d="M {x - 7} {y2 - 12} L {x} {y2} L {x + 7} {y2 - 12}" '
            f'fill="none" stroke="{stroke}" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round"/>',
        ]
    )


def check_icon(x, y, r=18):
    return "\n".join(
        [
            circle(x, y, r, "#15803d"),
            f'<path d="M {x - 8} {y} L {x - 2} {y + 7} L {x + 10} {y - 9}" '
            f'fill="none" stroke="white" stroke-width="4" stroke-linecap="round" '
            f'stroke-linejoin="round"/>',
        ]
    )


def warning_icon(x, y):
    return "\n".join(
        [
            f'<path d="M {x} {y - 24} L {x - 28} {y + 24} L {x + 28} {y + 24} Z" '
            f'fill="#ea580c"/>',
            svg_text(x, y + 16, "!", size=34, fill="white", weight="700", anchor="middle"),
        ]
    )


def pill(x, y, w, text, fill, stroke, text_color, icon_text=None):
    out = [rounded_rect(x, y, w, 48, fill, stroke=stroke, sw=2, rx=24)]
    tx = x + 28
    if icon_text:
        out.append(circle(x + 34, y + 24, 15, stroke))
        out.append(svg_text(x + 34, y + 31, icon_text, size=16, fill="white", weight="700", anchor="middle"))
        tx = x + 60
    out.append(svg_text(tx, y + 31, text, size=22, fill=text_color, weight="700"))
    return "\n".join(out)


def draw_completed_panel():
    x, y, w, h = 24, 28, 390, 715
    items = [
        ["无 Matplotlib 运行时"],
        ["无 Cartopy 绘图运行时依赖"],
        ["SVG 后端基础可用"],
        ["TextItem / MultiText", "语义层已建立"],
        ["LabelBar title / label bbox", "supplied-metrics 管线已打通"],
        ["AdjustGeometry supplied-bbox", "执行链已完成"],
        ["explicit adjusted SVG", "导出可用"],
        ["函数式 API、对象式 API、", "provider API 已具备"],
    ]

    out = [
        rounded_rect(x, y, w, h, "#f0fdf4", "#15803d", 2, 18),
        check_icon(x + 50, y + 46, 27),
        svg_text(x + 92, y + 56, "已经完成", size=34, fill="#166534", weight="800"),
    ]

    yy = y + 116
    for item in items:
        out.append(check_icon(x + 42, yy - 8, 16))
        out.append(svg_multiline(x + 78, yy, item, size=22, fill="#111827", line_gap=30))
        yy += 82 if len(item) > 1 else 56

    return "\n".join(out)


def draw_todo_panel():
    x, y, w, h = 1180, 28, 390, 715
    items = [
        ["live Plotchar metrics engine"],
        ["live TextItem bbox engine"],
        ["live MultiText bbox engine"],
        ["default renderer 自动接入", "adjusted LabelBar"],
        ["NCL Plotchar function-code", "parser"],
        ["NhlDOWN / Down", "文本渲染"],
        ["full LabelBar AutoManage", "parity"],
    ]

    out = [
        rounded_rect(x, y, w, h, "#fff7ed", "#f97316", 2, 18),
        warning_icon(x + 52, y + 50),
        svg_text(x + 96, y + 58, "当前还未完成", size=32, fill="#c2410c", weight="800"),
    ]

    yy = y + 132
    for item in items:
        out.append(circle(x + 36, yy - 8, 8, "#f59e0b"))
        out.append(svg_multiline(x + 66, yy, item, size=22, fill="#111827", line_gap=30))
        yy += 88 if len(item) > 1 else 62

    return "\n".join(out)


def draw_pipeline():
    x, y = 455, 35
    w = 650
    header_h = 58

    steps = [
        "HluLabelBar",
        "PlotcharExtentMetrics / metrics bundle / provider",
        "TextItem bbox semantics",
        "MultiText bbox semantics",
        "LabelBar title / labels bbox semantics",
        "AdjustGeometry request",
        "AdjustGeometry execution result",
        "materialized snapshot",
        "adjusted LabelBarGeometry",
        "adjusted SVG primitives",
        "adjusted SVG file export",
    ]

    out = [
        rounded_rect(x - 10, y, w + 20, header_h, "#1d4ed8", "#1d4ed8", 2, 12),
        svg_text(x + 22, y + 38, "已完成的显式 LabelBar 管线（explicit）", size=28, fill="white", weight="800"),
    ]

    box_x = x + 10
    box_w = w - 70
    box_h = 43
    gap = 18
    yy = y + 82

    for i, step in enumerate(steps, start=1):
        out.append(rounded_rect(box_x, yy, box_w, box_h, "#eff6ff", "#1d4ed8", 2, 9))
        out.append(circle(box_x + 28, yy + box_h / 2, 17, "#1d4ed8"))
        out.append(svg_text(box_x + 28, yy + 27, str(i), size=18, fill="white", weight="800", anchor="middle"))
        out.append(svg_text(box_x + box_w / 2 + 18, yy + 28, step, size=21, fill="#111827", weight="700", anchor="middle"))

        if i < len(steps):
            out.append(arrow_down(box_x + box_w / 2, yy + box_h, yy + box_h + gap, stroke="#1d4ed8"))

        yy += box_h + gap

    brace_x = box_x + box_w + 30
    top = y + 82
    bottom = yy - gap
    mid = (top + bottom) / 2
    out.append(
        f'<path d="M {brace_x} {top} C {brace_x + 34} {top} {brace_x + 34} {top + 54} {brace_x + 34} {top + 70} '
        f'L {brace_x + 34} {mid - 36} C {brace_x + 34} {mid - 10} {brace_x + 62} {mid - 10} {brace_x + 62} {mid} '
        f'C {brace_x + 62} {mid + 10} {brace_x + 34} {mid + 10} {brace_x + 34} {mid + 36} '
        f'L {brace_x + 34} {bottom - 70} C {brace_x + 34} {bottom - 54} {brace_x + 34} {bottom} {brace_x} {bottom}" '
        f'fill="none" stroke="#1d4ed8" stroke-width="4" stroke-linecap="round"/>'
    )
    out.append(svg_text(brace_x + 92, mid - 20, "完成", size=34, fill="#1d4ed8", weight="800", anchor="middle"))
    out.append(check_icon(brace_x + 92, mid + 36, 30))

    return "\n".join(out)


def draw_status_panel():
    x, y, w, h = 24, 760, 610, 205

    out = [
        rounded_rect(x, y, w, h, "#eff6ff", "#2563eb", 2, 16),
        circle(x + 42, y + 36, 22, "#2563eb"),
        svg_text(x + 42, y + 45, "i", size=25, fill="white", weight="800", anchor="middle"),
        svg_text(x + 76, y + 48, "状态理解", size=28, fill="#1e40af", weight="800"),
    ]

    rows = [
        ("当前最成熟的是：", "LabelBar supplied-metrics AdjustGeometry 显式管线。"),
        ("现在已经可以：", "手动提供 Plotchar metrics，输出经过 AdjustGeometry 的 LabelBar SVG。"),
        ("后续关键难点：", "真实 NCL Plotchar metrics 自动计算。"),
    ]

    yy = y + 88
    for i, (lead, txt) in enumerate(rows):
        out.append(circle(x + 42, yy - 7, 13, "#2563eb"))
        out.append(svg_text(x + 76, yy, lead, size=20, fill="#1e40af", weight="800"))
        out.append(svg_text(x + 240, yy, txt, size=20, fill="#111827", weight="400"))
        if i < len(rows) - 1:
            out.append(line(x + 30, yy + 25, x + w - 30, yy + 25, stroke="#93c5fd", sw=2, dash="6 8"))
        yy += 54

    return "\n".join(out)


def draw_result_preview():
    x, y, w, h = 680, 760, 890, 205

    bar_x = x + 95
    bar_y = y + 98
    bar_w = w - 190
    bar_h = 52
    segment_w = bar_w / 4

    colors = ["#3b82f6", "#bfdbfe", "#fed7aa", "#dc2626"]
    labels = ["Cold", "Cool", "Warm", "Hot"]

    out = [
        rounded_rect(x, y, w, h, "#faf5ff", "#7c3aed", 2, 16),
        circle(x + 42, y + 36, 22, "#7c3aed"),
        svg_text(x + 42, y + 45, "SVG", size=11, fill="white", weight="800", anchor="middle"),
        svg_text(x + 76, y + 48, "结果示意", size=28, fill="#6d28d9", weight="800"),
        svg_text(x + w / 2, y + 84, "Adjusted LabelBar demo", size=24, fill="#111827", weight="800", anchor="middle"),
    ]

    for i, c in enumerate(colors):
        sx = bar_x + i * segment_w
        out.append(
            f'<rect x="{sx}" y="{bar_y}" width="{segment_w}" height="{bar_h}" '
            f'fill="{c}" stroke="#111827" stroke-width="2"/>'
        )

    for i, lab in enumerate(labels):
        tx = bar_x + segment_w * (i + 0.5)
        out.append(svg_text(tx, bar_y + bar_h + 38, lab, size=22, fill="#111827", anchor="middle"))

    out.append(
        svg_text(
            x + w / 2,
            y + h - 26,
            "示例：水平 LabelBar，4 个 box，带分隔线与标题（经 AdjustGeometry 调整后）",
            size=17,
            fill="#4b5563",
            anchor="middle",
        )
    )

    return "\n".join(out)


def draw_badges():
    y = 1010
    badges = [
        (150, 160, "explicit only", "#eff6ff", "#2563eb", "#1e40af", "</>"),
        (405, 150, "opt-in", "#f0fdf4", "#16a34a", "#166534", "✓"),
        (620, 170, "SVG export", "#f5f3ff", "#7c3aed", "#6d28d9", "SVG"),
        (850, 210, "provider-ready", "#ecfeff", "#0891b2", "#155e75", "□"),
        (1130, 250, "NCL-source-guided", "#fff7ed", "#ea580c", "#c2410c", "📖"),
    ]

    out = []
    for x, w, text, fill, stroke, color, icon in badges:
        out.append(pill(x, y, w, text, fill, stroke, color, icon_text=icon))
    return "\n".join(out)


def build_svg():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        draw_completed_panel(),
        draw_pipeline(),
        draw_todo_panel(),
        draw_status_panel(),
        draw_result_preview(),
        draw_badges(),
        "</svg>",
    ]
    return "\n".join(parts)


def main():
    out_dir = Path("outputs/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "climara_current_progress_overview.svg"
    out_path.write_text(build_svg(), encoding="utf-8")

    print(out_path)


if __name__ == "__main__":
    main()
