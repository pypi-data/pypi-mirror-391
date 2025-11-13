import numpy as np
import pandas as pd
from scipy.stats import t as tdist

def lmmtest(fit, index=None, contrast=None, alternative="two.sided"):
    """
    Testing fixed effects and contrasts of fixed effects by t-statistic.

    Parameters
    ----------
    fit : dict
        Output from lmmfit or lmm. Must contain:
        - 'coef': 2D array (p covariates by m features)
        - 'cov': 3D array (p × p × m) or list of (p × p) matrices
        - 'df': scalar degrees of freedom

    index : list[int] or list[str], optional
        Which fixed effects to test. If None, all are tested.

    contrast : np.ndarray, optional
        Contrast matrix (p × c). If None, tests all coefficients.

    alternative : str
        One of {"two.sided", "less", "greater"}.

    Returns
    -------
    result : np.ndarray
        Combined matrix of coefficients, t-values, and p-values.
    """

    coef = fit["coef"]
    cov = fit["cov"]
    df = fit["df"]

    # record names if available
    if isinstance(coef, pd.DataFrame):
        Y_names = coef.columns
        X_names = coef.index
        coef = np.asarray(coef)
        p, m = coef.shape
    else:
        p, m = coef.shape
        Y_names = [f"Y{i+1}" for i in range(m)]
        X_names = [f"X{i+1}" for i in range(p)]

    if isinstance(contrast, pd.DataFrame):
        X_names = contrast.columns

    # --- Normalize shapes ---
    #coef = np.asarray(coef)
    #p, m = coef.shape
    # Convert cov to numpy array if list
    if isinstance(cov, list):
        cov = np.stack(cov, axis=2)
    cov = np.asarray(cov)

    # --- Determine contrast matrix ---
    if contrast is None:
        if index is None:
            index = np.arange(p)
        elif np.isscalar(index):
            index = [index]
        contrast = np.eye(p)[:, index]


    # Ensure contrast is 2D
    contrast = np.atleast_2d(contrast)

    # --- Compute effects ---
    eff = contrast.T @ coef  # (c × m)
    tval = np.zeros_like(eff)

    for j in range(m):
        cov_j = cov[:, :, j]
        se = np.sqrt(np.diag(contrast.T @ cov_j @ contrast))
        tval[:, j] = eff[:, j] / se

    # --- Compute p-values ---
    if alternative == "less":
        pval = tdist.cdf(tval, df)
    elif alternative == "greater":
        pval = tdist.sf(tval, df)
    else:  # two-sided
        pval = 2 * tdist.sf(np.abs(tval), df)

    # --- Combine results like in R: coef, t, p stacked ---
    eff = pd.DataFrame(eff.T, index=Y_names, columns=[f"{nm}_coef" for nm in X_names])    
    tval = pd.DataFrame(tval.T, index=Y_names, columns=[f"{nm}_t" for nm in X_names])
    pval = pd.DataFrame(pval.T, index=Y_names, columns=[f"{nm}_p" for nm in X_names])
    result = pd.concat([eff, tval, pval], axis=1)

    return result
