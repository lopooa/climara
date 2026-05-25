import numpy as np

from climara.graphics._coords import add_cyclic
from climara.graphics._cyclic import add_cyclic_point_1d
from climara.graphics._utils import maybe_add_cyclic


def main():
    arr = np.array([[1.0, 2.0, 3.0]])
    lon = np.array([0.0, 10.0, 20.0])

    out, out_lon = add_cyclic_point_1d(arr, lon, axis=-1)

    assert out.shape == (1, 4)
    assert np.allclose(out, [[1.0, 2.0, 3.0, 1.0]])
    assert np.allclose(out_lon, [0.0, 10.0, 20.0, 30.0])

    out, out_lon, _ = add_cyclic(arr, lon=lon, lat=None, axis=-1)

    assert out.shape == (1, 4)
    assert np.allclose(out_lon, [0.0, 10.0, 20.0, 30.0])

    out, out_lon = maybe_add_cyclic(arr, lon, add_cyclic=True)

    assert out.shape == (1, 4)
    assert np.allclose(out_lon, [0.0, 10.0, 20.0, 30.0])

    global_lon = np.array([0.0, 90.0, 180.0, 270.0])
    global_arr = np.array([[1.0, 2.0, 3.0, 4.0]])

    out, out_lon, _ = add_cyclic(global_arr, lon=global_lon, lat=None, axis=-1)

    assert out.shape == global_arr.shape
    assert np.allclose(out_lon, global_lon)

    print("✅ local cyclic helper smoke passed")


if __name__ == "__main__":
    main()
