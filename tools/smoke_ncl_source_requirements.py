from climara.graphics._ncl_source_requirements import (
    NCL_TEXT_BBOX_SOURCE_REQUIREMENTS,
    ncl_text_bbox_requirements_report,
    required_ncl_source_files,
    requirements_by_component,
)


def main():
    files = required_ncl_source_files()

    assert "ni/src/lib/hlu/TextItem.c" in files
    assert "ni/src/lib/hlu/MultiText.c" in files
    assert "ni/src/lib/hlu/LabelBar.c" in files

    symbols = {requirement.symbol for requirement in NCL_TEXT_BBOX_SOURCE_REQUIREMENTS}

    assert "FigureAndSetTextBBInfo" in symbols
    assert "TextItemDraw" in symbols
    assert "GetMaxTextLength" in symbols
    assert "SetDrawFlags" in symbols
    assert "SetTitle" in symbols
    assert "SetLabels" in symbols
    assert "AdjustGeometry" in symbols

    text_item = requirements_by_component("TextItem")
    multitext = requirements_by_component("MultiText")
    labelbar = requirements_by_component("LabelBar")

    assert len(text_item) >= 2
    assert len(multitext) >= 3
    assert len(labelbar) >= 3

    report = ncl_text_bbox_requirements_report()

    assert "Required source files:" in report
    assert "DL / DR / DB / DT" in report
    assert "AutoManage" in report
    assert "Do not implement TextItem bbox" in report

    print("✅ NCL source requirements smoke passed")


if __name__ == "__main__":
    main()
