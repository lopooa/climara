from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._plotchar_legacy_digitization_source import (
    require_legacy_digitization_sources,
)


def main():
    ncl_src_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_src_root:
        raise RuntimeError("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    report = require_legacy_digitization_sources(Path(ncl_src_root))

    print("NCL source root:", report.ncl_src_root)
    print("candidate files:", len(report.hits))
    print()

    for hit in report.hits[:80]:
        rel = hit.path.relative_to(report.ncl_src_root)
        terms = ", ".join(hit.matched_terms)
        print(f"{rel}")
        print(f"  terms: {terms}")

    if len(report.hits) > 80:
        print()
        print(f"... {len(report.hits) - 80} more candidate files omitted")

    print()
    print("✅ legacy digitization source scan completed")


if __name__ == "__main__":
    main()
