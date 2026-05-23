"""
Weighted dimension average functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/dimavgwgtW.c

Related Fortran routines include:
- dimavgwgt
- dimsumwgt
- areaAve

Public NCL-style functions:
- dim_avg_wgt
- dim_avg_wgt_n
- dim_sum_wgt
- dim_sum_wgt_n
"""


def dim_avg_wgt(data, weights, dim=None, opt=0, **kwargs):
    """Compute weighted average along one or more dimensions."""
    raise NotImplementedError("dim_avg_wgt is not implemented yet.")


def dim_avg_wgt_n(data, weights, dim=None, opt=0, **kwargs):
    """Compute weighted average along selected dimensions."""
    return dim_avg_wgt(data, weights=weights, dim=dim, opt=opt, **kwargs)


def dim_sum_wgt(data, weights, dim=None, opt=0, **kwargs):
    """Compute weighted sum along one or more dimensions."""
    raise NotImplementedError("dim_sum_wgt is not implemented yet.")


def dim_sum_wgt_n(data, weights, dim=None, opt=0, **kwargs):
    """Compute weighted sum along selected dimensions."""
    return dim_sum_wgt(data, weights=weights, dim=dim, opt=opt, **kwargs)


def coslat_weights(lat):
    """Return cosine-latitude weights."""
    raise NotImplementedError("coslat_weights is not implemented yet.")


def sqrt_coslat_weights(lat):
    """Return square-root cosine-latitude weights for EOF analysis."""
    raise NotImplementedError("sqrt_coslat_weights is not implemented yet.")
