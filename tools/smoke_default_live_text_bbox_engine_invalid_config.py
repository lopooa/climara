from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._ncl_plotchar_ctypes_backend import NclPlotcharCtypesBackendError
from climara.graphics._ncl_plotchar_live_engine import (
    configured_ncl_plotchar_backend_is_requested,
    has_configured_ncl_plotchar_live_engine,
)
from climara.graphics._ncl_plotchar_real_library import (
    NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
    NCL_PLOTCHAR_LIBRARY_ENV,
)
from climara.graphics._text_bbox import build_text_item_bbox_request, compute_text_item_bbox
from climara.graphics._text_semantics import build_text_item_semantics


def main():
    old_lib = os.environ.get(NCL_PLOTCHAR_LIBRARY_ENV)
    old_dirs = os.environ.get(NCL_PLOTCHAR_LIBRARY_DIRS_ENV)

    missing = Path("/tmp/climara_missing_real_ncar_plotchar_library.so")
    os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = str(missing)
    os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)

    try:
        assert configured_ncl_plotchar_backend_is_requested() is True
        assert has_configured_ncl_plotchar_live_engine() is False

        request = build_text_item_bbox_request(
            build_text_item_semantics("ABC", func_code="~"),
            x=0.4,
            y=0.6,
        )

        try:
            compute_text_item_bbox(request)
        except NclPlotcharCtypesBackendError as exc:
            message = str(exc)
            assert "validation failed" in message or "shared library" in message
            assert "c_pcseti" in message
            assert "c_plchhq" in message
        else:
            raise AssertionError("Invalid explicit live engine config must not fall back to heuristics")

        print("✅ Default live TextItem engine invalid-config guard smoke passed")
    finally:
        if old_lib is None:
            os.environ.pop(NCL_PLOTCHAR_LIBRARY_ENV, None)
        else:
            os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = old_lib

        if old_dirs is None:
            os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)
        else:
            os.environ[NCL_PLOTCHAR_LIBRARY_DIRS_ENV] = old_dirs


if __name__ == "__main__":
    main()
