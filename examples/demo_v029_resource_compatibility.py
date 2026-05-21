from __future__ import annotations

from climara.plotting import (
    export_resource_compatibility,
    print_resource_compatibility_summary,
    search_supported_resources,
)


def main():
    print_resource_compatibility_summary()

    path = export_resource_compatibility(
        "docs/ncl_resource_compatibility.md"
    )

    print(f"Generated: {path}")

    print()
    print("Search examples:")

    for keyword in ["cnFill", "mpProjection", "LabelBar", "gsnPolar"]:
        hits = search_supported_resources(keyword)
        print(f"  {keyword}: {len(hits)} hit(s)")


if __name__ == "__main__":
    main()
