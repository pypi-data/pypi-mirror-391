# lmm.py
import numpy as np
import pandas as pd
from numpy.linalg import inv, LinAlgError
from scipy.stats import t as t_dist
from numpy.linalg import qr
from numpy.linalg import slogdet
from numpy.linalg import pinv

def varest(ZZres, zrz, zryj, yryj, n, d, s, pres, max_iter=50, epsilon=1e-5):
    """
    Internal function to estimate variance components for one feature (gene).
    """
    k = len(d)
    sr = s[:k] / s[k]
    M = inv(np.diag(np.repeat(1.0, sum(d))) + (zrz * np.repeat(sr, d)[:, None]))

    if pres > 0:
        M0 = M
    else:
        M0inv = (ZZres * np.repeat(sr, d)[:, None]) + np.eye(sum(d))
        try:
            M0 = inv(M0inv)
        except LinAlgError:
            M0 = pinv(M0inv)

    dl = np.full(k + 1, 100.0)
    iter_count = 0

    while np.max(np.abs(dl)) > epsilon and iter_count < max_iter:
        iter_count += 1
        fs = np.zeros((k + 1, k + 1))
        dl = np.zeros(k + 1)

        yRZ = zryj.T @ M
        ZVZ = ZZres @ M0
        ZV2Z = ZVZ @ M0

        mi = 0
        for i in range(k):
            ik = slice(mi, mi + d[i])
            dl[i] = (np.sum(yRZ[ik] ** 2) / s[k] ** 2 -
                     np.trace(ZVZ[ik, ik]) / s[k]) / 2.0
            mj = 0
            for j in range(i + 1):
                ji = slice(mj, mj + d[j])
                fs[i, j] = np.sum(ZVZ[ji, ik] ** 2) / s[k] ** 2 / 2.0
                fs[j, i] = fs[i, j]
                mj += d[j]
            j = k
            fs[i, j] = np.trace(ZV2Z[ik, ik]) / s[k] ** 2 / 2.0
            fs[j, i] = fs[i, j]
            mi += d[i]

        fs[k, k] = (n - pres - sum(d) + np.sum(M0 * M0)) / s[k] ** 2 / 2.0
        yR2y = yryj - np.sum(((M.T + np.eye(sum(d))) @ zryj) * (M @ (np.repeat(sr, d) * zryj)))
        dl[k] = (yR2y / s[k] ** 2 - (n - pres - sum(d) + np.trace(M0)) / s[k]) / 2.0

        Minv = pinv(fs)
        s = s + Minv @ dl
        sr = s[:k] / s[k]
        M = inv((zrz * np.repeat(sr, d)[:, None]) + np.eye(sum(d)))
        if pres > 0:
            M0 = M
        else:
            M0inv = (ZZres * np.repeat(sr, d)[:, None]) + np.eye(sum(d))
            try:
                M0 = inv(M0inv)
            except LinAlgError:
                M0 = pinv(M0inv)

    qrM0 = qr(M0)
    logdetM0 = np.sum(np.log(np.abs(np.diag(qrM0[1]))))
    return dict(s=s, dl=dl, iter=iter_count, Minv=Minv, logdetM0=logdetM0)


