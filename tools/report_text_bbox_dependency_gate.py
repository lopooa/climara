from climara.graphics._capabilities import graphics_capabilities
from climara.graphics._ncl_source_requirements import required_ncl_source_files


def main():
    caps = graphics_capabilities()

    print("TextBBox dependency gate")
    print("=" * 24)
    print()

    print("Current engine flags")
    print("-" * 20)
    print(f"plotchar_metrics_engine: {caps.plotchar_metrics_engine}")
    print(f"text_bbox_engine: {caps.text_bbox_engine}")
    print(f"labelbar_adjust_geometry_engine: {caps.labelbar_adjust_geometry_engine}")
    print(f"plotchar_parser: {caps.plotchar_parser}")
    print(f"down_text_rendering: {caps.down_text_rendering}")

    print()
    print("Required order")
    print("-" * 14)
    print("1. Audit TextItem.c::FigureAndSetTextBBInfo.")
    print("2. Implement or explicitly guard Plotchar DL / DR / DB / DT metrics.")
    print("3. Only then implement a narrow TextItem bbox engine.")
    print("4. Use TextItem bbox results for MultiText bbox aggregation.")
    print("5. Only then revisit LabelBar AdjustGeometry / AutoManage.")

    print()
    print("Required NCL source files")
    print("-" * 25)
    for path in required_ncl_source_files():
        print(f"- {path}")

    print()
    print("Current status")
    print("-" * 14)
    if not caps.plotchar_metrics_engine:
        print("Blocked: Plotchar metrics engine is not implemented.")
    if not caps.text_bbox_engine:
        print("Blocked: TextItem / MultiText bbox engine is not implemented.")
    if not caps.labelbar_adjust_geometry_engine:
        print("Blocked: LabelBar AdjustGeometry / AutoManage is not implemented.")


if __name__ == "__main__":
    main()
