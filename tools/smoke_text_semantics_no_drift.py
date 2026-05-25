from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "labelbar_geometry": ROOT / "src/climara/graphics/_labelbar_geometry.py",
    "labelbar_svg_adapter": ROOT / "src/climara/graphics/_labelbar_svg_adapter.py",
    "render_svg": ROOT / "src/climara/graphics/_render_svg.py",
}


def _read(name):
    return FILES[name].read_text(encoding="utf-8")


def main():
    geometry = _read("labelbar_geometry")
    adapter = _read("labelbar_svg_adapter")
    render = _read("render_svg")

    assert "build_text_item_semantics" in geometry
    assert "build_text_item_semantics" in adapter
    assert "text_uses_func_code" in render

    forbidden_adapter_fragments = [
        '"nhlacross"',
        '"nhldown"',
        '"nhlmedium"',
        '"nhllow"',
        '"nhlworkstation"',
        'dir_code = "D"',
        'dir_code = "A"',
        "return f\"{code}{dir_code}{code}",
    ]

    for fragment in forbidden_adapter_fragments:
        assert fragment not in adapter, (
            "LabelBar SVG adapter should delegate TextItem normalization "
            f"to _text_semantics.py, found duplicate fragment: {fragment}"
        )

    forbidden_render_fragments = [
        "func_code in str(",
        "code in str(",
    ]

    for fragment in forbidden_render_fragments:
        assert fragment not in render, (
            "SVG renderer should delegate Plotchar function-code detection "
            f"to _text_semantics.py, found duplicate fragment: {fragment}"
        )

    assert "LabelBarGeometry" in geometry
    assert "label_func_code" not in geometry
    assert "label_direction" not in geometry

    print("✅ TextItem semantics no-drift smoke passed")


if __name__ == "__main__":
    main()
