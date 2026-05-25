from __future__ import annotations

import numpy as np


def add_cyclic_point_1d(data, coord, axis=-1):
    arr = np.asarray(data)
    coord = np.asarray(coord)

    if coord.ndim != 1:
        raise ValueError("Expected 1D coordinate for cyclic point")

    if coord.size == 0:
        return arr, coord

    axis = axis % arr.ndim

    if arr.shape[axis] != coord.size:
        raise ValueError(
            f"Coordinate length {coord.size} does not match data axis {axis} "
            f"length {arr.shape[axis]}"
        )

    if coord.size == 1:
        step = 360.0
    else:
        step = float(np.nanmedian(np.diff(coord)))

    first = np.take(arr, [0], axis=axis)
    cyclic_arr = np.concatenate([arr, first], axis=axis)
    cyclic_coord = np.concatenate([coord, np.asarray([coord[-1] + step], dtype=coord.dtype)])

    return cyclic_arr, cyclic_coord
