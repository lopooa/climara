from pathlib import Path


def main():
    source = Path("src/climara/graphics/_panel.py").read_text(encoding="utf-8")

    assert "_labelbar_bottom_rect_to_view_rect" in source
    assert "bottom + height" in source

    forbidden_unconverted = [
        "rect=labelbar_rect,",
        "rect = labelbar_rect,",
        "rect=lb_rect,",
        "rect = lb_rect,",
    ]

    remaining = [item for item in forbidden_unconverted if item in source]
    if remaining:
        raise RuntimeError(f"unconverted panel labelbar rect usage remains: {remaining}")

    converted = [
        "_labelbar_bottom_rect_to_view_rect(labelbar_rect)",
        "_labelbar_bottom_rect_to_view_rect(lb_rect)",
    ]

    if not any(item in source for item in converted):
        raise RuntimeError("panel labelbar rect conversion call not found")

    print("✅ panel labelbar rect View-semantics smoke passed")
    print("✅ panel bottom-rect is converted to HLU vpYF/top rect before LabelBar construction")


if __name__ == "__main__":
    main()
