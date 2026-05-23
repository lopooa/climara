"""EOF numerical functions.

NCL reference:
- ni/src/lib/nfp/eofW.c
- ni/src/lib/nfpfort/eof_scripps.f
- ni/src/lib/nfpfort/eof2data.f
"""

def eofunc(data, neval=1, dim="time", weights=None, **kwargs):
    """Compute EOF patterns."""
    raise NotImplementedError("eofunc is not implemented yet.")


def eofunc_ts(data, eof, dim="time", weights=None, **kwargs):
    """Project data onto EOF patterns to compute PC time series."""
    raise NotImplementedError("eofunc_ts is not implemented yet.")
