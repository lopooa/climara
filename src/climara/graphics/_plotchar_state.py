from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class PlotcharStateError(ValueError):
    pass


class PlotcharUnsupportedError(NotImplementedError):
    pass


_FONT_NAME_TO_NUMBER = {
    "PWRITX DATABASE": 0,
    "DEFAULT": 1,
    "CARTOGRAPHIC_ROMAN": 2,
    "CARTOGRAPHIC_GREEK": 3,
    "SIMPLEX_ROMAN": 4,
    "SIMPLEX_GREEK": 5,
    "SIMPLEX_SCRIPT": 6,
    "COMPLEX_ROMAN": 7,
    "COMPLEX_GREEK": 8,
    "COMPLEX_SCRIPT": 9,
    "COMPLEX_ITALIC": 10,
    "COMPLEX_CYRILLIC": 11,
    "DUPLEX_ROMAN": 12,
    "TRIPLEX_ROMAN": 13,
    "TRIPLEX_ITALIC": 14,
    "GOTHIC_GERMAN": 15,
    "GOTHIC_ENGLISH": 16,
    "GOTHIC_ITALIAN": 17,
    "MATH_SYMBOLS": 18,
    "SYMBOL_SET1": 19,
    "SYMBOL_SET2": 20,
    "HELVETICA": 21,
    "HELVETICA-BOLD": 22,
    "TIMES-ROMAN": 25,
    "TIMES-BOLD": 26,
    "COURIER": 29,
    "COURIER-BOLD": 30,
    "GREEK": 33,
    "MATH-SYMBOLS": 34,
    "TEXT-SYMBOLS": 35,
    "WEATHER1": 36,
    "WEATHER2": 37,
    "O_HELVETICA": 121,
    "O_HELVETICA-BOLD": 122,
    "O_TIMES-ROMAN": 125,
    "O_TIMES-BOLD": 126,
    "O_COURIER": 129,
    "O_COURIER-BOLD": 130,
    "O_GREEK": 133,
    "O_MATH-SYMBOLS": 134,
    "O_TEXT-SYMBOLS": 135,
    "O_WEATHER1": 136,
    "O_WEATHER2": 137,
}


def _param_key(whch: Any) -> str:
    text = str(whch).strip()
    if len(text) < 2:
        raise PlotcharStateError(f"Plotchar parameter name must have at least two characters: {whch!r}")
    return text[:2].upper()


