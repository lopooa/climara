from __future__ import annotations

import ctypes
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from ._ncl_plotchar_ctypes_backend import (
    NclPlotcharCtypesBackend,
    NclPlotcharCtypesBackendError,
    build_ncl_plotchar_ctypes_backend,
)

NCL_PLOTCHAR_LIBRARY_ENV = "CLIMARA_NCL_PLOTCHAR_LIB"
NCL_PLOTCHAR_LIBRARY_DIRS_ENV = "CLIMARA_NCL_PLOTCHAR_LIB_DIRS"

REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS = (
    "c_pcseti",
    "c_pcsetr",
    "c_pcsetc",
    "c_plchhq",
    "c_pcgetr",
)

# These names are only searched in explicitly supplied directories. climara must
# not silently guess or fall back to an unrelated text-metrics engine.
NCL_PLOTCHAR_CANDIDATE_LIBRARY_NAMES = (
    "libncarg.so",
    "libncarg.so.0",
    "libncarg_gks.so",
    "libncarg_c.so",
    "libncl.so",
)


@dataclass(frozen=True)
class NclPlotcharLibraryValidation:
    requested_paths: tuple[Path, ...]
    existing_paths: tuple[Path, ...]
    missing_paths: tuple[Path, ...]
    missing_symbols: tuple[str, ...]
    load_errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        # `missing_paths` is informational. When the user supplies an explicit
        # directory, climara expands a short candidate-name list; most candidates
        # may not exist even when one real library is valid. The validation is OK
        # only when at least one existing library loads and exposes every required
        # NCAR/NCL Plotchar C wrapper symbol.
        return (
            len(self.existing_paths) > 0
            and len(self.missing_symbols) == 0
            and len(self.load_errors) == 0
        )

    def require_ok(self) -> None:
        if self.ok:
            return

        raise NclPlotcharCtypesBackendError(
            "NCAR/NCL Plotchar shared library validation failed.\n"
            + ncl_plotchar_library_validation_report(self)
        )


def split_path_list(value: str | None) -> tuple[Path, ...]:
    if value is None:
        return ()

    parts = [part.strip() for part in value.split(os.pathsep)]
    return tuple(Path(part).expanduser() for part in parts if part)


def _dedupe_paths(paths: Iterable[Path]) -> tuple[Path, ...]:
    out = []
    seen = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return tuple(out)


def explicit_ncl_plotchar_library_paths(
    *,
    library_env: str = NCL_PLOTCHAR_LIBRARY_ENV,
    library_dirs_env: str = NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
) -> tuple[Path, ...]:
    """Return only explicitly configured candidate library paths.

    `CLIMARA_NCL_PLOTCHAR_LIB` may contain one or more shared-library files
    separated by `os.pathsep`.

    `CLIMARA_NCL_PLOTCHAR_LIB_DIRS` may contain one or more directories; climara
    only searches the small NCAR/NCL candidate-name list inside those explicit
    directories. It does not scan the whole system and does not guess a backend.
    """
    paths = list(split_path_list(os.environ.get(library_env)))

    for directory in split_path_list(os.environ.get(library_dirs_env)):
        for name in NCL_PLOTCHAR_CANDIDATE_LIBRARY_NAMES:
            paths.append(directory / name)

    return _dedupe_paths(paths)


def _load_cdll(path: Path) -> ctypes.CDLL:
    mode = getattr(ctypes, "RTLD_GLOBAL", 0)
    return ctypes.CDLL(str(path), mode=mode)


def _symbol_exists(libraries: Sequence[ctypes.CDLL], symbol: str) -> bool:
    for library in reversed(tuple(libraries)):
        if hasattr(library, symbol):
            return True
    return False


def validate_ncl_plotchar_library_paths(
    paths: Sequence[str | os.PathLike[str] | Path],
) -> NclPlotcharLibraryValidation:
    requested = tuple(Path(path).expanduser() for path in paths)
    existing = tuple(path for path in requested if path.exists())
    missing = tuple(path for path in requested if not path.exists())

    load_errors: list[str] = []
    libraries: list[ctypes.CDLL] = []

    for path in existing:
        try:
            libraries.append(_load_cdll(path))
        except OSError as exc:
            load_errors.append(f"{path}: {exc}")

    if libraries:
        missing_symbols = tuple(
            symbol
            for symbol in REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS
            if not _symbol_exists(libraries, symbol)
        )
    else:
        missing_symbols = REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS

    return NclPlotcharLibraryValidation(
        requested_paths=requested,
        existing_paths=existing,
        missing_paths=missing,
        missing_symbols=missing_symbols,
        load_errors=tuple(load_errors),
    )


