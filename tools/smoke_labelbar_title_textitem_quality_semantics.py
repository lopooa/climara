from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives


def _quality(value, expected):
    geom = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitleFontQuality": value,
        },
    ).compute_geometry()

    assert geom.title_text_item is not None
    assert geom.title_text_item.font_quality == value
    assert geom.title_text_item.quality_index == expected

    primitives = labelbar_to_svg_primitives(
        HluLabelBar(
            resources={
                "lbTitleString": "Demo title",
                "lbTitleFontQuality": value,
            },
        ),
        900,
        500,
    )

    assert len(primitives.title_texts) == 1
    assert primitives.title_texts[0].font_quality == value
    assert primitives.title_texts[0].quality_index == expected


def main():
    _quality("High", 0)
    _quality("NhlHigh", 0)
    _quality("Medium", 1)
    _quality("NhlMedium", 1)
    _quality("Low", 2)
    _quality("NhlLow", 2)
    _quality("Workstation", 3)
    _quality("NhlWorkstation", 3)

    default_geom = HluLabelBar(
        resources={"lbTitleString": "Demo title"}
    ).compute_geometry()

    assert default_geom.title_text_item is not None
    assert default_geom.title_text_item.font_quality == "High"
    assert default_geom.title_text_item.quality_index == 0

    print("✅ LabelBar title TextItem quality semantics smoke passed")


if __name__ == "__main__":
    main()
