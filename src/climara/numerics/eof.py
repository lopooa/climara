"""
EOF numerical functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/eofW.c

Related Fortran routines include:
- ddrveof
- xrveoft
- deof11

Public NCL-style functions:
- eofunc
- eofunc_n
- eofunc_ts
- eofunc_ts_n
- eofcov
- eofcor
- eof2data
"""


def eofunc(data, neval=1, opt=None, dim="time", weights=None, **kwargs):
    """Compute EOF patterns."""
    raise NotImplementedError("eofunc is not implemented yet.")


def eofunc_n(data, neval=1, opt=None, dim="time", weights=None, **kwargs):
    """Compute EOF patterns along a selected dimension."""
    return eofunc(data, neval=neval, opt=opt, dim=dim, weights=weights, **kwargs)


def eofunc_ts(data, eof, opt=None, dim="time", weights=None, **kwargs):
    """Compute principal component time series from EOF patterns."""
    raise NotImplementedError("eofunc_ts is not implemented yet.")


def eofunc_ts_n(data, eof, opt=None, dim="time", weights=None, **kwargs):
    """Compute principal component time series along a selected dimension."""
    return eofunc_ts(data, eof, opt=opt, dim=dim, weights=weights, **kwargs)


def eofcov(data, neval=1, opt=None, dim="time", weights=None, **kwargs):
    """Compute covariance EOFs."""
    raise NotImplementedError("eofcov is not implemented yet.")


def eofcor(data, neval=1, opt=None, dim="time", weights=None, **kwargs):
    """Compute correlation EOFs."""
    raise NotImplementedError("eofcor is not implemented yet.")


def eof2data(eof, pc, **kwargs):
    """Reconstruct data from EOF patterns and principal components."""
    raise NotImplementedError("eof2data is not implemented yet.")
