from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


ROOT = Path(__file__).resolve().parents[1]


def _save(labelbar, filename):
    out = ROOT / "outputs" / "smoke" / filename
    save_svg(labelbar, out, width=900, height=500)
    return out.read_text(encoding="utf-8")


def _expect_not_implemented(labelbar, filename, required_parts):
    try:
        _save(labelbar, filename)
    except NotImplementedError as exc:
        message = str(exc)
        for part in required_parts:
            assert part in message, message
    else:
        raise AssertionError("expected NotImplementedError")


def _base_labelbar(labels=None, **resources):
    if labels is None:
        labels = ["A", "B", "C", "D"]

    merged = {
        "lbTitleString": "Plain title",
        "lbTitlePosition": "Top",
        "lbLabelDirection": "Across",
        "lbLabelFuncCode": "~",
    }
    merged.update(resources)

    return HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=labels,
        resources=merged,
    )


def _assert_doc_boundary():
    doc = ROOT / "docs" / "no_matplotlib_remaining_work.md"
    assert doc.exists(), "missing docs/no_matplotlib_remaining_work.md"

    text = doc.read_text(encoding="utf-8")

    required_terms = [
        "Plotchar function-code parsing",
        "Down-direction TextItem rendering",
        "TextItem bounding boxes",
        "MultiText bounding boxes",
        "LabelBar AutoManage",
        "LabelBar AdjustGeometry",
        "NotImplementedError",
    ]

    for term in required_terms:
        assert term in text, term


def main():
    _assert_doc_boundary()

    ordinary = _base_labelbar(lbTitleString="Ordinary title")
    ordinary_svg = _save(ordinary, "svg_textitem_not_complete_guard_ordinary.svg")
    assert "Ordinary title" in ordinary_svg
    assert ">A<" in ordinary_svg

    down_title = _base_labelbar(
        lbTitleString="Left title",
        lbTitlePosition="Left",
    )
    primitives = labelbar_to_svg_primitives(down_title, 900, 500)
    assert primitives.title_texts
    assert primitives.title_texts[0].direction == "Down"

    _expect_not_implemented(
        down_title,
        "svg_textitem_not_complete_guard_down_title.svg",
        ("TextItem direction 'Down'", "Plotchar vertical text"),
    )

    down_labels = _base_labelbar(lbLabelDirection="Down")
    primitives = labelbar_to_svg_primitives(down_labels, 900, 500)
    assert primitives.texts
    assert all(text.direction == "Down" for text in primitives.texts)

    _expect_not_implemented(
        down_labels,
        "svg_textitem_not_complete_guard_down_labels.svg",
        ("TextItem direction 'Down'", "Plotchar vertical text"),
    )

    title_with_codes = _base_labelbar(lbTitleString="Speed ~S~2~N~")
    _expect_not_implemented(
        title_with_codes,
        "svg_textitem_not_complete_guard_title_codes.svg",
        ("Plotchar function-code sequences", "plain SVG text"),
    )

    labels_with_codes = _base_labelbar(labels=["A", "B ~S~2~N~", "C", "D"])
    primitives = labelbar_to_svg_primitives(labels_with_codes, 900, 500)
    assert primitives.texts
    assert any(text.text == "B ~S~2~N~" for text in primitives.texts)

    _expect_not_implemented(
        labels_with_codes,
        "svg_textitem_not_complete_guard_label_codes.svg",
        ("Plotchar function-code sequences", "plain SVG text"),
    )

    print("✅ TextItem incomplete-semantics guard smoke passed")


if __name__ == "__main__":
    main()
