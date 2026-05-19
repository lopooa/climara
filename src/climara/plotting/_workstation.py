from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


@dataclass
class NclWorkstation:
    """
    NCL-style workstation.

    This is inspired by:

        wks = gsn_open_wks("png", "figure_name")
        draw(plot)
        frame(wks)

    In climara, the workstation controls output file naming,
    file type, dpi, and frame index.
    """
    wks_type: str = "png"
    name: str = "climara_plot"
    output_dir: str | Path = "."
    dpi: int = 300
    bbox_inches: str = "tight"
    frame_index: int = 0
    close_after_frame: bool = False

    def __post_init__(self):
        self.wks_type = str(self.wks_type).lower().lstrip(".")
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def suffix(self):
        if self.wks_type in ["pdf", "png", "jpg", "jpeg", "svg", "eps", "tif", "tiff"]:
            return self.wks_type

        return "png"

    def next_filename(self, filename=None):
        if filename is not None:
            path = Path(filename)

            if not path.is_absolute():
                path = self.output_dir / path

            return path

        if self.frame_index == 0:
            return self.output_dir / f"{self.name}.{self.suffix}"

        return self.output_dir / f"{self.name}_{self.frame_index + 1:03d}.{self.suffix}"

    def draw(self, fig=None):
        """
        Draw a Matplotlib figure, similar to NCL draw(plot).
        """
        if fig is None:
            fig = plt.gcf()

        fig.canvas.draw_idle()

        return fig

    def frame(self, fig=None, filename=None):
        """
        Save a figure, similar to NCL frame(wks).
        """
        if fig is None:
            fig = plt.gcf()

        path = self.next_filename(filename=filename)

        fig.savefig(
            path,
            dpi=self.dpi,
            bbox_inches=self.bbox_inches,
        )

        self.frame_index += 1

        if self.close_after_frame:
            plt.close(fig)

        return path

    def close(self, fig=None):
        if fig is None:
            fig = plt.gcf()

        plt.close(fig)


def gsn_open_wks(wks_type="png", name="climara_plot", output_dir=".", **kwargs):
    """
    Open an NCL-style workstation.

    Examples
    --------
    wks = gsn_open_wks("png", "my_figure")
    wks.frame(fig)
    """
    return NclWorkstation(
        wks_type=wks_type,
        name=name,
        output_dir=output_dir,
        **kwargs,
    )


def ncl_draw(obj=None):
    """
    Draw a figure or a plot-like object.

    If obj is a Matplotlib Figure, draw it.
    If obj has a draw() method, call it.
    """
    if obj is None:
        fig = plt.gcf()
        fig.canvas.draw_idle()
        return fig

    if hasattr(obj, "canvas"):
        obj.canvas.draw_idle()
        return obj

    if hasattr(obj, "draw"):
        return obj.draw()

    raise TypeError("ncl_draw expects a Matplotlib Figure or an object with draw().")


def ncl_frame(wks, fig=None, filename=None):
    """
    Save a frame using an NCL-style workstation.
    """
    if not isinstance(wks, NclWorkstation):
        raise TypeError("wks must be an NclWorkstation returned by gsn_open_wks().")

    return wks.frame(fig=fig, filename=filename)


def ncl_close(fig=None):
    if fig is None:
        fig = plt.gcf()

    plt.close(fig)


draw = ncl_draw
frame = ncl_frame
