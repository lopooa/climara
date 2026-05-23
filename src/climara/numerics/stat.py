"""
Statistical numerical functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/statW.c

Related Fortran routines include:
- dstat2
- dstat4
- drmvmean
- dxstnd

Public NCL-style functions:
- dim_rmvmean
- dim_rmvmean_n
- dim_standardize
- dim_standardize_n
- dim_rmsd
- dim_rmsd_n
- dim_stat4
- dim_stat4_n
"""


def dim_rmvmean(data, dim="time", **kwargs):
    """Remove the mean along a dimension."""
    raise NotImplementedError("dim_rmvmean is not implemented yet.")


def dim_rmvmean_n(data, dim="time", **kwargs):
    """Remove the mean along a selected dimension."""
    return dim_rmvmean(data, dim=dim, **kwargs)


def dim_standardize(data, dim="time", ddof=1, **kwargs):
    """Standardize data along a dimension."""
    raise NotImplementedError("dim_standardize is not implemented yet.")


def dim_standardize_n(data, dim="time", ddof=1, **kwargs):
    """Standardize data along a selected dimension."""
    return dim_standardize(data, dim=dim, ddof=ddof, **kwargs)


def dim_rmsd(x, y, dim="time", **kwargs):
    """Compute RMS difference along a dimension."""
    raise NotImplementedError("dim_rmsd is not implemented yet.")


def dim_rmsd_n(x, y, dim="time", **kwargs):
    """Compute RMS difference along a selected dimension."""
    return dim_rmsd(x, y, dim=dim, **kwargs)


def dim_stat4(data, dim="time", **kwargs):
    """Compute four basic statistics along a dimension."""
    raise NotImplementedError("dim_stat4 is not implemented yet.")


def dim_stat4_n(data, dim="time", **kwargs):
    """Compute four basic statistics along a selected dimension."""
    return dim_stat4(data, dim=dim, **kwargs)
