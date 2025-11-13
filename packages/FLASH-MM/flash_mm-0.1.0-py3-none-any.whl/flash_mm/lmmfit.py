# lmmfit.py
import numpy as np
from .lmm import lmm

def lmmfit(Y, X, Z, d=None, Y_names=None, X_names=None, theta0=None, nBlocks=None, method="REML",
           max_iter=50, epsilon=1e-5, output_cov=True, output_RE=False, verbose=False):
    """
    Fit Linear Mixed-Effects Models (LMM) by sample-level data.
    This function wraps `lmm()` to estimate LMM parameters 
    using either Restricted Maximum Likelihood (REML) or Maximum Likelihood (ML) with Fisher scoring gradient descent.

    Parameters
    ----------
    Y : np.ndarray
        A features-by-samples response matrix. Each row represents a feature (e.g. gene), and each column is a sample (e.g. cell).
    X : np.ndarray
        Design matrix for fixed effects. Rows correspond to columns of Y (the samples).
    Z : np.ndarray
        Z = [Z1, ..., Zk] is the design matrix for k random factors (components). Rows correspond to columns of Y (the samples).
    d : list[int] or int
        List of random effect sizes; if int, converted to [d]. d = (d1,...,dk), where di is the number of columns in the i-th random effects design matrix, Zi. Defaults to `Z.shape[1]` if not given.
    Y_names : list[str]
        A list of features representing the row names of Y. If None, default to ["Y1", ..., "Ym"].
    X_names : list[str]
        A list of covariates, the colunm names of X. If None, default to ["X1", ..., "Xp"].
    theta0 : np.ndarray, optional
        Initial variance components, (s1, ...,sk, s_(k+1)), where si = sigma_i^2, the variance component of the i-th random effect component. s_(k+1) = sigma^2, the variance component of the residual error.
    nBlocks : int, optional
        Number of blocks to split Y into for memory efficiency. Default is ceil((ncol(Y)*1e-8)*nrow(Y)).
    method : str
        "REML" or "ML".
    max_iter : int
        Maximum number of iterations.
    epsilon : float
        Convergence tolerance.  If the absolute value of the first partial derivative of log likelihood is less than epsilon, the iterative algorithms for LMM estimation converge.
    output_cov : bool
        Whether to output the covariance matrices for the estimated coefficients, used for testing contrasts.
    output_RE : bool
        Whether to output the best linear unbiased prediction (BLUP) of the random effects.
    verbose : bool
        Print non-convergence messages.

    Returns
    -------
    dict
        Dictionary containing: method, dlogL, logLik, niter, coef, se, t, p, cov, df, theta, se.theta, RE
        - method : The method for fitting LMM.
        - dlogL : pandas.DataFrame or numpy.ndarray
              First partial derivatives of log-likelihoods for each feature.
        - logLik : pandas.Series or numpy.ndarray
              Maximum log-likelihoods for the ML method, or maximum log-restricted-likelihoods for the REML method.
        - niter : pandas.Series or numpy.ndarray
              Number of iterations for each feature.
        - coef : pandas.DataFrame
              Estimated coefficients (fixed effects). Each column corresponds to a feature, and each row to a covariate.
        - se : pandas.DataFrame
              Standard errors of the estimated coefficients.
        - t : pandas.DataFrame
              t-values for the fixed effects, computed as `coef/se`.
        - df : pandas.Series or numpy.ndarray
              Degrees of freedom for the t-statistics.
        - p : pandas.DataFrame
              Two-sided p-values for the t-tests of the fixed effects.
        - cov : pandas.DataFrame or numpy.ndarray
              Covariance matrices of the estimated coefficients (fixed effects).
        - theta : pandas.DataFrame
              Estimated variance components. Each column corresponds to a feature, and each row to a variance component. The last row represents the variance component of residual error.
        - se_theta : pandas.DataFrame or numpy.ndarray
              Standard errors of the estimated variance components (`theta`).
        - RE : pandas.DataFrame
              Best linear unbiased predictions (BLUPs) of the random effects.

    Example
    -------
    >>> import numpy as np
    >>> import pandas as pd

    >>> # Generate data: X, Y, and Z    
    >>> n = int(1e3)
    >>> m = 10
    >>> np.random.seed(2024)
    >>> Y = np.random.normal(size=(m, n))
    >>> Y_names = [f"Gene{i+1}" for i in range(Y.shape[0])]

    >>> trt = np.random.choice(["A", "B"], size=n, replace=True)
    >>> X = pd.get_dummies(trt, drop_first=False).to_numpy()
    >>> X_names = [f"X{i+1}" for i in range(X.shape[1])]

    >>> q = 20
    >>> sam = np.empty(n, dtype=object)
    >>> mask_A = trt == "A"
    >>> mask_B = trt == "B"
    >>> sam[mask_A] = [f"A{i}" for i in np.random.randint(1, q//2 + 1, mask_A.sum())]
    >>> sam[mask_B] = [f"B{i}" for i in np.random.randint(1, q//2 + 1, mask_B.sum())]
    >>> Z = pd.get_dummies(sam, drop_first=False).to_numpy()
    >>> d = Z.shape[1]

    >>> method = "REML"
    >>> #method = "ML"

    >>> # Fit LMM using lmmfit function based on sample-level data.
    >>> fit = lmmfit(Y, X, Z, d=d, method = method)

    >>> # Fit LMM using lmm function based on summary-level data (summary statistics).
    >>> # Computing summary-level data
    >>> XX = X.T @ X
    >>> XY = (Y @ X).T
    >>> ZX = Z.T @ X
    >>> ZY = (Y @ Z).T
    >>> ZZ = Z.T @ Z
    >>> Ynorm = np.sum(Y * Y, axis=1)
    >>> n_obs = X.shape[0]

    >>> # Fitting LMM using lmm function
    >>> fitss = lmm(XX, XY, ZX, ZY, ZZ, Ynorm=Ynorm, n=n_obs, d=d)

    >>> # Inspect output
    >>> fit.keys()
    >>> fit['coef'].head()
    >>> fit['theta']                   
    """

    if np.any(np.isnan(Y)) or np.any(np.isnan(X)) or np.any(np.isnan(Z)):
        raise ValueError("Input matrices contain NaNs.")

    if Y.ndim == 1:
        Y = Y[np.newaxis, :]

    if Y.shape[1] != X.shape[0] or Y.shape[1] != Z.shape[0]:
        raise ValueError("Dimension mismatch between Y, X, and Z.")

    if d is None:
        d = [Z.shape[1]]

    p = X.shape[1]
    n = X.shape[0]
    m = Y.shape[0]

    if Y_names is None:
        Y_names = [f"Y{i+1}" for i in range(m)]
    else:
        if len(Y_names) != m:
            raise ValueError("Y_names length must match number of rows in Y.")
        
    if X_names is None:
        X_names = [f"X{i+1}" for i in range(p)]
    else:
        if len(X_names) != p:
            raise ValueError("X_names length must match number of columns in X.")

    if nBlocks is None:
        nBlocks = int(np.ceil((Y.shape[1] * 1e-8) * Y.shape[0]))
    nBlocks = min(nBlocks, Y.shape[0])
    size = int(round(Y.shape[0] / nBlocks))
    if nBlocks * size < Y.shape[0]:
        size += 1

    XY, ZY, Ynorm = [], [], []
    for i in range(nBlocks):
        j = slice(i * size, min(Y.shape[0], (i + 1) * size))
        XY.append((X.T @ Y[j, :].T))
        ZY.append((Z.T @ Y[j, :].T))
        Ynorm.append(np.sum(Y[j, :] * Y[j, :], axis=1))
    XY = np.hstack(XY)
    ZY = np.hstack(ZY)
    Ynorm = np.concatenate(Ynorm)

    XX = X.T @ X
    ZX = Z.T @ X
    ZZ = Z.T @ Z

    return lmm(XX, XY, ZX, ZY, ZZ, Ynorm=Ynorm, n=n, d=d, Y_names=Y_names, X_names=X_names,
               theta0=theta0, method=method, max_iter=max_iter,
               epsilon=epsilon, output_cov=output_cov,
               output_RE=output_RE, verbose=verbose)