def _clamp_int(value: Any, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def normalize_plotchar_font_number(value: Any) -> int:
    nodf = abs(int(value))
    if (
        (23 <= nodf <= 24)
        or (27 <= nodf <= 28)
        or (31 <= nodf <= 32)
        or (38 <= nodf <= 120)
        or (123 <= nodf <= 124)
        or (127 <= nodf <= 128)
        or (131 <= nodf <= 132)
        or nodf >= 138
    ):
        return 1
    return nodf


def normalize_plotchar_font_name(value: Any) -> int:
    name = str(value).strip().upper()
    if name not in _FONT_NAME_TO_NUMBER:
        raise PlotcharStateError(f"PCSETC('FN', ...) received an unsupported NCL Plotchar font name: {value!r}")
    return _FONT_NAME_TO_NUMBER[name]


@dataclass
class PlotcharState:
    adds: float = 0.0
    cons: float = 0.0
    dstb: float = 0.0
    dstl: float = 0.0
    dstr: float = 0.0
    dstt: float = 0.0
    hpic: tuple[float, float, float] = (21.0, 13.0, 9.0)
    ibnu: int = 3
    ibxc: tuple[int, int, int] = (-1, -1, -1)
    ibxf: int = 0
    icen: int = 0
    iord: int = 1
    iouc: int = 1
    iouf: int = 0
    ipcc: int = -1
    iquf: int = 0
    ishc: int = 0
    ishf: int = 0
    itef: int = 0
    jcod: int = 0
    lsci: tuple[int, ...] = field(default_factory=lambda: tuple([-1] * 16))
    nfcc: int = -1
    nodf: int = 0
    rbxl: float = 0.0
    rbxm: float = 0.15
    rbxx: float = -0.05
    rbxy: float = -0.05
    rolw: float = 0.0
    rplw: float = 0.0
    rslw: float = 0.0
    shdx: float = -0.05
    shdy: float = -0.05
    siza: float = 0.888888888888888
    ssic: float = 7.0
    sspr: float = 10.0
    subs: float = 0.0
    vpic: tuple[float, float, float] = (32.0, 20.0, 14.0)
    wpic: tuple[float, float, float] = (16.0, 12.0, 8.0)
    xbeg: float = 0.0
    xcen: float = 0.0
    xend: float = 0.0
    xmul: tuple[float, float, float] = (1.0, 1.0, 1.0)
    ybeg: float = 0.0
    ycen: float = 0.0
    yend: float = 0.0
    ymul: tuple[float, float, float] = (1.0, 1.0, 1.0)
    zinx: float = 1.0
    ziny: float = 1.0
    zinz: float = 1.0
    imap: int = 0
    oorv: float = 0.0
    rhtw: float = 1.75

    @classmethod
    def defaults(cls) -> "PlotcharState":
        return cls()

    def reset(self) -> "PlotcharState":
        fresh = type(self).defaults()
        self.__dict__.update(fresh.__dict__)
        return self

    def pcseti(self, whch: Any, ival: Any) -> "PlotcharState":
        key = _param_key(whch)
        value = int(ival)

        if key == "CE":
            self.icen = _clamp_int(value, 0, 1)
        elif key == "DO":
            self.iord = max(-2, min(2, value))
            if self.iord == 0:
                self.iord = 1
        elif key == "FN":
            self.nodf = normalize_plotchar_font_number(value)
        elif key == "MA":
            self.imap = max(0, value)
        elif key == "OC":
            self.iouc = value
        elif key == "OF":
            self.iouf = _clamp_int(value, 0, 1)
        elif key == "QU":
            self.iquf = _clamp_int(value, 0, 2)
        elif key == "SF":
            self.ishf = _clamp_int(value, 0, 1)
        elif key == "TE":
            self.itef = _clamp_int(value, 0, 1)
        elif key == "UN":
            self.ibnu = max(1, value)
        else:
            self.pcsetr(whch, float(value))
        return self

    def pcsetr(self, whch: Any, rval: Any) -> "PlotcharState":
        key = _param_key(whch)
        value = float(rval)

        if key == "AS":
            self.adds = value
        elif key == "BF":
            self.ibxf = int(value)
        elif key == "BL":
            self.rbxl = value
        elif key == "BM":
            self.rbxm = value
        elif key == "BX":
            self.rbxx = value
        elif key == "BY":
            self.rbxy = value
        elif key == "CD":
            self.jcod = _clamp_int(value, 0, 1)
        elif key == "CE":
            self.icen = _clamp_int(value, 0, 1)
        elif key == "CH":
            self.hpic = (self.hpic[0], self.hpic[1], max(0.0, value))
            self.ymul = (self.ymul[0], self.ymul[1], self.hpic[2] / 9.0)
        elif key == "CL":
            self.rplw = max(0.0, value)
        elif key == "CS":
            self.cons = value / 2.0
        elif key == "CV":
            self.vpic = (self.vpic[0], self.vpic[1], max(0.0, value))
        elif key == "CW":
            self.wpic = (self.wpic[0], self.wpic[1], max(0.0, value))
            self.xmul = (self.xmul[0], self.xmul[1], self.wpic[2] / 8.0)
        elif key == "DO":
            self.iord = max(-2, min(2, int(value)))
            if self.iord == 0:
                self.iord = 1
        elif key == "FN":
            self.nodf = normalize_plotchar_font_number(value)
        elif key == "HW":
            self.rhtw = value
        elif key == "IH":
            self.hpic = (self.hpic[0], max(0.0, value), self.hpic[2])
            self.ymul = (self.ymul[0], self.hpic[1] / 13.0, self.ymul[2])
        elif key == "IS":
            self.ssic = max(0.0, value)
        elif key == "IV":
            self.vpic = (self.vpic[0], max(0.0, value), self.vpic[2])
        elif key == "IW":
            self.wpic = (self.wpic[0], max(0.0, value), self.wpic[2])
            self.xmul = (self.xmul[0], self.wpic[1] / 12.0, self.xmul[2])
        elif key == "MA":
            self.imap = max(0, int(value))
        elif key == "OC":
            self.iouc = int(value)
        elif key == "OF":
            self.iouf = _clamp_int(value, 0, 1)
        elif key == "OL":
            self.rolw = max(0.0, value)
        elif key == "OR":
            self.oorv = value
        elif key == "PH":
            self.hpic = (max(0.0, value), self.hpic[1], self.hpic[2])
            self.ymul = (self.hpic[0] / 21.0, self.ymul[1], self.ymul[2])
        elif key == "PS":
            self.sspr = max(0.0, value)
        elif key == "PV":
            self.vpic = (max(0.0, value), self.vpic[1], self.vpic[2])
        elif key == "PW":
            self.wpic = (max(0.0, value), self.wpic[1], self.wpic[2])
            self.xmul = (self.wpic[0] / 16.0, self.xmul[1], self.xmul[2])
        elif key == "QU":
            self.iquf = _clamp_int(value, 0, 2)
        elif key == "SA":
            self.siza = max(0.0, value)
        elif key == "SC":
            self.ishc = int(value)
        elif key == "SF":
            self.ishf = _clamp_int(value, 0, 1)
        elif key == "SL":
            self.rslw = max(0.0, value)
        elif key == "SS":
            self.subs = value
        elif key == "SX":
            self.shdx = value
        elif key == "SY":
            self.shdy = value
        elif key == "TE":
            self.itef = _clamp_int(value, 0, 1)
        elif key == "UN":
            self.ibnu = max(1, int(value))
        elif key == "ZX":
            self.zinx = max(0.0, value)
        elif key == "ZY":
            self.ziny = max(0.0, value)
        elif key == "ZZ":
            self.zinz = max(0.0, value)
        else:
            raise PlotcharStateError(f"PCSETR parameter is not implemented in the Python Plotchar state model: {whch!r}")
        return self

    def pcsetc(self, whch: Any, cval: Any) -> "PlotcharState":
        key = _param_key(whch)
        text = str(cval)

        if key == "FC":
            if text == "":
                raise PlotcharStateError("PCSETC('FC', ...) requires a non-empty function-code character")
            self.nfcc = ord(text[0])
        elif key == "FN":
            self.nodf = normalize_plotchar_font_name(text)
        else:
            raise PlotcharStateError(f"PCSETC parameter is not implemented in the Python Plotchar state model: {whch!r}")
        return self

    def pcgetr(self, whch: Any) -> float:
        key = _param_key(whch)

        if key == "AS":
            return self.adds
        if key == "BF":
            return float(self.ibxf)
        if key == "BL":
            return self.rbxl
        if key == "BM":
            return self.rbxm
        if key == "BX":
            return self.rbxx
        if key == "BY":
            return self.rbxy
        if key == "CD":
            return float(self.jcod)
        if key == "CE":
            return float(self.icen)
        if key == "CH":
            return self.hpic[2]
        if key == "CL":
            return self.rplw
        if key == "CS":
            return 2.0 * self.cons
        if key == "CV":
            return self.vpic[2]
        if key == "CW":
            return self.wpic[2]
        if key == "DB":
            return self.dstb
        if key == "DL":
            return self.dstl
        if key == "DO":
            return float(self.iord)
        if key == "DR":
            return self.dstr
        if key == "DT":
            return self.dstt
        if key == "FN":
            return float(self.nodf)
        if key == "HW":
            return self.rhtw
        if key == "IH":
            return self.hpic[1]
        if key == "IS":
            return self.ssic
        if key == "IV":
            return self.vpic[1]
        if key == "IW":
            return self.wpic[1]
        if key == "MA":
            return float(self.imap)
        if key == "OC":
            return float(self.iouc)
        if key == "OF":
            return float(self.iouf)
        if key == "OL":
            return self.rolw
        if key == "OR":
            return self.oorv
        if key == "PH":
            return self.hpic[0]
        if key == "PS":
            return self.sspr
        if key == "PV":
            return self.vpic[0]
        if key == "PW":
            return self.wpic[0]
        if key == "QU":
            return float(self.iquf)
        if key == "SA":
            return self.siza
        if key == "SC":
            return float(self.ishc)
        if key == "SF":
            return float(self.ishf)
        if key == "SL":
            return self.rslw
        if key == "SS":
            return self.subs
        if key == "SX":
            return self.shdx
        if key == "SY":
            return self.shdy
        if key == "TE":
            return float(self.itef)
        if key == "UN":
            return float(self.ibnu)
        if key == "XB":
            return self.xbeg
        if key == "XC":
            return self.xcen
        if key == "XE":
            return self.xend
        if key == "YB":
            return self.ybeg
        if key == "YC":
            return self.ycen
        if key == "YE":
            return self.yend
        if key == "ZX":
            return self.zinx
        if key == "ZY":
            return self.ziny
        if key == "ZZ":
            return self.zinz
        raise PlotcharStateError(f"PCGETR parameter is not implemented in the Python Plotchar state model: {whch!r}")

    def apply_textitem_measurement_state(self, textitem_state: Any) -> "PlotcharState":
        self.pcseti("TE", int(textitem_state.text_extent_flag))
        self.pcsetr("CS", float(textitem_state.constant_spacing))
        self.pcsetc("FC", str(textitem_state.func_code))
        self.pcsetr("PH", float(textitem_state.principle_height))
        self.pcsetr("PW", float(textitem_state.principle_width))
        self.pcseti("QU", int(textitem_state.quality_index))
        self.pcseti("FN", int(textitem_state.effective_font))
        return self

    def _set_extent_vectors_from_plchhq(
        self,
        *,
        dl: float,
        dr: float,
        db: float,
        dt: float,
    ) -> "PlotcharState":
        self.dstl = float(dl)
        self.dstr = float(dr)
        self.dstb = float(db)
        self.dstt = float(dt)
        return self

    def plchhq(self, *args: Any, **kwargs: Any) -> None:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent computation is not implemented yet. "
            "Do not replace it with fixed-width, character-count, SVG, browser, "
            "or visual-estimation metrics. The next stage must map PLCHHQ source logic."
        )


def pcrset() -> PlotcharState:
    return PlotcharState.defaults()


def build_textitem_plotchar_state(textitem_state: Any) -> PlotcharState:
    return PlotcharState.defaults().apply_textitem_measurement_state(textitem_state)


__all__ = [
    "PlotcharState",
    "PlotcharStateError",
    "PlotcharUnsupportedError",
    "build_textitem_plotchar_state",
    "normalize_plotchar_font_name",
    "normalize_plotchar_font_number",
    "pcrset",
]
