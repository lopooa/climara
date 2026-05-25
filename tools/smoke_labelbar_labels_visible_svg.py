from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


def _extract_svg_size(text: str) -> tuple[float, float]:
    match = re.search(r'<svg[^>]*\bwidth="([0-9.]+)"[^>]*\bheight="([0-9.]+)"', text)
    if match:
        return float(match.group(1)), float(match.group(2))

    match = re.search(r'<svg[^>]*\bviewBox="[^"]*?\s+([0-9.]+)\s+([0-9.]+)"', text)
    if match:
        return float(match.group(1)), float(match.group(2))

    raise RuntimeError("could not find SVG size")


def _extract_text_positions(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    pattern = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.DOTALL)

    for match in pattern.finditer(text):
        attrs = match.group(1)
        value = re.sub(r"<.*?>", "", match.group(2)).strip()
        y_match = re.search(r'\by="([0-9.\-]+)"', attrs)
        if value and y_match:
            out[value] = float(y_match.group(1))

    return out


def main() -> None:
    proc = subprocess.run(
        [sys.executable, "tools/smoke_panel_labelbar_ncl_contour_info.py"],
        cwd=Path.cwd(),
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    output = Path("outputs") / "figures" / "panel_labelbar_ncl_contour_info_smoke.svg"
    text = output.read_text(encoding="utf-8")

    width, height = _extract_svg_size(text)
    positions = _extract_text_positions(text)

    missing = [label for label in list("ABCDEFGHIJ") if label not in positions]
    if missing:
        raise RuntimeError(f"missing labelbar labels: {missing}")

    outside = {
        label: positions[label]
        for label in list("ABCDEFGHIJ")
        if not (0.0 <= positions[label] <= height)
    }
    if outside:
        raise RuntimeError(f"labelbar labels outside visible SVG height {height}: {outside}")

    print(f"✅ labelbar labels visible smoke passed: {output}")
    print(f"✅ SVG size: {width} x {height}")
    print("✅ A-J labels are inside the SVG canvas")
    for label in list("ABCDEFGHIJ"):
        print(f"  {label}: y={positions[label]:.3f}")


if __name__ == "__main__":
    main()
