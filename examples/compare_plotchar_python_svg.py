from __future__ import annotations

import html
import os
from pathlib import Path

from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures" / "python_plotchar_text_compare.svg"


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)
    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise RuntimeError("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")
    return Path(ncl_root) / "common" / "src" / "fontcap"


def base_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 0)
    return state


def func_code(state: PlotcharState) -> str:
    return chr(state.nfcc) if state.nfcc >= 0 else ":"


def real_string(state: PlotcharState, body: str, direction: str = "A") -> str:
    code = func_code(state)
    return f"{code}{direction}{code}{body}"


def compute_case(label: str, body_builder, size: float = 0.035):
    state = base_state()
    code = func_code(state)
    body = body_builder(code)
    try:
        result = compute_plchhq_fontcap_text_extent(
            chrs=real_string(state, body),
            state=state,
            xpos=0.5,
            ypos=0.5,
            size=size,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
        )
        return {
            "label": label,
            "body": body,
            "ok": True,
            "text": result.text,
            "font_number": result.font_number,
            "glyph_count": result.glyph_count,
            "metrics": result.metrics,
            "error": "",
        }
    except PlotcharUnsupportedError as exc:
        return {
            "label": label,
            "body": body,
            "ok": False,
            "text": "",
            "font_number": -1,
            "glyph_count": 0,
            "metrics": None,
            "error": str(exc),
        }


def cases():
    return [
        ("Plain", lambda c: "ABC abc 123"),
        ("Subscript B/N", lambda c: f"H{c}B{c}2{c}N{c}O"),
        ("Superscript S/N", lambda c: f"x{c}S{c}2{c}N{c} + y{c}S{c}2{c}N{c}"),
        ("Script B/S/E/N", lambda c: f"A{c}B{c}sub{c}E{c}B{c}sub2{c}N{c}  B{c}S{c}sup{c}E{c}S{c}sup2{c}N{c}"),
        ("Font switch F22/F21", lambda c: f"Font21 {c}F22{c}Font22 {c}F21{c}Font21"),
        ("Case U/L", lambda c: f"{c}U{c}abc DEF{c}L{c} ABC def{c}N{c}"),
        ("Carriage C", lambda c: f"Line1{c}C{c}Line2"),
        ("Movement H/V", lambda c: f"A{c}H15{c}B{c}V10{c}C"),
        ("Zoom X/Y/Z", lambda c: f"A{c}X130{c}B{c}Y80{c}C{c}Z100{c}"),
    ]


def svg_text(x, y, text, size=18, weight="normal", anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">'
        f"{html.escape(str(text))}</text>"
    )


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [compute_case(label, builder) for label, builder in cases()]

    width = 1280
    row_h = 108
    top = 92
    height = top + row_h * len(rows) + 120
    origin_x = 500
    scale = 2800.0

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append(svg_text(40, 42, "Python climara Plotchar diagnostic SVG", size=24, weight="bold"))
    parts.append(svg_text(40, 70, "Interpreted text + computed bbox from Python Plotchar/fontcap measurement path.", size=14))
    parts.append(svg_text(40, 90, "Glyph shape uses SVG/browser text here; compare layout and bbox semantics, not final NCL glyph shape.", size=14))

    for i, row in enumerate(rows):
        y = top + i * row_h + 55
        parts.append(f'<line x1="30" x2="{width - 30}" y1="{y + 38}" y2="{y + 38}" stroke="#ddd" stroke-width="1"/>')
        parts.append(svg_text(40, y - 24, row["label"], size=16, weight="bold"))
        parts.append(svg_text(40, y - 2, "body: " + row["body"].replace("\n", "\\n"), size=12))
        parts.append(f'<line x1="{origin_x - 260}" x2="{origin_x + 360}" y1="{y}" y2="{y}" stroke="#bbb" stroke-width="1"/>')
        parts.append(f'<line x1="{origin_x}" x2="{origin_x}" y1="{y - 38}" y2="{y + 38}" stroke="#bbb" stroke-width="1"/>')
        parts.append(f'<circle cx="{origin_x}" cy="{y}" r="3" fill="black"/>')

        if row["ok"]:
            m = row["metrics"]
            left = origin_x + m.dl * scale
            right = origin_x + m.dr * scale
            top_y = y - m.dt * scale
            bottom_y = y - m.db * scale
            parts.append(
                f'<rect x="{left:.3f}" y="{top_y:.3f}" width="{right - left:.3f}" height="{bottom_y - top_y:.3f}" '
                f'fill="none" stroke="red" stroke-width="1.6"/>'
            )
            parts.append(svg_text(origin_x, y - 8, row["text"], size=30, anchor="middle"))
            parts.append(svg_text(900, y - 18, f"text={row['text']!r}", size=13))
            parts.append(svg_text(900, y + 2, f"font={row['font_number']} glyphs={row['glyph_count']}", size=13))
            parts.append(svg_text(900, y + 22, f"DL={m.dl:.5g} DR={m.dr:.5g} DB={m.db:.5g} DT={m.dt:.5g}", size=13))
        else:
            parts.append(svg_text(origin_x, y, "GUARDED / UNSUPPORTED", size=20, weight="bold", anchor="middle"))
            parts.append(svg_text(900, y - 6, row["error"][:96], size=12))

    parts.append("</svg>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
