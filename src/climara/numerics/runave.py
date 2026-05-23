"""
Running average functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/wrunaveW.c

Related Fortran routines:
- drunave
- dwgtrunave

Public NCL-style functions:
- runave
- runave_n
- wgt_runave
- wgt_runave_n
"""


def runave(data, n, opt=0, dim="time", **kwargs):
    """Compute a running average."""
    raise NotImplementedError("runave is not implemented yet.")


def runave_n(data, n, opt=0, dim="time", **kwargs):
    """Compute a running average along a selected dimension."""
    return runave(data, n=n, opt=opt, dim=dim, **kwargs)


def wgt_runave(data, weights, opt=0, dim="time", **kwargs):
    """Compute a weighted running average."""
    raise NotImplementedError("wgt_runave is not implemented yet.")


def wgt_runave_n(data, weights, opt=0, dim="time", **kwargs):
    """Compute a weighted running average along a selected dimension."""
    return wgt_runave(data, weights=weights, opt=opt, dim=dim, **kwargs)