def lmm(XX, XY, ZX, ZY, ZZ, Ynorm, n, d, Y_names=None, X_names=None,
        theta0=None, method="REML", max_iter=50, epsilon=1e-5,
        output_cov=True, output_RE=False, verbose=False):
    """
    Fit linear mixed-effects models (LMM) from summary-level data 
    using either Restricted Maximum Likelihood (REML) or Maximum Likelihood (ML) with Fisher scoring gradient descent.

    Parameters
    ----------
    XX : np.ndarray (p, p)
        t(X)X, where X is the n-by-p fixed-effects design matrix.
    XY : np.ndarray (p, m)
        t(YX), where Y is a m-by-n (features-by-samples) matrix.
    ZX : np.ndarray (q, p)
        t(Z)X, where Z = [Z1, ..., Zk] is the n-by-q design matrix for k random factors (variables or random components).
    ZY : np.ndarray (q, m)
        t(YZ).
    ZZ : np.ndarray (q, q)
        t(Z)Z.
    Ynorm : np.ndarray
        rowSums(Y*Y), squared norms for features.
    n : int
        Number of samples.
    d : list[int] or int
        List of random effect sizes; if int, converted to [d]. d = (d1,...,dk), where di is the number of columns in the i-th random effects design matrix, Zi.
    Y_names : list[str]
        A list of features representing the row names of Y. If None, default to ["Y1", ..., "Ym"].
    X_names : list[str]
        A list of covariates, the colunm names of X. If None, default to ["X1", ..., "Xp"].
    theta0 : np.ndarray, optional
        Initial variance components, (s1, ...,sk, s_(k+1)), where si = sigma_i^2, the variance component of the i-th random effect component. s_(k+1) = sigma^2, the variance component of the residual error.
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

    >>> # Fit LMM using summary-level data
    >>> # Computing summary-level data
    >>> XX = X.T @ X
    >>> XY = (Y @ X).T
    >>> ZX = Z.T @ X
    >>> ZY = (Y @ Z).T
    >>> ZZ = Z.T @ Z
    >>> Ynorm = np.sum(Y * Y, axis=1)
    >>> n_obs = X.shape[0]

    >>> # Fitting LMM using lmm function
    >>> fit = lmm(XX, XY, ZX, ZY, ZZ, Ynorm=Ynorm, n=n_obs, d=d)

    >>> # Inspect output
    >>> fit.keys()
    >>> fit['coef'].head()
    >>> fit['theta']              
    """

    if np.any(np.isnan(XY)) or np.any(np.isnan(ZX)) or np.any(np.isnan(ZY)):
        raise ValueError("Input contains NaNs.")

    if np.sum(d) != ZZ.shape[1]:
        raise ValueError("Sum(d) must equal ncol(ZZ).")

    p = ZX.shape[1]
    m = XY.shape[1]

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

    # Ensure d is iterable
    if isinstance(d, (int, np.integer)):
        d = [d]
    k = len(d)
    theta_names = [f"var{i+1}" for i in range(k)] + ["var0"]

    try:
        XXinv = inv(XX)
    except LinAlgError:
        raise ValueError("XX is not positive-definite or X is not full column rank.")

    xxz = XXinv @ ZX.T
    zrz = ZZ - ZX @ (XXinv @ ZX.T)
    zry = ZY - ZX @ (XXinv @ XY)
    yry = Ynorm - np.sum(XY * (XXinv @ XY), axis=0)

    pres = p if method == "REML" else 0
    ZZres = zrz if method == "REML" else ZZ

    niter, dlogL, loglike = [], [], []
    theta, setheta = [], []
    RE, beta, sebeta = [], [], []
    covbeta = []

    for jy in range(m):
        s = np.concatenate([np.zeros(k), [yry[jy] / (n - p)]]) if theta0 is None else theta0
        vest = varest(ZZres, zrz, zry[:, jy], yry[jy], n, d, s, pres,
                      max_iter=max_iter, epsilon=epsilon)
        s, dl, iter_, Minv, logdet = (
            vest["s"], vest["dl"], vest["iter"], vest["Minv"], vest["logdetM0"]
        )

        sr = s[:k] / s[k]
        DZZ1 = ZZ * np.repeat(sr, d)[:, None] + np.eye(sum(d))
        try:
            M = inv(DZZ1)
        except LinAlgError:
            M = pinv(DZZ1)
        M = M * np.repeat(sr, d)[None, :]

        xvx = pinv(XX - ZX.T @ M @ ZX)
        xvy = XY[:, jy] - ZX.T @ (M @ ZY[:, jy])
        b = xvx @ xvy
        covb = (xvx + xvx.T) * (s[k] / 2)
        REj = M @ (ZY[:, jy] - ZX @ b)

        niter.append(iter_)
        theta.append(s)
        setheta.append(np.sqrt(np.diag(Minv)))
        beta.append(b)
        dlogL.append(dl)
        loglike.append(-(n - pres) * (1 + np.log(2 * np.pi * s[k])) / 2 + logdet / 2)
        sebeta.append(np.sqrt(np.diag(covb)))
        covbeta.append(covb)
        RE.append(REj)

    beta = np.column_stack(beta)
    sebeta = np.column_stack(sebeta)
    tval = beta / sebeta
    pval = 2 * t_dist.sf(np.abs(tval), df=n - p) * 2
    covbeta = np.stack(covbeta, axis=2)

    theta = np.column_stack(theta)
    setheta = np.column_stack(setheta)
    RE = np.column_stack(RE)

    dlogL = np.column_stack(dlogL)
    nonconverge = np.where(np.sum(np.abs(dlogL) > epsilon, axis=0) > 0)[0]
    if verbose:
        print(f"{len(nonconverge)} features did not converge (abs(dlogL) > {epsilon})")

    # wrap results as DataFrames
    beta = pd.DataFrame(beta, index=X_names, columns=Y_names)
    sebeta = pd.DataFrame(sebeta, index=X_names, columns=Y_names)
    tval = pd.DataFrame(tval, index=X_names, columns=Y_names)
    pval = pd.DataFrame(pval, index=X_names, columns=Y_names)
    theta = pd.DataFrame(theta, index=theta_names, columns=Y_names)
    setheta = pd.DataFrame(setheta, index=theta_names, columns=Y_names)
    dlogL = pd.DataFrame(dlogL, index=theta_names, columns=Y_names)
    loglike = pd.Series(loglike, index=Y_names)
    niter = pd.Series(niter, index=Y_names)
    RE = pd.DataFrame(RE, index=[f"z{i+1}" for i in range(sum(d))], columns=Y_names)

    if not output_cov:
        covbeta = None
    if not output_RE:
        RE = None

    return {
        "method": method,
        "dlogL": dlogL,
        "logLik": loglike,
        "niter": niter,
        "coef": beta,
        "se": sebeta,
        "t": tval,
        "p": pval,
        "cov": covbeta,
        "df": n-p,
        "theta": theta,
        "se_theta": setheta,
        "RE": RE
        }