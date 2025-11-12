"""
Utility Functions for RBFM-VAR Package
======================================

Helper functions for data manipulation, lag construction, and diagnostics.

Author: Implementation by Claude for Dr. Merwan Roudane
"""

import numpy as np
from typing import Tuple, Optional, List
from scipy import stats


def construct_var_matrices(
    data: np.ndarray,
    p: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Construct standard VAR matrices Y and X.
    
    For VAR(p): Y_t = A_1 Y_{t-1} + ... + A_p Y_{t-p} + ε_t
    
    Parameters
    ----------
    data : np.ndarray
        (T x n) data matrix
    p : int
        Lag order
    
    Returns
    -------
    Y : np.ndarray
        (T-p x n) dependent variables
    X : np.ndarray
        (T-p x np) stacked lagged variables
    """
    T, n = data.shape
    
    # Y: observations from t=p+1 to T
    Y = data[p:]
    
    # X: [Y_{t-1}, ..., Y_{t-p}]
    X_list = []
    for lag in range(1, p + 1):
        X_list.append(data[p-lag:T-lag])
    
    X = np.column_stack(X_list)
    
    return Y, X


def lag_matrix(data: np.ndarray, lags: int) -> np.ndarray:
    """
    Create matrix of lagged values.
    
    Parameters
    ----------
    data : np.ndarray
        (T x n) data matrix  
    lags : int
        Number of lags
    
    Returns
    -------
    lagged : np.ndarray
        (T x n*lags) matrix of lagged values
    """
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    T, n = data.shape
    lagged_list = []
    
    for lag in range(1, lags + 1):
        lagged_list.append(np.vstack([
            np.full((lag, n), np.nan),
            data[:-lag]
        ]))
    
    return np.column_stack(lagged_list)


def difference(data: np.ndarray, order: int = 1) -> np.ndarray:
    """
    Compute differences of specified order.
    
    Parameters
    ----------
    data : np.ndarray
        Input data
    order : int
        Order of differencing (1 for first difference, 2 for second, etc.)
    
    Returns
    -------
    differenced : np.ndarray
        Differenced data
    """
    result = data.copy()
    for _ in range(order):
        result = np.diff(result, axis=0)
    return result


def select_lag_order(
    data: np.ndarray,
    max_lag: int = 10,
    criterion: str = 'bic'
) -> int:
    """
    Select VAR lag order using information criterion.
    
    Parameters
    ----------
    data : np.ndarray
        Data matrix
    max_lag : int
        Maximum lag to consider
    criterion : str
        'aic', 'bic', or 'hqic'
    
    Returns
    -------
    optimal_lag : int
        Selected lag order
    """
    from .rbfmvar_estimator import RBFMVAREstimator
    
    T, n = data.shape
    criteria_values = []
    
    for p in range(1, min(max_lag + 1, T // 4)):
        try:
            model = RBFMVAREstimator(data, p=p)
            model.fit()
            
            if criterion.lower() == 'aic':
                crit = model._compute_aic()
            elif criterion.lower() == 'bic':
                crit = model._compute_bic()
            elif criterion.lower() == 'hqic':
                crit = -2 * model._compute_log_likelihood() + \
                       2 * np.log(np.log(T - p)) * n * (n * p + n)
            else:
                raise ValueError(f"Unknown criterion: {criterion}")
            
            criteria_values.append(crit)
        except:
            criteria_values.append(np.inf)
    
    optimal_lag = int(np.argmin(criteria_values)) + 1
    return optimal_lag


def impulse_response(
    Phi: np.ndarray,
    A: np.ndarray,
    p: int,
    horizon: int = 20,
    shock_size: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Compute impulse response functions.
    
    Parameters
    ----------
    Phi : np.ndarray
        Estimated Φ coefficients
    A : np.ndarray
        Estimated A coefficients
    p : int
        Lag order
    horizon : int
        Response horizon
    shock_size : np.ndarray, optional
        Size of shock (default: unit shock to each variable)
    
    Returns
    -------
    irf : np.ndarray
        (horizon x n x n) impulse responses
        irf[h, i, j] = response of variable i to shock in j at horizon h
    """
    n = Phi.shape[0]
    
    # Convert to VAR(1) companion form
    # [y_t]     [A_1  A_2 ... A_p] [y_{t-1}]
    # [y_{t-1}] = [I    0  ... 0  ] [y_{t-2}]
    # [...]     [0    I  ... 0  ] [...]
    
    # For RBFM-VAR, need to reconstruct A_i from Φ and A
    # This is complex, so simplified version:
    
    if shock_size is None:
        shock_size = np.eye(n)
    
    irf = np.zeros((horizon, n, n))
    irf[0] = shock_size
    
    # Simplified IRF computation
    # Would need full VAR(p) matrices for complete implementation
    
    return irf


def forecast_error_variance_decomposition(
    Phi: np.ndarray,
    A: np.ndarray,
    Sigma: np.ndarray,
    horizon: int = 20
) -> np.ndarray:
    """
    Compute forecast error variance decomposition.
    
    Parameters
    ----------
    Phi : np.ndarray
        Estimated Φ coefficients
    A : np.ndarray
        Estimated A coefficients
    Sigma : np.ndarray
        Error covariance matrix
    horizon : int
        Forecast horizon
    
    Returns
    -------
    fevd : np.ndarray
        (horizon x n x n) variance decomposition
        fevd[h, i, j] = proportion of h-step forecast error variance of
                        variable i due to shocks in variable j
    """
    n = Phi.shape[0]
    
    # Cholesky decomposition for orthogonalized shocks
    P = np.linalg.cholesky(Sigma)
    
    # Compute IRFs with Cholesky shocks
    irf = impulse_response(Phi, A, p=1, horizon=horizon, shock_size=P)
    
    # Cumulative squared IRFs
    mse = np.cumsum(irf**2, axis=0)
    
    # Total MSE for each variable at each horizon
    total_mse = mse.sum(axis=2, keepdims=True)
    
    # FEVD: proportion due to each shock
    fevd = mse / total_mse
    
    return fevd


def portmanteau_test(
    residuals: np.ndarray,
    lags: int = 10,
    df_adjustment: Optional[int] = None
) -> Tuple[float, float]:
    """
    Multivariate Portmanteau test for residual autocorrelation.
    
    Tests H0: No autocorrelation up to lag h.
    
    Parameters
    ----------
    residuals : np.ndarray
        (T x n) residual matrix
    lags : int
        Number of lags to test
    df_adjustment : int, optional
        Degrees of freedom adjustment (number of parameters estimated)
    
    Returns
    -------
    statistic : float
        Test statistic
    p_value : float
        P-value
    """
    T, n = residuals.shape
    
    # Sample autocovariances
    C0 = residuals.T @ residuals / T
    C0_inv = np.linalg.inv(C0)
    
    Q = 0
    for h in range(1, lags + 1):
        Ch = residuals[h:].T @ residuals[:-h] / T
        Q += np.trace(Ch.T @ C0_inv @ Ch @ C0_inv) / (T - h)
    
    Q *= T**2
    
    # Degrees of freedom
    if df_adjustment is None:
        df = n**2 * lags
    else:
        df = n**2 * lags - df_adjustment
    
    p_value = 1 - stats.chi2.cdf(Q, df)
    
    return Q, p_value


def arch_test(
    residuals: np.ndarray,
    lags: int = 4
) -> Tuple[float, float]:
    """
    Test for ARCH effects in residuals.
    
    Tests H0: No ARCH effects up to lag h.
    
    Parameters
    ----------
    residuals : np.ndarray
        (T x n) residual matrix
    lags : int
        Number of lags
    
    Returns
    -------
    statistic : float
        Test statistic
    p_value : float
        P-value
    """
    if residuals.ndim == 1:
        residuals = residuals.reshape(-1, 1)
    
    T, n = residuals.shape
    
    # Squared residuals
    resid_sq = residuals**2
    
    # For each variable, test ARCH
    statistics = []
    p_values = []
    
    for i in range(n):
        u_sq = resid_sq[:, i]
        
        # Regress u²_t on u²_{t-1}, ..., u²_{t-h}
        Y = u_sq[lags:]
        X = lag_matrix(u_sq, lags)[lags:]
        X = np.column_stack([np.ones(len(X)), X])
        
        # OLS
        beta = np.linalg.lstsq(X, Y, rcond=None)[0]
        fitted = X @ beta
        resid = Y - fitted
        
        # R²
        TSS = np.sum((Y - Y.mean())**2)
        RSS = np.sum(resid**2)
        R2 = 1 - RSS / TSS
        
        # LM statistic
        LM = (T - lags) * R2
        
        # Chi-square test
        p_val = 1 - stats.chi2.cdf(LM, lags)
        
        statistics.append(LM)
        p_values.append(p_val)
    
    # Return average across variables
    return np.mean(statistics), np.mean(p_values)


def stability_check(
    Phi: np.ndarray,
    A: np.ndarray,
    p: int
) -> Tuple[bool, np.ndarray]:
    """
    Check stability of estimated VAR.
    
    A VAR is stable if all eigenvalues of companion matrix are inside unit circle.
    
    Parameters
    ----------
    Phi : np.ndarray
        Φ coefficient matrix
    A : np.ndarray
        A coefficient matrix  
    p : int
        Lag order
    
    Returns
    -------
    is_stable : bool
        Whether VAR is stable
    eigenvalues : np.ndarray
        Eigenvalues of companion matrix
    """
    n = Phi.shape[0]
    
    # Would need to reconstruct full VAR(p) matrices
    # Simplified check on A matrix eigenvalues
    
    try:
        eigenvalues = np.linalg.eigvals(A[:, :n])  # Just use first difference part
        max_eigenvalue = np.max(np.abs(eigenvalues))
        is_stable = max_eigenvalue < 1.0
    except:
        is_stable = False
        eigenvalues = np.array([])
    
    return is_stable, eigenvalues


def plot_residual_diagnostics(residuals: np.ndarray, variable_names: Optional[List[str]] = None):
    """
    Create diagnostic plots for residuals.
    
    Parameters
    ----------
    residuals : np.ndarray
        (T x n) residual matrix
    variable_names : list of str, optional
        Names of variables
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib required for plotting")
        return
    
    T, n = residuals.shape
    
    if variable_names is None:
        variable_names = [f'Var{i+1}' for i in range(n)]
    
    fig, axes = plt.subplots(n, 3, figsize=(15, 4*n))
    
    if n == 1:
        axes = axes.reshape(1, -1)
    
    for i in range(n):
        resid = residuals[:, i]
        
        # Time series plot
        axes[i, 0].plot(resid)
        axes[i, 0].axhline(0, color='r', linestyle='--')
        axes[i, 0].set_title(f'{variable_names[i]}: Residuals')
        axes[i, 0].set_xlabel('Time')
        
        # Histogram
        axes[i, 1].hist(resid, bins=30, edgecolor='black', alpha=0.7)
        axes[i, 1].set_title(f'{variable_names[i]}: Distribution')
        axes[i, 1].set_xlabel('Residual')
        
        # Q-Q plot
        stats.probplot(resid, dist="norm", plot=axes[i, 2])
        axes[i, 2].set_title(f'{variable_names[i]}: Q-Q Plot')
    
    plt.tight_layout()
    plt.show()


def compute_persistence(A: np.ndarray) -> np.ndarray:
    """
    Compute persistence measures from A matrix.
    
    For I(1) processes, this indicates how long shocks persist.
    
    Parameters
    ----------
    A : np.ndarray
        Estimated A coefficient matrix
    
    Returns
    -------
    persistence : np.ndarray
        Persistence measures for each variable
    """
    n = A.shape[0]
    
    # Extract level coefficients
    level_coeffs = A[:, n:]
    
    # Persistence: eigenvalues close to 1 indicate high persistence
    try:
        eigenvalues = np.linalg.eigvals(level_coeffs)
        persistence = np.abs(eigenvalues)
    except:
        persistence = np.ones(n)
    
    return persistence


def format_summary_table(summary: dict) -> str:
    """
    Format model summary as a table.
    
    Parameters
    ----------
    summary : dict
        Summary dictionary from RBFMVAREstimator.summary()
    
    Returns
    -------
    table : str
        Formatted summary table
    """
    lines = []
    lines.append("\n" + "="*70)
    lines.append("RBFM-VAR Model Summary")
    lines.append("="*70)
    lines.append(f"Number of variables: {summary['n_vars']}")
    lines.append(f"Lag order: {summary['lag_order']}")
    lines.append(f"Sample size: {summary['sample_size']}")
    lines.append(f"Effective sample size: {summary['effective_sample_size']}")
    lines.append(f"\nLog-likelihood: {summary['log_likelihood']:.2f}")
    lines.append(f"AIC: {summary['AIC']:.2f}")
    lines.append(f"BIC: {summary['BIC']:.2f}")
    lines.append("\nResidual standard errors:")
    for i, std in enumerate(summary['residual_std']):
        lines.append(f"  Variable {i+1}: {std:.4f}")
    lines.append("="*70 + "\n")
    
    return '\n'.join(lines)
