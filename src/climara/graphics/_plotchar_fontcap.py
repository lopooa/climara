from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from ._plotchar_state import PlotcharStateError, PlotcharUnsupportedError


@dataclass(frozen=True)
class FontcapMetrics:
    character_start: int
    character_end: int
    font_cap: float
    font_base: float
    font_half: float
    font_right: float | None = None
    font_top: float | None = None
    font_bottom: float | None = None


@dataclass(frozen=True)
class FontcapGlyph:
    ascii_code: int
    char: str
    width: float
    llx: float
    lly: float
    urx: float
    ury: float
    points: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class PlotcharRdguGlyph:
    rdgu_left: float
    rdgu_right: float
    points: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class Fontcap:
    font_number: int
    path: Path
    metrics: FontcapMetrics
    glyphs: dict[int, FontcapGlyph]

    def glyph_for_ascii(self, ascii_code: int) -> FontcapGlyph:
        if ascii_code not in self.glyphs:
            raise PlotcharUnsupportedError(
                f"NCL fontcap {self.path.name} does not define ASCII {ascii_code}. "
                "This Python Plotchar stage only supports characters present in the parsed fontcap."
            )
        return self.glyphs[ascii_code]


_HEADER_KEYS = {
    "CHARACTER_START",
    "CHARACTER_END",
    "FONT_RIGHT",
    "FONT_TOP",
    "FONT_CAP",
    "FONT_HALF",
    "FONT_BASE",
    "FONT_BOTTOM",
}

_INTEGER_RE = re.compile(r"[-+]?\d+")


_FONT_NUMBER_ALIASES = {
    121: 21,
    122: 22,
    125: 25,
    126: 26,
    129: 29,
    130: 30,
    133: 33,
    134: 34,
    135: 35,
    136: 36,
    137: 37,
}


def normalize_fontcap_file_number(font_number: int) -> int:
    number = abs(int(font_number))
    return _FONT_NUMBER_ALIASES.get(number, number)


def fontcap_file_name(font_number: int) -> str:
    return f"font{normalize_fontcap_file_number(font_number)}.fc"


def candidate_fontcap_dirs() -> tuple[Path, ...]:
    dirs: list[Path] = []

    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        dirs.append(Path(explicit))

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if ncl_root:
        dirs.append(Path(ncl_root) / "common" / "src" / "fontcap")

    cwd = Path.cwd()
    dirs.extend(
        [
            cwd / "resources" / "plotchar" / "fontcap",
            cwd / "resources" / "fontcap",
            cwd.parent / "NCL" / "common" / "src" / "fontcap",
            cwd.parent / "ncl" / "common" / "src" / "fontcap",
        ]
    )

    out: list[Path] = []
    seen: set[str] = set()
    for path in dirs:
        key = str(path.expanduser())
        if key in seen:
            continue
        seen.add(key)
        out.append(Path(key))
    return tuple(out)


def resolve_fontcap_path(font_number: int, fontcap_dir: str | Path | None = None) -> Path:
    name = fontcap_file_name(font_number)

    if fontcap_dir is not None:
        path = Path(fontcap_dir).expanduser() / name
        if not path.exists():
            raise FileNotFoundError(f"NCL fontcap file not found: {path}")
        return path

    for directory in candidate_fontcap_dirs():
        path = directory.expanduser() / name
        if path.exists():
            return path

    searched = "\n".join(f"- {directory}" for directory in candidate_fontcap_dirs())
    raise FileNotFoundError(
        f"NCL fontcap file {name!r} was not found. Set CLIMARA_PLOTCHAR_FONTCAP_DIR "
        f"or NCL_SRC_ROOT. Searched:\n{searched}"
    )


def _is_comment(line: str) -> bool:
    return line.strip().startswith("/*")


def _parse_header(lines: list[str]) -> dict[str, float]:
    values: dict[str, float] = {}
    i = 0
    while i < len(lines):
        key = lines[i].strip()
        if key in _HEADER_KEYS:
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or _is_comment(lines[j])):
                j += 1
            if j < len(lines):
                numbers = _INTEGER_RE.findall(lines[j])
                if numbers:
                    values[key] = float(numbers[0])
                    i = j
        i += 1
    return values


def _parse_char_header(line: str) -> tuple[int, float, float, float, float, float] | None:
    # Comment format in NCAR fontcap source:
    # /*     A        65        128     2     0   125   140
    numbers = _INTEGER_RE.findall(line)
    if len(numbers) < 6:
        return None
    ascii_code, width, llx, lly, urx, ury = [float(value) for value in numbers[-6:]]
    return int(ascii_code), width, llx, lly, urx, ury


