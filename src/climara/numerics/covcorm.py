"""
Covariance and correlation functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/covcormW.c

Related Fortran routines include:
- dcovcorm
- dcovcorm_xy
- patternCor

Public NCL-style functions:
- covcorm
- covcorm_xy
- escorc
- esccr
- pattern_cor
"""


def covcorm(x, y, dim="time", **kwargs):
    """Compute covariance and correlation along a dimension."""
    raise NotImplementedError("covcorm is not implemented yet.")


def covcorm_xy(x, y, dim="time", **kwargs):
    """Compute covariance and correlation for paired x/y fields."""
    raise NotImplementedError("covcorm_xy is not implemented yet.")


def escorc(x, y, dim="time", **kwargs):
    """Compute correlation between x and y along a dimension."""
    raise NotImplementedError("escorc is not implemented yet.")


def esccr(x, y, dim="time", **kwargs):
    """Compute cross-correlation between x and y."""
    raise NotImplementedError("esccr is not implemented yet.")


def pattern_cor(x, y, weights=None, **kwargs):
    """Compute pattern correlation."""
    raise NotImplementedError("pattern_cor is not implemented yet.")
