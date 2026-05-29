from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from ._ncl_plotchar_textitem import NclPlotcharTextItemMeasurementCall
from ._plotchar_metrics import PlotcharExtentMetrics, build_plotchar_extent_metrics
from ._plotchar_metrics_provider import PlotcharMetricsProviderError


class NclPlotcharCtypesBackendError(PlotcharMetricsProviderError):
    pass


_C_PCSETI = "c_pcseti"
_C_PCSETR = "c_pcsetr"
_C_PCSETC = "c_pcsetc"
_C_PLCHHQ = "c_plchhq"
_C_PCGETR = "c_pcgetr"
_REQUIRED_SYMBOLS = (_C_PCSETI, _C_PCSETR, _C_PCSETC, _C_PLCHHQ, _C_PCGETR)


@dataclass(frozen=True)
class NclPlotcharCtypesLibrarySpec:
    paths: tuple[Path, ...]


@dataclass(frozen=True)
class NclPlotcharCRoutines:
    pcseti: Callable[[bytes, int], None]
    pcsetr: Callable[[bytes, float], None]
    pcsetc: Callable[[bytes, bytes], None]
    plchhq: Callable[[float, float, bytes, float, float, float], None]
    pcgetr: Callable[[bytes, Any], None]

    def metrics_for_call(
        self,
        call: NclPlotcharTextItemMeasurementCall,
    ) -> PlotcharExtentMetrics:
        func_code = _ascii_bytes(call.state.func_code, "Plotchar function code")
        chrs = _ascii_bytes(call.chrs, "Plotchar real_string")

        if b"\x00" in chrs:
            raise NclPlotcharCtypesBackendError(
                "NCL Plotchar C wrapper strings must not contain NUL bytes."
            )

        # TextItem.c::DoPcCalc state setup before FigureAndSetTextBBInfo.
        # Keep this order aligned to TextItem.c; do not collapse it into a
        # generic renderer heuristic.
        self.pcseti(b"TE", int(call.state.text_extent_flag))
        self.pcsetr(b"CS", float(call.state.constant_spacing))
        self.pcsetc(b"FC", func_code)
        self.pcsetr(b"PH", float(call.state.principle_height))
        self.pcsetr(b"PW", float(call.state.principle_width))
        self.pcseti(b"QU", int(call.state.quality_index))
        self.pcseti(b"FN", int(call.state.effective_font))

        if int(call.state.quality_index) < 3:
            self.pcseti(b"QU", int(call.state.quality_index))
        else:
            raise NclPlotcharCtypesBackendError(
                "Workstation-quality TextItem Plotchar state is still guarded; "
                "do not approximate PS/PDF/GKS-specific TextItem.c behavior."
            )

        # TextItem.c::FigureAndSetTextBBInfo measurement call.
        self.plchhq(
            float(call.xpos),
            float(call.ypos),
            chrs,
            float(call.size),
            float(call.angd),
            float(call.cntr),
        )

        # TextItem.c retrieval order is DL, DR, DT, DB.
        dl = self._pcgetr_float(b"DL")
        dr = self._pcgetr_float(b"DR")
        dt = self._pcgetr_float(b"DT")
        db = self._pcgetr_float(b"DB")

        return build_plotchar_extent_metrics(dl=dl, dr=dr, db=db, dt=dt)

    def _pcgetr_float(self, name: bytes) -> float:
        out = ctypes.c_float()
        self.pcgetr(name, ctypes.pointer(out))
        return float(out.value)


