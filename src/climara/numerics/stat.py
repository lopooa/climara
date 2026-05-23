"""Statistical numerical functions.

NCL reference:
- ni/src/lib/nfp/statW.c
"""

def dim_standardize(data, dim="time", ddof=1, **kwargs):
    """Standardize data along a dimension."""
    raise NotImplementedError("dim_standardize is not implemented yet.")


def remove_monthly_climatology(data, dim="time", **kwargs):
    """Remove monthly climatology from a monthly time series."""
    raise NotImplementedError("remove_monthly_climatology is not implemented yet.")


def calc_monthly_anomaly(data, dim="time", **kwargs):
    """Calculate monthly anomalies."""
    return remove_monthly_climatology(data, dim=dim, **kwargs)
