from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_state import PlotcharUnsupportedError


# NCL PLCHHQ legacy digitization offsets.
# IFRO/IFGR select Roman or Greek digitization blocks.
IFRO = 0
IFGR = 384

# ISZP/ISZI/ISZC select principal, indexical, or cartographic size.
ISZP = 0
ISZI = 128
ISZC = 256

# ICSU/ICSL select upper or lower case.
ICSU = 0
ICSL = 64

# Standard character heights used by the legacy digitization branch.
SPIC = (21.0, 13.0, 9.0)


# DPC order reconstructed from PLCHHQ CDPC/IASC table.
# NCL fills IDPC only if the ASCII code has not already been assigned,
# so duplicate space keeps the first entry.
_DPC_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "+-*/()$= ,."
    "abcdefghijklmnopqrstuvwxyz"
    "!\"#%&:;<>?@[\\]{|}~'^_` "
)


def build_ascii_to_dpc_index() -> dict[int, int]:
    out: dict[int, int] = {}

    for index, char in enumerate(_DPC_CHARS, start=1):
        code = ord(char)
        if code not in out:
            out[code] = index

    return out


ASCII_TO_DPC_INDEX = build_ascii_to_dpc_index()


@dataclass(frozen=True)
class LegacyDigitizationKey:
    font_family: str
    size_level: str
    case_mode: str
    char: str

    @property
    def font_offset(self) -> int:
        if self.font_family == "roman":
            return IFRO
        if self.font_family == "greek":
            return IFGR

        raise PlotcharUnsupportedError(
            f"Unsupported legacy Plotchar font family: {self.font_family!r}"
        )

    @property
    def size_offset(self) -> int:
        if self.size_level == "principal":
            return ISZP
        if self.size_level == "indexical":
            return ISZI
        if self.size_level == "cartographic":
            return ISZC

        raise PlotcharUnsupportedError(
            f"Unsupported legacy Plotchar size level: {self.size_level!r}"
        )

    @property
    def case_offset(self) -> int:
        if self.case_mode == "upper":
            return ICSU
        if self.case_mode == "lower":
            return ICSL

        raise PlotcharUnsupportedError(
            f"Unsupported legacy Plotchar case mode: {self.case_mode!r}"
        )

    @property
    def dpc_index(self) -> int:
        if len(self.char) != 1:
            raise PlotcharUnsupportedError(
                f"Legacy Plotchar digitization key requires a single character, got {self.char!r}"
            )

        code = ord(self.char)
        if code not in ASCII_TO_DPC_INDEX:
            raise PlotcharUnsupportedError(
                f"Character {self.char!r} is not mapped in the NCL PLCHHQ DPC table."
            )

        return ASCII_TO_DPC_INDEX[code]

    @property
    def inda_index(self) -> int:
        return (
            self.font_offset
            + self.size_offset
            + self.case_offset
            + self.dpc_index
        )


def legacy_digitization_index(
    char: str,
    *,
    font_family: str = "roman",
    size_level: str = "principal",
    case_mode: str = "upper",
) -> int:
    key = LegacyDigitizationKey(
        font_family=font_family,
        size_level=size_level,
        case_mode=case_mode,
        char=char,
    )
    return key.inda_index


__all__ = [
    "ASCII_TO_DPC_INDEX",
    "IFRO",
    "IFGR",
    "ISZP",
    "ISZI",
    "ISZC",
    "ICSU",
    "ICSL",
    "SPIC",
    "LegacyDigitizationKey",
    "legacy_digitization_index",
]
