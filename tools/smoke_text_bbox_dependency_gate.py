from pathlib import Path

from climara.graphics._capabilities import graphics_capabilities
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._ncl_source_requirements import (
    NCL_TEXT_BBOX_SOURCE_REQUIREMENTS,
    required_ncl_source_files,
)
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine


def main():
    caps = graphics_capabilities()

    assert caps.plotchar_metrics_engine == has_plotchar_metrics_engine()
    assert caps.text_bbox_engine == has_text_bbox_engine()
    assert caps.labelbar_adjust_geometry_engine == has_labelbar_adjust_geometry_engine()

    if caps.text_bbox_engine:
        assert caps.plotchar_metrics_engine, (
            "TextItem bbox engine cannot be enabled before Plotchar DL / DR / DB / DT metrics "
            "are implemented from audited NCL c_plchhq / c_pcgetr semantics."
        )

    if caps.labelbar_adjust_geometry_engine:
        assert caps.text_bbox_engine, (
            "LabelBar AdjustGeometry cannot be enabled before trustworthy TextItem / MultiText "
            "bbox engines are available."
        )

    assert caps.plotchar_parser is False
    assert caps.down_text_rendering is False

    files = set(required_ncl_source_files())

    assert "ni/src/lib/hlu/TextItem.c" in files
    assert "ni/src/lib/hlu/MultiText.c" in files
    assert "ni/src/lib/hlu/LabelBar.c" in files

    symbols = {item.symbol for item in NCL_TEXT_BBOX_SOURCE_REQUIREMENTS}

    assert "FigureAndSetTextBBInfo" in symbols
    assert "TextItemDraw" in symbols
    assert "GetMaxTextLength" in symbols
    assert "SetDrawFlags" in symbols
    assert "SetTitle" in symbols
    assert "SetLabels" in symbols
    assert "AdjustGeometry" in symbols

    doc = Path("docs/ncl_text_bbox_source_map.md")
    assert doc.exists(), "NCL bbox source map document must exist before bbox work continues"

    text = doc.read_text(encoding="utf-8")
    assert "Do not implement TextItem / MultiText bbox from visual estimates." in text
    assert "Do not start by changing SVG output." in text
    assert "FigureAndSetTextBBInfo" in text
    assert "c_plchhq" in text
    assert "c_pcgetr" in text

    print("✅ TextBBox dependency gate smoke passed")


if __name__ == "__main__":
    main()
