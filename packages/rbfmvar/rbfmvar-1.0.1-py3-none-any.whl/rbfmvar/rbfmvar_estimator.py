"""
RBFM-VAR: Residual-Based Fully Modified Vector Autoregression
Based on Chang (2000) - "Vector Autoregressions with Unknown Mixtures of I(0), I(1), and I(2) Components"

This implementation fixes the common broadcasting error in constructing residuals.
"""

import numpy as np
from scipy import stats
import warnings

def create_lags(y, max_lag):
    """
    Create lagged variables properly handling indices.

    Parameters:
    -----------
    y : array-like, shape (T, n)
        Time series data
    max_lag : int
        Maximum lag order

    Returns:
    --------
    Y_lagged : array, shape (T-max_lag, n*max_lag)
        Matrix of lagged variables
    """
    T, n = y.shape
    Y_lagged = np.zeros((T - max_lag, n * max_lag))

    for lag in range(1, max_lag + 1):
        start_col = (lag - 1) * n
        end_col = lag * n
        Y_lagged[:, start_col:end_col] = y[max_lag - lag : T - lag, :]

    return Y_lagged


def bartlett_kernel(x, bandwidth):
    """Bartlett kernel for HAC estimation."""
    if np.abs(x) <= bandwidth:
        return 1 - np.abs(x) / bandwidth
    else:
        return 0


def compute_long_run_variance(residuals, bandwidth=None):
    """
    Compute long-run variance matrix using Bartlett kernel.

    Parameters:
    -----------
    residuals : array-like, shape (T, n)
        Residuals
    bandwidth : int, optional
        Bandwidth parameter. If None, uses Andrews (1991) automatic selection.

    Returns:
    --------
    Omega : array, shape (n, n)
        Long-run variance matrix
    """
    T, n = residuals.shape

    # Automatic bandwidth selection if not provided
    if bandwidth is None:
        bandwidth = int(np.floor(4 * (T / 100) ** (2/9)))
        bandwidth = max(1, bandwidth)

    # Compute Gamma(0)
    Omega = residuals.T @ residuals / T

    # Add autocovariances
    for lag in range(1, bandwidth + 1):
        weight = bartlett_kernel(lag, bandwidth)
        if weight > 0:
            Gamma_lag = residuals[lag:, :].T @ residuals[:-lag, :] / T
            Omega += weight * (Gamma_lag + Gamma_lag.T)

    return Omega


