from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HluTextItem:
    """NCL/HLU-style TextItem object.

    This mirrors the HLU TextItem resource idea used by NCL:

        txString
        txPosXF
        txPosYF
        txJust
        txFontHeightF
        txFontColor
        txAngleF

    coord_system:
        ndc       page normalized device coordinates
        viewport  local 0-1 coordinates inside a plot viewport
    """

    txString: str = ""
    txPosXF: float = 0.0
    txPosYF: float = 0.0
    txJust: str = "center_center"
    txFontHeightF: float = 10.0
    txFontColor: str = "black"
    txAngleF: float = 0.0
    coord_system: str = "ndc"
    name: str | None = None
    resources: dict = field(default_factory=dict)

    def copy(self):
        return HluTextItem(
            txString=self.txString,
            txPosXF=self.txPosXF,
            txPosYF=self.txPosYF,
            txJust=self.txJust,
            txFontHeightF=self.txFontHeightF,
            txFontColor=self.txFontColor,
            txAngleF=self.txAngleF,
            coord_system=self.coord_system,
            name=self.name,
            resources=dict(self.resources),
        )
