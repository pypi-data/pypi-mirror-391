import numpy as np
import pandas as pd
import re

def contrast_matrix(contrast, model_matrix_names):
    """
    Construct contrast matrix for comparisons between treatments.

    Parameters
    ----------
    contrast : dict or list
        A dict of named contrasts (e.g. {"AvsB": "A-B"}) or a list of expressions (e.g. ["A-B", "A-(B+C+D)/3"]).
    model_matrix_names : list
        Column names of the model (design) matrix.

    Returns
    -------
    pandas.DataFrame
        Contrast matrix where rows correspond to model terms and columns to contrasts.

    Examples
    --------
    >>> model_vars = ["A", "B", "C", "D"]
    >>> contrast = {"AvsB": "A-B", "AvsC": "A-C", "AvsB.C.D": "A-(B+C+D)/3"}
    >>> contrast_matrix(contrast, model_vars)
    """
    if len(model_matrix_names) != len(set(model_matrix_names)):
        raise ValueError("model.matrix.names must be unique")

    # normalize input
    if isinstance(contrast, dict):
        contrast_names = list(contrast.keys())
        contrast_exprs = list(contrast.values())
    else:
        contrast_names = ["" for _ in contrast]
        contrast_exprs = contrast

    n_rows = len(model_matrix_names)
    n_cols = len(contrast_exprs)
    cm = np.zeros((n_rows, n_cols))
    rownames = model_matrix_names

    # Adjust column names
    colnames = [n if n else e for n, e in zip(contrast_names, contrast_exprs)]

    covars = model_matrix_names.copy()
    exprs = contrast_exprs.copy()

    # Handle special characters (parentheses)
    for i, covar in enumerate(covars):
        if "(" in covar or ")" in covar:
            xi = f"SVar{i+1}"
            vi = re.escape(covar)
            exprs = [re.sub(vi, xi, e) for e in exprs]
            covars[i] = xi

    # Replace colon (:) with 'cl'
    covars = [c.replace(":", "cl") for c in covars]
    exprs = [e.replace(":", "cl") for e in exprs]

    # Build identity mapping
    mdcovars = pd.DataFrame(np.eye(len(covars)), columns=covars)

    # Evaluate each contrast expression safely
    for j, e in enumerate(exprs):
        try:
            # Evaluate the string as a vectorized expression in the context of mdcovars
            cm[:, j] = mdcovars.eval(e).to_numpy()
        except Exception as err:
            raise ValueError(f"Error evaluating contrast '{e}': {err}")

    cm_df = pd.DataFrame(cm, index=rownames, columns=colnames)
    return cm_df
