"""Dimension weighted average functions.

NCL reference:
- ni/src/lib/nfp/dimavgwgtW.c
- ni/src/lib/nfpfort/dimavgwgt.f
- ni/src/lib/nfpfort/areaAve.f
"""

def dim_avg_wgt(data, weights, dim=None, **kwargs):
    """Compute weighted average along one or more dimensions."""
    raise NotImplementedError("dim_avg_wgt is not implemented yet.")


def coslat_weights(lat):
    """Return cosine-latitude weights."""
    raise NotImplementedError("coslat_weights is not implemented yet.")


def sqrt_coslat_weights(lat):
    """Return square-root cosine-latitude weights for EOF analysis."""
    raise NotImplementedError("sqrt_coslat_weights is not implemented yet.")
