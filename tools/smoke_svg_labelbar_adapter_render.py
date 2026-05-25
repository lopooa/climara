from pathlib import Path


def main():
    source = Path("src/climara/graphics/_render_svg.py").read_text(encoding="utf-8")

    start = source.find("def _render_labelbar(")
    end = source.find("\ndef render_object(", start)
    block = source[start:end]

    required = [
        "labelbar_to_svg_primitives",
        "for polygon in primitives.polygons",
        "for line in primitives.lines",
        "for text_item in primitives.texts",
        "<polygon",
        "<line",
        "<text",
        "polygon.stroke_width",
        "line.stroke_width",
    ]

    missing = [item for item in required if item not in block]
    if missing:
        raise RuntimeError(f"renderer does not consume expected LabelBar primitives: {missing}")

    forbidden = [
        "box_width =",
        "box_height =",
        "axis_positions =",
        "_labelbar_label_positions(obj, len(labels))",
        "inner_width =",
        "inner_height =",
    ]

    present = [item for item in forbidden if item in block]
    if present:
        raise RuntimeError(f"_render_labelbar still computes LabelBar geometry directly: {present}")

    print("✅ SVG LabelBar primitive renderer smoke passed")
    print("✅ _render_labelbar consumes adapter primitives instead of computing LabelBar geometry")


if __name__ == "__main__":
    main()
