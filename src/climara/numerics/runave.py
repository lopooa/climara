"""Running average functions.

NCL reference:
- ni/src/lib/nfp/runaveW.c
- ni/src/lib/nfpfort/runave_dp.f
"""

def runave(data, n, dim="time", center=True, **kwargs):
    """Compute a running average."""
    raise NotImplementedError("runave is not implemented yet.")


def wrunave(data, weights, dim="time", center=True, **kwargs):
    """Compute a weighted running average."""
    raise NotImplementedError("wrunave is not implemented yet.")


def running_mean_3(data, dim="time", **kwargs):
    """Convenience wrapper for a centered 3-point running mean."""
    return runave(data, n=3, dim=dim, center=True, **kwargs)
