from pathlib import Path


def main():
    path = Path("docs/ncl_text_bbox_source_map.md")

    if not path.exists():
        raise FileNotFoundError(
            "docs/ncl_text_bbox_source_map.md is missing. "
            "Copy the downloaded Markdown file into docs/ before running this smoke."
        )

    text = path.read_text(encoding="utf-8")

    required = [
        "ni/src/lib/hlu/TextItem.c",
        "ni/src/lib/hlu/MultiText.c",
        "ni/src/lib/hlu/LabelBar.c",
        "FigureAndSetTextBBInfo",
        "c_plchhq",
        "c_pcgetr",
        "TextItem.c around lines 1152-1229",
        "MultiText.c around lines 330-348",
        "MultiText.c around lines 552-625",
        "LabelBar.c around lines 2135-2398",
        "LabelBar.c around lines 3591-3845",
        "Do not implement TextItem / MultiText bbox from visual estimates.",
        "Do not start by changing SVG output.",
        "has_labelbar_adjust_geometry_engine() == False",
        "TextItem bbox engine",
        "MultiText bbox engine",
        "LabelBar AutoManage",
        "LabelBar AdjustGeometry implementation",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("Missing required NCL bbox source-map entries:")
        for item in missing:
            print(f"  - {item}")
        raise SystemExit(1)

    print("✅ NCL TextItem / MultiText / LabelBar bbox source map doc smoke passed")


if __name__ == "__main__":
    main()
