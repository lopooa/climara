from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import render_object, save_svg


def _labelbar():
    return HluLabelBar(
        rect=(0.2, 0.85, 0.2, 0.5),
        colors=("#2166ac", "#f7f7f7", "#b2182b"),
        labels=("Low", "Mid", "High"),
        resources={
            "lbBoxCount": 3,
            "lbOrientation": "Vertical",
            "lbLabelAlignment": "BoxCenters",
            "lbLabelPosition": "Right",
            "lbLabelAngleF": -45.0,
            "lbLabelsOn": True,
        },
    )


def main():
    out = Path("outputs/figures/render_object_entrypoint_guard_smoke.svg")
    out.parent.mkdir(parents=True, exist_ok=True)

    labelbar = _labelbar()

    try:
        render_object(labelbar, out)
    except TypeError as exc:
        msg = str(exc)
        assert "SvgDocument" in msg
        assert "save_svg" in msg
    else:
        raise RuntimeError("render_object accepted a Path as doc; expected TypeError")

    save_svg(labelbar, out, width=800, height=600)

    text = out.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "rotate(315.000" in text
    assert "Low" in text
    assert "Mid" in text
    assert "High" in text

    print("✅ render_object entrypoint guard smoke passed")
    print("✅ incorrect Path argument fails fast; save_svg remains the full SVG file entrypoint")


if __name__ == "__main__":
    main()