def _parse_coordinate_pairs(line: str) -> tuple[tuple[float, float], ...]:
    text = line.strip()
    if not text or _is_comment(text):
        return ()
    upper = text.upper()
    if upper.startswith("BEGIN_") or upper.startswith("END_"):
        return ()
    numbers = [float(value) for value in _INTEGER_RE.findall(text)]
    if len(numbers) < 2 or len(numbers) % 2:
        return ()
    return tuple((numbers[i], numbers[i + 1]) for i in range(0, len(numbers), 2))


def parse_fontcap(path: str | Path, *, font_number: int | None = None) -> Fontcap:
    path = Path(path)
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    header = _parse_header(lines)

    missing = [key for key in ("CHARACTER_START", "CHARACTER_END", "FONT_CAP", "FONT_BASE", "FONT_HALF") if key not in header]
    if missing:
        raise PlotcharStateError(f"fontcap {path} is missing required source metrics: {missing}")

    metrics = FontcapMetrics(
        character_start=int(header["CHARACTER_START"]),
        character_end=int(header["CHARACTER_END"]),
        font_cap=header["FONT_CAP"],
        font_base=header["FONT_BASE"],
        font_half=header["FONT_HALF"],
        font_right=header.get("FONT_RIGHT"),
        font_top=header.get("FONT_TOP"),
        font_bottom=header.get("FONT_BOTTOM"),
    )

    glyphs: dict[int, FontcapGlyph] = {}
    i = 0
    while i < len(lines):
        if lines[i].strip().upper() != "BEGIN_CHAR":
            i += 1
            continue

        ascii_code: int | None = None
        width = llx = lly = urx = ury = None
        points: list[tuple[float, float]] = []
        i += 1

        while i < len(lines) and lines[i].strip().upper() != "END_CHAR":
            line = lines[i]
            if _is_comment(line):
                parsed = _parse_char_header(line)
                if parsed is not None:
                    ascii_code, width, llx, lly, urx, ury = parsed
            else:
                points.extend(_parse_coordinate_pairs(line))
            i += 1

        if ascii_code is not None and width is not None and llx is not None and lly is not None and urx is not None and ury is not None:
            glyphs[ascii_code] = FontcapGlyph(
                ascii_code=ascii_code,
                char=chr(ascii_code),
                width=width,
                llx=llx,
                lly=lly,
                urx=urx,
                ury=ury,
                points=tuple(points),
            )
        i += 1

    if not glyphs:
        raise PlotcharStateError(f"fontcap {path} did not yield any glyph definitions")

    if font_number is None:
        match = re.search(r"font(\d+)\.fc$", path.name)
        font_number = int(match.group(1)) if match else -1

    return Fontcap(font_number=int(font_number), path=path, metrics=metrics, glyphs=glyphs)


@lru_cache(maxsize=64)
def load_fontcap(font_number: int, fontcap_dir: str | Path | None = None) -> Fontcap:
    path = resolve_fontcap_path(font_number, fontcap_dir)
    return parse_fontcap(path, font_number=font_number)


def glyph_to_rdgu(glyph: FontcapGlyph, metrics: FontcapMetrics, *, chgt: float) -> PlotcharRdguGlyph:
    # Mirrors PCFFGD.f lines 60-74 for source fontcap coordinates:
    # XOFF=-0.5*CWIDTH, YOFF=FBASE-FHALF, SCALE=CHGT/(FCAP-FBASE)
    denom = float(metrics.font_cap) - float(metrics.font_base)
    if denom == 0.0:
        raise PlotcharStateError("fontcap has FONT_CAP == FONT_BASE; cannot reproduce PCFFGD SCALE")

    scale = float(chgt) / denom
    xoff = -0.5 * float(glyph.width)
    yoff = float(metrics.font_base) - float(metrics.font_half)
    points = tuple(((x + xoff) * scale, (y + yoff) * scale) for x, y in glyph.points)

    return PlotcharRdguGlyph(
        rdgu_left=xoff * scale,
        rdgu_right=-xoff * scale,
        points=points,
    )


def glyphs_to_rdgu(glyphs: Iterable[FontcapGlyph], metrics: FontcapMetrics, *, chgt: float) -> tuple[PlotcharRdguGlyph, ...]:
    return tuple(glyph_to_rdgu(glyph, metrics, chgt=chgt) for glyph in glyphs)


__all__ = [
    "Fontcap",
    "FontcapGlyph",
    "FontcapMetrics",
    "PlotcharRdguGlyph",
    "candidate_fontcap_dirs",
    "fontcap_file_name",
    "glyph_to_rdgu",
    "glyphs_to_rdgu",
    "load_fontcap",
    "normalize_fontcap_file_number",
    "parse_fontcap",
    "resolve_fontcap_path",
]
