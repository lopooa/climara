from climara.graphics import (
    export_resource_compatibility,
    list_supported_resources,
    search_supported_resources,
)


path = export_resource_compatibility()

rows = list_supported_resources()
contour_rows = list_supported_resources(group="ContourPlot")
labelbar_hits = search_supported_resources("labelbar")

print(f"exported {path}")
print(f"total supported entries: {len(rows)}")
print(f"ContourPlot entries: {len(contour_rows)}")
print(f"labelbar search hits: {len(labelbar_hits)}")