@dataclass(frozen=True)
class NclPlotcharCtypesBackend:
    routines: NclPlotcharCRoutines
    libraries: tuple[Any, ...] = ()
    library_paths: tuple[Path, ...] = ()

    @classmethod
    def from_library_paths(
        cls,
        library_paths: Sequence[str | os.PathLike[str]],
    ) -> "NclPlotcharCtypesBackend":
        paths = tuple(Path(path).expanduser() for path in library_paths)

        if not paths:
            raise NclPlotcharCtypesBackendError(
                "No NCAR/NCL Plotchar shared library paths were supplied. "
                "Set CLIMARA_NCL_PLOTCHAR_LIB to one or more shared libraries."
            )

        missing = [str(path) for path in paths if not path.exists()]
        if missing:
            raise NclPlotcharCtypesBackendError(
                "NCAR/NCL Plotchar shared library path does not exist: "
                + ", ".join(missing)
            )

        mode = getattr(ctypes, "RTLD_GLOBAL", 0)
        libraries = tuple(ctypes.CDLL(str(path), mode=mode) for path in paths)
        routines = routines_from_libraries(libraries)

        return cls(routines=routines, libraries=libraries, library_paths=paths)

    @classmethod
    def from_env(
        cls,
        env_name: str = "CLIMARA_NCL_PLOTCHAR_LIB",
    ) -> "NclPlotcharCtypesBackend":
        value = os.environ.get(env_name, "").strip()

        if not value:
            raise NclPlotcharCtypesBackendError(
                f"{env_name} is not set. climara will not guess or approximate "
                "Plotchar metrics; provide real NCAR/NCL shared library path(s)."
            )

        paths = tuple(part for part in value.split(os.pathsep) if part)
        return cls.from_library_paths(paths)

    def metrics_for_call(
        self,
        call: NclPlotcharTextItemMeasurementCall,
    ) -> PlotcharExtentMetrics:
        return self.routines.metrics_for_call(call)


def _ascii_bytes(value: Any, role: str) -> bytes:
    text = str(value)

    try:
        return text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise NclPlotcharCtypesBackendError(
            f"{role} must be ASCII before calling NCAR Plotchar C wrappers; "
            f"got {text!r}. This path must stay guarded until NCL string "
            "encoding behavior is explicitly mapped."
        ) from exc


def _configure_symbol(library: Any, symbol: str) -> Any:
    func = getattr(library, symbol)

    if symbol == _C_PCSETI:
        func.argtypes = [ctypes.c_char_p, ctypes.c_int]
        func.restype = None
    elif symbol == _C_PCSETR:
        func.argtypes = [ctypes.c_char_p, ctypes.c_float]
        func.restype = None
    elif symbol == _C_PCSETC:
        func.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        func.restype = None
    elif symbol == _C_PLCHHQ:
        func.argtypes = [
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_char_p,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
        ]
        func.restype = None
    elif symbol == _C_PCGETR:
        func.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float)]
        func.restype = None

    return func


def _find_configured_symbol(libraries: Iterable[Any], symbol: str) -> Any:
    for library in reversed(tuple(libraries)):
        try:
            return _configure_symbol(library, symbol)
        except AttributeError:
            continue

    raise NclPlotcharCtypesBackendError(
        f"Required NCAR/NCL Plotchar C wrapper symbol was not found: {symbol}. "
        "The shared library path must expose c_pcseti, c_pcsetr, c_pcsetc, "
        "c_plchhq, and c_pcgetr."
    )


def routines_from_libraries(libraries: Sequence[Any]) -> NclPlotcharCRoutines:
    if not libraries:
        raise NclPlotcharCtypesBackendError(
            "No shared libraries are loaded for NCAR/NCL Plotchar routines."
        )

    return NclPlotcharCRoutines(
        pcseti=_find_configured_symbol(libraries, _C_PCSETI),
        pcsetr=_find_configured_symbol(libraries, _C_PCSETR),
        pcsetc=_find_configured_symbol(libraries, _C_PCSETC),
        plchhq=_find_configured_symbol(libraries, _C_PLCHHQ),
        pcgetr=_find_configured_symbol(libraries, _C_PCGETR),
    )


def build_ncl_plotchar_ctypes_backend_from_env(
    env_name: str = "CLIMARA_NCL_PLOTCHAR_LIB",
) -> NclPlotcharCtypesBackend:
    return NclPlotcharCtypesBackend.from_env(env_name=env_name)


def build_ncl_plotchar_ctypes_backend(
    library_paths: Sequence[str | os.PathLike[str]],
) -> NclPlotcharCtypesBackend:
    return NclPlotcharCtypesBackend.from_library_paths(library_paths)


__all__ = [
    "NclPlotcharCRoutines",
    "NclPlotcharCtypesBackend",
    "NclPlotcharCtypesBackendError",
    "NclPlotcharCtypesLibrarySpec",
    "build_ncl_plotchar_ctypes_backend",
    "build_ncl_plotchar_ctypes_backend_from_env",
    "routines_from_libraries",
]
