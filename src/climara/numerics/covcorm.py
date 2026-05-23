"""Covariance and correlation numerical functions.

NCL reference:
- ni/src/lib/nfp/covcormW.c
- ni/src/lib/nfpfort/covcorm_driver.f
- ni/src/lib/nfpfort/patternCor.f
"""

def escorc(x, y, dim="time", **kwargs):
    """Compute correlation along a dimension."""
    raise NotImplementedError("escorc is not implemented yet.")


def pattern_cor(x, y, weights=None, **kwargs):
    """Compute pattern correlation."""
    raise NotImplementedError("pattern_cor is not implemented yet.")


def pattern_cor_weighted(x, y, weights=None, **kwargs):
    """Compute weighted pattern correlation."""
    return pattern_cor(x, y, weights=weights, **kwargs)