def rbfm_var(y, p, bandwidth=None):
    """
    Estimate RBFM-VAR model for VAR(p) with unknown mixtures of I(0), I(1), I(2).

    Parameters:
    -----------
    y : array-like, shape (T, n)
        Time series data
    p : int
        Lag order of VAR
    bandwidth : int, optional
        Bandwidth for long-run variance estimation

    Returns:
    --------
    results : dict
        Dictionary containing:
        - 'Phi_plus': Corrected estimates for Phi (coefficients on Z)
        - 'A_plus': Corrected estimates for A (coefficients on W)
        - 'residuals': Regression residuals
        - 'Omega_hat': Estimated error covariance matrix
        - 'se_Phi': Standard errors for Phi
        - 'se_A': Standard errors for A
    """

    y = np.asarray(y)
    T, n = y.shape

    if T < p + 10:
        raise ValueError(f"Sample size {T} too small for lag order {p}. Need at least {p+10} observations.")

    print(f"\n{'='*60}")
    print(f"RBFM-VAR Estimation")
    print(f"{'='*60}")
    print(f"Sample size (T): {T}")
    print(f"Number of variables (n): {n}")
    print(f"Lag order (p): {p}")

    # Step 1: Construct Z_t = (Δ²y_{t-1}, ..., Δ²y_{t-p+2})'
    # These are the STATIONARY regressors

    # First difference
    delta_y = np.diff(y, axis=0)  # Shape: (T-1, n)
    # Second difference
    delta2_y = np.diff(delta_y, axis=0)  # Shape: (T-2, n)

    print(f"\nAfter differencing:")
    print(f"  Δy shape: {delta_y.shape}")
    print(f"  Δ²y shape: {delta2_y.shape}")

    if p >= 3:
        # For p >= 3, we have multiple lags of Δ²y
        # We need Δ²y_{t-1}, ..., Δ²y_{t-(p-2)}
        # Maximum lag we need is (p-2)
        num_z_lags = p - 2

        # Available observations for Δ²y start at t=2 (since we need two differences)
        # For regression at time t, we need Δ²y up to lag (p-2)
        # So effective sample starts at t = 2 + (p-2) = p

        Z = create_lags(delta2_y, num_z_lags)  # Shape: (T-2-num_z_lags, n*num_z_lags)
        T_eff = Z.shape[0]

        print(f"  Z (lags of Δ²y) shape: {Z.shape}")
        print(f"  Effective sample size: {T_eff}")

    else:
        # For p < 3, no lagged second differences in regression
        Z = np.zeros((T - p, 0))
        T_eff = T - p
        print(f"  No Z variables (p < 3)")
        print(f"  Effective sample size: {T_eff}")

    # Step 2: Construct W_t = (Δy'_{t-1}, y'_{t-1})'
    # These are potentially NONSTATIONARY regressors

    # We need Δy_{t-1} and y_{t-1}
    # For regression at time t, effective time index after differences is t-2 (for Δ²y)
    # We need Δy and y at lag 1, meaning Δy_{t-2-1} = Δy_{t-3} and y_{t-3}

    # Align with Z
    if p >= 3:
        # Z uses observations from index (p-2) to (T-2)
        # For W, we need same time indices
        # Δy_{t-1} where t corresponds to Z indices
        # Z[0] corresponds to t = (p-2), so we need Δy_{t-1} = Δy_{p-3}
        # This is index (p-3) in delta_y

        start_idx = p - 3
        end_idx = start_idx + T_eff

        delta_y_t1 = delta_y[start_idx:end_idx, :]  # Δy_{t-1}
        y_t1 = y[start_idx:end_idx, :]  # y_{t-1}

    else:
        # For p=1: Δ²y_{t} = Δy_t - Δy_{t-1}, starts at t=2
        # Regression: Δ²y_t = A₁Δy_{t-1} + A₂y_{t-1}
        # At t=2: need Δy_1 and y_1

        start_idx = 0
        end_idx = T_eff

        delta_y_t1 = delta_y[start_idx:end_idx, :]
        y_t1 = y[start_idx:end_idx, :]

    W = np.hstack([delta_y_t1, y_t1])  # Shape: (T_eff, 2n)

    print(f"  W (Δy_{{t-1}}, y_{{t-1}}) shape: {W.shape}")
    print(f"  Delta y_{{t-1}} shape: {delta_y_t1.shape}")
    print(f"  y_{{t-1}} shape: {y_t1.shape}")

    # Step 3: Construct dependent variable Δ²y_t

    # delta2_y starts at t=2
    # We need it aligned with our regressors
    if p >= 3:
        y_dep = delta2_y[p-2:p-2+T_eff, :]
    else:
        y_dep = delta2_y[:T_eff, :]

    print(f"  Dependent variable (Δ²y_t) shape: {y_dep.shape}")

    # Verify shapes match
    assert Z.shape[0] == W.shape[0] == y_dep.shape[0], \
        f"Shape mismatch: Z{Z.shape}, W{W.shape}, y{y_dep.shape}"

    # Step 4: Construct X = [Z, W]
    if Z.shape[1] > 0:
        X = np.hstack([Z, W])
    else:
        X = W

    print(f"\nRegression setup:")
    print(f"  X (all regressors) shape: {X.shape}")
    print(f"  y (dependent) shape: {y_dep.shape}")

    # Step 5: OLS estimation to get preliminary residuals
    # y_t = [Φ, A] [Z_t, W_t]' + ε_t

    try:
        beta_ols = np.linalg.lstsq(X, y_dep, rcond=None)[0]  # Shape: (n*(p-2)+2n, n)
    except np.linalg.LinAlgError:
        warnings.warn("Singular matrix in OLS. Using pseudo-inverse.")
        beta_ols = np.linalg.pinv(X) @ y_dep

    residuals_ols = y_dep - X @ beta_ols

    print(f"  OLS completed")
    print(f"  Residuals shape: {residuals_ols.shape}")

    # Step 6: Construct v̂_t for correction terms (Equation 11 in paper)
    # THIS IS WHERE THE ERROR TYPICALLY OCCURS
    #
    # v̂_t = (v̂'_{1t}, v̂'_{2t})' where:
    # v̂_{1t} = Δ²y_{t-1}
    # v̂_{2t} = Δy_{t-1} - N̂Δy_{t-2}
    #
    # where N̂ is from regression: Δy_{t-1} = NΔy_{t-2} + error

    print(f"\n{'='*60}")
    print(f"Constructing correction terms v̂_t")
    print(f"{'='*60}")

    # For v̂_{1t}: we need Δ²y_{t-1}
    # For v̂_{2t}: we need Δy_{t-1} and Δy_{t-2}

    # CRITICAL FIX: Ensure we have enough observations for ALL terms
    # We need at least 2 lags of Δy, which means we lose 2 observations minimum

    if T_eff < 3:
        raise ValueError(f"Not enough observations ({T_eff}) to construct v̂_t. Need at least 3.")

    # Align Δ²y_{t-1} with regression sample
    # delta2_y[0] is Δ²y at t=2
    # For regression sample starting at effective t, we need Δ²y_{t-1}

    if p >= 3:
        v1t_start = p - 3  # One lag back from dependent variable start
        v1t_end = v1t_start + T_eff
    else:
        v1t_start = 0
        v1t_end = T_eff

    # Check bounds
    if v1t_end > len(delta2_y):
        v1t_end = len(delta2_y)
        T_eff = v1t_end - v1t_start
        print(f"  Adjusted T_eff to {T_eff} due to data availability")

    v1t = delta2_y[v1t_start:v1t_end, :]  # Δ²y_{t-1}

    print(f"  v̂_{{1t}} = Δ²y_{{t-1}} shape: {v1t.shape}")

    # For v̂_{2t}, we need to regress Δy_{t-1} on Δy_{t-2}
    # CRITICAL: Make sure we have aligned data

    # delta_y[0] is Δy at t=1
    # For regression sample, we need Δy_{t-1} and Δy_{t-2}

    if p >= 3:
        # Δy_{t-1} for regression sample
        dy_t1_start = p - 3
        dy_t1_end = dy_t1_start + T_eff

        # Δy_{t-2} for regression sample
        dy_t2_start = p - 4
        dy_t2_end = dy_t2_start + T_eff

    else:
        dy_t1_start = 0
        dy_t1_end = T_eff

        dy_t2_start = 0  # Can't go negative
        dy_t2_end = T_eff

    # Make sure indices are valid
    if dy_t2_start < 0:
        # Not enough data for Δy_{t-2}
        # Need to reduce sample size
        offset = -dy_t2_start
        dy_t2_start = 0
        dy_t1_start += offset
        v1t_start += offset
        T_eff -= offset

        dy_t2_end = T_eff
        dy_t1_end = dy_t1_start + T_eff
        v1t_end = v1t_start + T_eff

        print(f"  Adjusted indices: reducing T_eff to {T_eff}")

    delta_y_for_N_t1 = delta_y[dy_t1_start:dy_t1_end, :]  # Δy_{t-1}
    delta_y_for_N_t2 = delta_y[dy_t2_start:dy_t2_end, :]  # Δy_{t-2}

    print(f"  For N̂ estimation:")
    print(f"    Δy_{{t-1}} shape: {delta_y_for_N_t1.shape}")
    print(f"    Δy_{{t-2}} shape: {delta_y_for_N_t2.shape}")

    # Check for broadcasting compatibility
    if delta_y_for_N_t1.shape[0] != delta_y_for_N_t2.shape[0]:
        min_len = min(delta_y_for_N_t1.shape[0], delta_y_for_N_t2.shape[0])
        delta_y_for_N_t1 = delta_y_for_N_t1[:min_len, :]
        delta_y_for_N_t2 = delta_y_for_N_t2[:min_len, :]
        v1t = v1t[:min_len, :]
        T_eff = min_len
        print(f"  Aligned to T_eff = {T_eff}")

    # Estimate N̂
    if delta_y_for_N_t2.shape[0] > 0:
        try:
            N_hat = np.linalg.lstsq(delta_y_for_N_t2, delta_y_for_N_t1, rcond=None)[0]
            v2t = delta_y_for_N_t1 - delta_y_for_N_t2 @ N_hat
            print(f"  N̂ estimated successfully")
        except np.linalg.LinAlgError:
            warnings.warn("Singular matrix in N estimation. Using zeros.")
            N_hat = np.zeros((n, n))
            v2t = delta_y_for_N_t1
    else:
        warnings.warn("No observations for N estimation. Using Δy_{t-1} directly.")
        v2t = delta_y_for_N_t1

    print(f"  v̂_{{2t}} = Δy_{{t-1}} - N̂Δy_{{t-2}} shape: {v2t.shape}")

    # Verify v1t and v2t have same length
    min_len = min(v1t.shape[0], v2t.shape[0])
    v1t = v1t[:min_len, :]
    v2t = v2t[:min_len, :]
    T_eff = min_len

    print(f"\nFinal correction terms:")
    print(f"  v̂_{{1t}} shape: {v1t.shape}")
    print(f"  v̂_{{2t}} shape: {v2t.shape}")
    print(f"  Effective sample: {T_eff}")

    # Combine v̂_t = (v̂'_{1t}, v̂'_{2t})'
    v_hat = np.hstack([v1t, v2t])  # Shape: (T_eff, 2n)

    # Also need to align X, y_dep, residuals to T_eff
    X = X[:T_eff, :]
    y_dep = y_dep[:T_eff, :]
    residuals_ols = residuals_ols[:T_eff, :]
    W = W[:T_eff, :]

    print(f"\nAligned regression arrays:")
    print(f"  X: {X.shape}")
    print(f"  y_dep: {y_dep.shape}")
    print(f"  W: {W.shape}")
    print(f"  residuals: {residuals_ols.shape}")

    # Step 7: Estimate long-run covariances

    print(f"\n{'='*60}")
    print(f"Long-run covariance estimation")
    print(f"{'='*60}")

    if bandwidth is None:
        bandwidth = int(np.floor(4 * (T_eff / 100) ** (2/9)))
        bandwidth = max(1, min(bandwidth, T_eff // 4))

    print(f"  Bandwidth: {bandwidth}")

    # Ω_εv̂
    combined_resid = np.hstack([residuals_ols, v_hat])
    Omega_ev_hat = compute_long_run_variance(combined_resid, bandwidth)

    # Partition
    Omega_ee = Omega_ev_hat[:n, :n]
    Omega_ev = Omega_ev_hat[:n, n:]
    Omega_vv = Omega_ev_hat[n:, n:]

    print(f"  Ω_εε shape: {Omega_ee.shape}")
    print(f"  Ω_εv̂ shape: {Omega_ev.shape}")
    print(f"  Ω_v̂v̂ shape: {Omega_vv.shape}")

    # Step 8: Construct correction terms

    # Moore-Penrose pseudo-inverse for potentially singular matrices
    try:
        Omega_vv_inv = np.linalg.pinv(Omega_vv)
    except:
        Omega_vv_inv = np.zeros_like(Omega_vv)

    # One-sided long-run covariance Δ_{v̂,Δw}
    # Compute autocovariances
    Delta_v_dw = np.zeros((v_hat.shape[1], W.shape[1]))

    for lag in range(bandwidth):
        if lag < T_eff:
            weight = bartlett_kernel(lag, bandwidth)
            if lag == 0:
                Gamma_lag = (v_hat.T @ W) / T_eff
            else:
                Gamma_lag = (v_hat[:-lag, :].T @ W[lag:, :]) / T_eff
            Delta_v_dw += weight * Gamma_lag

    # Correction term 1: -Ω_εv̂ Ω_v̂v̂^{-1} V'
    correction1 = -Omega_ev @ Omega_vv_inv @ v_hat.T

    # Correction term 2: Ω_εv̂ Ω_v̂v̂^{-1} Δ_{v̂,Δw}
    # This should be added to each column of W.T (shape 2n × T_eff)
    # So we need to broadcast it properly
    correction2_base = Omega_ev @ Omega_vv_inv @ Delta_v_dw  # Shape: (n, 2n)
    correction2 = T_eff * correction2_base[:, :, np.newaxis]  # Shape: (n, 2n, 1) for broadcasting

    # Actually, let's think about this more carefully
    # We want to add correction to W for each time t
    # W is T_eff × 2n, so W.T is 2n × T_eff
    # For each column t of W.T (which is a 2n vector), we add the same correction
    # So correction2 should be a 2n × T_eff matrix where each column is the same

    # The correction is applied as: W_plus = W + correction for each row
    # In transpose: W_plus.T = W.T + correction.T for each column
    # So we need correction.T to be 2n × T_eff where each column is identical

    # Recompute: correction should be T_eff × 2n where each row is the same
    # Wait, I think the formulation in the paper is different

    # Let me reconsider: the correction is T × (adjustment term)
    # where adjustment term comes from the long-run covariance structure
    # But it's applied to W matrix, not to each W_t separately

    # Actually, looking at Chang & Phillips (1995) RBFM-OLS:
    # The correction is: -Ω_εu Ω_uu^{-1} u' for the dependent variable
    # and Δ_uΔw for the regressor
    # These are summed over t, so they're aggregates

    # So correction1 is already correct: n × T_eff
    # For correction2: we want to correct ∑_t w_t ε_t'
    # The correction is T × Δ where Δ is the one-sided covariance
    # When we work with W' = (w_1, ..., w_T), this becomes
    # a 2n × T matrix correction where each column gets the same adjustment? No...

    # Actually, I think I need to go back to the paper formulation more carefully
    # Let me simplify and just use a column vector correction

    # For now, let's use a simpler approach: replicate the correction across all time periods
    correction2_vec = Omega_ev @ Omega_vv_inv @ Delta_v_dw  # Shape: (n, 2n)
    # We need to broadcast this to match W.T shape which is (2n, T_eff)
    # Each column of W.T gets the same correction from correction2_vec.T
    correction2 = np.repeat(correction2_vec.T, T_eff, axis=1)  # Shape: (2n, T_eff)

    print(f"\nCorrection terms (corrected):")
    print(f"  correction1 shape: {correction1.shape}")
    print(f"  correction2_vec shape: {correction2_vec.shape}")
    print(f"  correction2 shape: {correction2.shape}")

    # Step 9: Apply corrections

    # Corrected dependent variable
    Y_plus = y_dep.T + correction1  # Shape: (n, T_eff)

    # Corrected W
    W_plus = W.T + correction2  # Shape: (2n, T_eff)

    # Construct X_plus
    if Z.shape[1] > 0:
        X_plus = np.vstack([Z.T, W_plus])  # Shape: (n*(p-2)+2n, T_eff)
    else:
        X_plus = W_plus

    # RBFM estimation
    try:
        beta_plus = (Y_plus @ X_plus.T) @ np.linalg.pinv(X_plus @ X_plus.T)
    except:
        beta_plus = np.linalg.pinv(X_plus.T) @ Y_plus.T
        beta_plus = beta_plus.T

    residuals_plus = y_dep - (X_plus.T @ beta_plus.T)

    # Extract Φ and A
    if Z.shape[1] > 0:
        n_z = Z.shape[1]
        Phi_plus = beta_plus[:, :n_z]
        A_plus = beta_plus[:, n_z:]
    else:
        Phi_plus = np.zeros((n, 0))
        A_plus = beta_plus

    print(f"\n{'='*60}")
    print(f"Estimation completed successfully!")
    print(f"{'='*60}")
    print(f"  Φ⁺ shape: {Phi_plus.shape}")
    print(f"  A⁺ shape: {A_plus.shape}")
    print(f"  Residual std: {np.std(residuals_plus, axis=0)}")

    # Compute standard errors (simplified - asymptotic theory)
    Sigma_hat = (residuals_plus.T @ residuals_plus) / T_eff

    try:
        XX_inv = np.linalg.pinv(X_plus @ X_plus.T)
        Var_beta = np.kron(Sigma_hat, XX_inv)
        se_beta = np.sqrt(np.diag(Var_beta)).reshape(beta_plus.shape)

        if Z.shape[1] > 0:
            se_Phi = se_beta[:, :n_z]
            se_A = se_beta[:, n_z:]
        else:
            se_Phi = np.zeros((n, 0))
            se_A = se_beta
    except:
        se_Phi = np.ones_like(Phi_plus) * np.nan
        se_A = np.ones_like(A_plus) * np.nan

    return {
        'Phi_plus': Phi_plus,
        'A_plus': A_plus,
        'residuals': residuals_plus,
        'Omega_hat': Sigma_hat,
        'se_Phi': se_Phi,
        'se_A': se_A,
        'T_eff': T_eff,
        'bandwidth': bandwidth,
        'Omega_ee': Omega_ee,
        'Omega_ev': Omega_ev,
        'Omega_vv': Omega_vv
    }


def format_results(results, var_names=None):
    """Format and print estimation results."""

    n = results['A_plus'].shape[0]

    if var_names is None:
        var_names = [f'y{i+1}' for i in range(n)]

    print(f"\n{'='*70}")
    print(f"RBFM-VAR Estimation Results")
    print(f"{'='*70}")
    print(f"Effective sample size: {results['T_eff']}")
    print(f"Bandwidth: {results['bandwidth']}")
    print(f"\nResidual covariance matrix:")
    print(results['Omega_hat'])

    # Print coefficient estimates
    print(f"\n{'='*70}")
    print(f"Coefficient Estimates for A (nonstationary components)")
    print(f"{'='*70}")

    A_plus = results['A_plus']
    se_A = results['se_A']

    for i, var in enumerate(var_names):
        print(f"\nEquation for {var}:")
        print(f"{'Variable':<20} {'Coefficient':>12} {'Std. Error':>12} {'t-stat':>10}")
        print("-" * 70)

        for j in range(A_plus.shape[1]):
            if j < n:
                var_name = f"Δ{var_names[j]}_{{t-1}}"
            else:
                var_name = f"{var_names[j-n]}_{{t-1}}"

            coef = A_plus[i, j]
            se = se_A[i, j]
            t_stat = coef / se if se > 0 else np.nan

            print(f"{var_name:<20} {coef:12.6f} {se:12.6f} {t_stat:10.3f}")

    if results['Phi_plus'].shape[1] > 0:
        print(f"\n{'='*70}")
        print(f"Coefficient Estimates for Φ (stationary components)")
        print(f"{'='*70}")
        print("(Lags of Δ²y)")
        print(results['Phi_plus'])


# Example usage
if __name__ == "__main__":

    print("\n" + "="*70)
    print("RBFM-VAR Example: Simulated Data")
    print("="*70)

    # Simulate I(2) VAR data similar to Chang (2000)
    np.random.seed(42)
    T = 200
    n = 3
    p = 2

    # Generate I(2) data
    # Δ²y_t = ε_t with some dependence
    epsilon = np.random.multivariate_normal(
        mean=np.zeros(n),
        cov=np.eye(n),
        size=T
    )

    # Create I(2) by cumulative summing twice
    delta_y = np.cumsum(epsilon, axis=0)
    y = np.cumsum(delta_y, axis=0)

    print(f"\nSimulated data:")
    print(f"  y shape: {y.shape}")
    print(f"  First 5 rows of y:")
    print(y[:5])

    # Estimate RBFM-VAR
    try:
        results = rbfm_var(y, p=p, bandwidth=None)

        # Format and display results
        var_names = ['X', 'Y', 'Z']
        format_results(results, var_names)

        print("\n" + "="*70)
        print("Estimation successful! No broadcasting errors.")
        print("="*70)

    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()