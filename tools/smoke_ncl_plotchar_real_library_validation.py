from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._ncl_plotchar_ctypes_backend import NclPlotcharCtypesBackendError
from climara.graphics._ncl_plotchar_real_library import (
    NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
    NCL_PLOTCHAR_LIBRARY_ENV,
    REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS,
    build_validated_ncl_plotchar_ctypes_backend,
    configured_ncl_plotchar_library_status_report,
    explicit_ncl_plotchar_library_paths,
    split_path_list,
    validate_configured_ncl_plotchar_library,
    validate_ncl_plotchar_library_paths,
)
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine


def main():
    old_lib = os.environ.pop(NCL_PLOTCHAR_LIBRARY_ENV, None)
    old_dirs = os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)

    try:
        assert split_path_list(None) == ()
        assert explicit_ncl_plotchar_library_paths() == ()

        validation = validate_configured_ncl_plotchar_library()
        assert validation.ok is False
        assert validation.requested_paths == ()
        assert validation.existing_paths == ()
        assert validation.missing_paths == ()
        assert validation.missing_symbols == REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS

        report = configured_ncl_plotchar_library_status_report()
        assert f"{NCL_PLOTCHAR_LIBRARY_ENV}=<unset>" in report
        assert "fixed-width" in report
        assert "browser text metrics" in report

        missing_path = Path("/tmp/climara-missing-ncl-plotchar-library.so")
        validation = validate_ncl_plotchar_library_paths([missing_path])
        assert validation.ok is False
        assert validation.requested_paths == (missing_path,)
        assert validation.existing_paths == ()
        assert validation.missing_paths == (missing_path,)

        os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = str(missing_path)
        try:
            build_validated_ncl_plotchar_ctypes_backend()
        except NclPlotcharCtypesBackendError as exc:
            assert "validation failed" in str(exc)
        else:
            raise AssertionError("missing real Plotchar library must remain guarded")

        assert isinstance(has_plotchar_metrics_engine(), bool)

    finally:
        if old_lib is not None:
            os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = old_lib
        else:
            os.environ.pop(NCL_PLOTCHAR_LIBRARY_ENV, None)

        if old_dirs is not None:
            os.environ[NCL_PLOTCHAR_LIBRARY_DIRS_ENV] = old_dirs
        else:
            os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)

    print("✅ NCL Plotchar real library validation smoke passed")


if __name__ == "__main__":
    main()
