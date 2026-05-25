from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HluView:
    """NCL/HLU-style viewport resources.

    This mirrors the HLU View resources used by NCL:

        vpXF
        vpYF
        vpWidthF
        vpHeightF

    vpXF and vpYF are the upper-left corner in NDC.
    This object is backend independent.
    """

    vpXF: float = 0.0
    vpYF: float = 1.0
    vpWidthF: float = 1.0
    vpHeightF: float = 1.0

    @property
    def left(self):
        return self.vpXF

    @property
    def right(self):
        return self.vpXF + self.vpWidthF

    @property
    def top(self):
        return self.vpYF

    @property
    def bottom(self):
        return self.vpYF - self.vpHeightF

    def as_mpl_rect(self):
        """Return [left, bottom, width, height] for backend-neutral viewport mapping."""
        return [self.left, self.bottom, self.vpWidthF, self.vpHeightF]

    def copy(self):
        return HluView(
            vpXF=self.vpXF,
            vpYF=self.vpYF,
            vpWidthF=self.vpWidthF,
            vpHeightF=self.vpHeightF,
        )


@dataclass
class HluBoundingBox:
    """NCL/HLU-style bounding box.

    NCL's NhlGetBB returns top, bottom, left and right values.
    """

    top: float
    bottom: float
    left: float
    right: float

    @classmethod
    def from_view(cls, view: HluView):
        return cls(
            top=view.top,
            bottom=view.bottom,
            left=view.left,
            right=view.right,
        )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom
