import numpy as np

def sslmm(X, Y, Z, nBlocks=None):
    """
    Compute summary-level data (sufficient statistics) for LMM fitting.

    Parameters
    ----------
    X : np.ndarray
        Design matrix for fixed effects (samples × variables of fixed effects).
    Y : np.ndarray
        A features-by-samples response matrix. Each row represents a feature (e.g. gene), and each column is a sample (e.g. cell).
    Z : np.ndarray
        Z = [Z1, ..., Zk] is the design matrix for k random factors (components) (samples × variables of random effects).
    nBlocks : int, optional
        Number of blocks to split Y into for memory efficiency. Default is ceil((ncol(Y)*1e-8)*nrow(Y)).

    Returns
    -------
    dict
        {
            "n": int,
            "XX": np.ndarray,
            "XY": np.ndarray,
            "ZX": np.ndarray,
            "ZY": np.ndarray,
            "ZZ": np.ndarray,
            "Ynorm": np.ndarray
        }
    """
    # Validate inputs
    if np.isnan(X).any() or np.isnan(Y).any() or np.isnan(Z).any():
        raise ValueError("Input matrices X, Y, Z must not contain NA/NaN values.")
    if Y.shape[1] != X.shape[0] or Y.shape[1] != Z.shape[0]:
        raise ValueError("Y columns must match X and Z rows.")

    n_features = Y.shape[0]
    n_samples = X.shape[0]

    # Default nBlocks logic, matching R's: ceiling((ncol(Y)*1e-08)*nrow(Y))
    if nBlocks is None:
        nBlocks = int(np.ceil((Y.shape[1] * 1e-8) * Y.shape[0]))
    if nBlocks < 1:
        nBlocks = 1
    if nBlocks > n_features:
        print(f"Note: nBlocks={nBlocks} > nrow(Y), changed to nBlocks={n_features}.")
        nBlocks = n_features

    size = int(round(n_features / nBlocks))
    if nBlocks * size < n_features:
        size = int(round(n_features / nBlocks)) + 1

    XY_blocks = []
    ZY_blocks = []
    Ynorm_list = []

    for i in range(nBlocks):
        j_start = i * size
        j_end = min(n_features, (i + 1) * size)
        if j_start >= j_end:
            break

        Y_block = Y[j_start:j_end, :]
        XY_block = (Y_block @ X).T  # shape: (X.shape[1], block_size)
        ZY_block = (Y_block @ Z).T  # shape: (Z.shape[1], block_size)
        Ynorm_block = np.sum(Y_block * Y_block, axis=1)

        XY_blocks.append(XY_block)
        ZY_blocks.append(ZY_block)
        Ynorm_list.append(Ynorm_block)

    XY = np.concatenate(XY_blocks, axis=1)
    ZY = np.concatenate(ZY_blocks, axis=1)
    Ynorm = np.concatenate(Ynorm_list)

    return {
        "n": n_samples,
        "XX": X.T @ X,
        "XY": XY,
        "ZX": Z.T @ X,
        "ZY": ZY,
        "ZZ": Z.T @ Z,
        "Ynorm": Ynorm
    }