def validate_configured_ncl_plotchar_library(
    *,
    library_env: str = NCL_PLOTCHAR_LIBRARY_ENV,
    library_dirs_env: str = NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
) -> NclPlotcharLibraryValidation:
    return validate_ncl_plotchar_library_paths(
        explicit_ncl_plotchar_library_paths(
            library_env=library_env,
            library_dirs_env=library_dirs_env,
        )
    )


def build_validated_ncl_plotchar_ctypes_backend(
    paths: Sequence[str | os.PathLike[str] | Path] | None = None,
    *,
    library_env: str = NCL_PLOTCHAR_LIBRARY_ENV,
    library_dirs_env: str = NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
) -> NclPlotcharCtypesBackend:
    if paths is None:
        configured_paths = explicit_ncl_plotchar_library_paths(
            library_env=library_env,
            library_dirs_env=library_dirs_env,
        )
    else:
        configured_paths = tuple(Path(path).expanduser() for path in paths)

    if not configured_paths:
        raise NclPlotcharCtypesBackendError(
            f"No NCAR/NCL Plotchar shared library is configured. Set {library_env} "
            f"to the real shared library path, or set {library_dirs_env} to an "
            "explicit directory containing the NCAR/NCL Plotchar library. climara "
            "will not approximate Plotchar metrics."
        )

    validation = validate_ncl_plotchar_library_paths(configured_paths)
    validation.require_ok()
    return build_ncl_plotchar_ctypes_backend(validation.existing_paths)


def ncl_plotchar_library_validation_report(
    validation: NclPlotcharLibraryValidation,
) -> str:
    lines = [
        "NCAR/NCL Plotchar shared library validation",
        "=" * 45,
        "",
        f"ok: {validation.ok}",
        "",
        "requested paths:",
    ]

    if validation.requested_paths:
        lines.extend(f"- {path}" for path in validation.requested_paths)
    else:
        lines.append("- <none>")

    lines.append("")
    lines.append("existing paths:")
    if validation.existing_paths:
        lines.extend(f"- {path}" for path in validation.existing_paths)
    else:
        lines.append("- <none>")

    lines.append("")
    lines.append("missing paths:")
    if validation.missing_paths:
        lines.extend(f"- {path}" for path in validation.missing_paths)
    else:
        lines.append("- <none>")

    lines.append("")
    lines.append("required C wrapper symbols:")
    lines.extend(f"- {symbol}" for symbol in REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS)

    lines.append("")
    lines.append("missing symbols:")
    if validation.missing_symbols:
        lines.extend(f"- {symbol}" for symbol in validation.missing_symbols)
    else:
        lines.append("- <none>")

    lines.append("")
    lines.append("load errors:")
    if validation.load_errors:
        lines.extend(f"- {error}" for error in validation.load_errors)
    else:
        lines.append("- <none>")

    lines.append("")
    lines.append("source-alignment rule:")
    lines.append(
        "A configured backend must expose c_pcseti, c_pcsetr, c_pcsetc, "
        "c_plchhq, and c_pcgetr. Without these real NCAR/NCL routines, climara "
        "must stay guarded and must not use fixed-width, character-count, SVG, "
        "or browser text metrics."
    )

    return "\n".join(lines)


def configured_ncl_plotchar_library_status_report() -> str:
    validation = validate_configured_ncl_plotchar_library()
    env_lines = [
        f"{NCL_PLOTCHAR_LIBRARY_ENV}={os.environ.get(NCL_PLOTCHAR_LIBRARY_ENV, '<unset>')}",
        f"{NCL_PLOTCHAR_LIBRARY_DIRS_ENV}={os.environ.get(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, '<unset>')}",
        "",
    ]
    return "\n".join(env_lines) + ncl_plotchar_library_validation_report(validation)


def finite_nonnegative_metrics(metrics: object) -> bool:
    values = [
        float(getattr(metrics, "dl")),
        float(getattr(metrics, "dr")),
        float(getattr(metrics, "db")),
        float(getattr(metrics, "dt")),
    ]
    return all(math.isfinite(value) and value >= 0.0 for value in values)


__all__ = [
    "NCL_PLOTCHAR_CANDIDATE_LIBRARY_NAMES",
    "NCL_PLOTCHAR_LIBRARY_DIRS_ENV",
    "NCL_PLOTCHAR_LIBRARY_ENV",
    "NclPlotcharLibraryValidation",
    "REQUIRED_NCL_PLOTCHAR_C_WRAPPER_SYMBOLS",
    "build_validated_ncl_plotchar_ctypes_backend",
    "configured_ncl_plotchar_library_status_report",
    "explicit_ncl_plotchar_library_paths",
    "finite_nonnegative_metrics",
    "ncl_plotchar_library_validation_report",
    "split_path_list",
    "validate_configured_ncl_plotchar_library",
    "validate_ncl_plotchar_library_paths",
]
