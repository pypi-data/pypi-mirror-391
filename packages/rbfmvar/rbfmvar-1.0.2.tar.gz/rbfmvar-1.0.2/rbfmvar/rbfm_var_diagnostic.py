"""
RBFM-VAR Implementation - Broadcasting Error Fix
Based on Chang (2000)

This version focuses on correctly handling array dimensions to avoid the common
broadcasting error: "operands could not be broadcast together with shapes (49,3) (0,3)"
"""

import numpy as np
import warnings

def rbfm_var_simple(y, p, verbose=True):
    """
    Simplified RBFM-VAR estimation with explicit dimension checking.
    
    Parameters:
    -----------
    y : array-like, shape (T, n)
        Time series data
    p : int
        Lag order
    verbose : bool
        Print diagnostic information
        
    Returns:
    --------
    results : dict
        Estimation results
    """
    
    y = np.asarray(y)
    T, n = y.shape
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"RBFM-VAR Estimation - Diagnostic Mode")
        print(f"{'='*70}")
        print(f"Input data shape: {y.shape}")
        print(f"T (sample size) = {T}, n (variables) = {n}, p (lags) = {p}")
    
    # CRITICAL: Check minimum sample size
    min_T = p + 5  # Need enough observations after differencing and lagging
    if T < min_T:
        raise ValueError(
            f"Sample size too small!\n"
            f"  Current T = {T}\n"
            f"  Minimum required = {min_T} (p + 5)\n"
            f"  After taking differences and lags, no observations would remain."
        )
    
    # Step 1: Create differences
    if verbose:
        print(f"\n{'-'*70}")
        print("Step 1: Creating differences")
        print(f"{'-'*70}")
    
    delta_y = np.diff(y, axis=0)  # First difference, shape: (T-1, n)
    delta2_y = np.diff(delta_y, axis=0)  # Second difference, shape: (T-2, n)
    
    if verbose:
        print(f"  Original y:     {y.shape}")
        print(f"  Δy:             {delta_y.shape}")
        print(f"  Δ²y:            {delta2_y.shape}")
    
    # Step 2: Determine effective sample size
    # After taking Δ²y (loses 2 obs) and p lags (loses p obs), we have:
    T_eff = T - 2 - p + 1  # Effective sample size for regression
    
    if verbose:
        print(f"\n{'-'*70}")
        print(f"Step 2: Determining effective sample")
        print(f"{'-'*70}")
        print(f"  Observations lost to Δ²y: 2")
        print(f"  Observations lost to lags: {p-1}")
        print(f"  Effective sample size: {T_eff}")
    
    if T_eff < 10:
        warnings.warn(
            f"Very small effective sample size: {T_eff}. "
            f"Consider reducing lag order or using more data."
        )
    
    # Step 3: Construct regressors
    if verbose:
        print(f"\n{'-'*70}")
        print(f"Step 3: Constructing regressors")
        print(f"{'-'*70}")
    
    # W_t = (Δy_{t-1}', y_{t-1}')' - the potentially nonstationary regressors
    # For time t in effective sample:
    #   - We need Δy at lag 1: Δy_{t-1}
    #   - We need y at lag 1: y_{t-1}
    
    # Since delta2_y[i] corresponds to time i+2 in original series,
    # and we're regressing delta2_y[p-1:p-1+T_eff],
    # these correspond to times p+1, p+2, ..., p+T_eff in original series
    
    # For Δy_{t-1}, we need Δy at times p, p+1, ..., p+T_eff-1
    # These are delta_y[p-1:p-1+T_eff]
    
    start_idx_dy = p - 1
    end_idx_dy = p - 1 + T_eff
    delta_y_t1 = delta_y[start_idx_dy:end_idx_dy, :]
    
    # For y_{t-1}, we need y at times p, p+1, ..., p+T_eff-1
    # These are y[p-1:p-1+T_eff]
    y_t1 = y[start_idx_dy:end_idx_dy, :]
    
    if verbose:
        print(f"  Δy_{{t-1}} indices: [{start_idx_dy}:{end_idx_dy}]")
        print(f"  Δy_{{t-1}} shape: {delta_y_t1.shape}")
        print(f"  y_{{t-1}} shape: {y_t1.shape}")
    
    # Verify dimensions
    assert delta_y_t1.shape[0] == T_eff, \
        f"Dimension error: delta_y_t1 has {delta_y_t1.shape[0]} rows, expected {T_eff}"
    assert y_t1.shape[0] == T_eff, \
        f"Dimension error: y_t1 has {y_t1.shape[0]} rows, expected {T_eff}"
    
    W = np.hstack([delta_y_t1, y_t1])  # Shape: (T_eff, 2n)
    
    if verbose:
        print(f"  W = [Δy_{{t-1}}, y_{{t-1}}] shape: {W.shape}")
        print(f"  ✓ Dimension check passed")
    
    # Dependent variable: Δ²y_t
    start_idx_y = p - 1
    end_idx_y = p - 1 + T_eff
    y_dep = delta2_y[start_idx_y:end_idx_y, :]
    
    if verbose:
        print(f"  Δ²y_t indices: [{start_idx_y}:{end_idx_y}]")
        print(f"  Δ²y_t shape: {y_dep.shape}")
    
    assert y_dep.shape[0] == T_eff, \
        f"Dimension error: y_dep has {y_dep.shape[0]} rows, expected {T_eff}"
    
    # For simplicity, we only use W (no additional Z regressors)
    X = W
    
    if verbose:
        print(f"\n  Final regression arrays:")
        print(f"    X (regressors): {X.shape}")
        print(f"    y (dependent):  {y_dep.shape}")
        print(f"    All arrays have {T_eff} observations ✓")
    
    # Step 4: OLS Estimation
    if verbose:
        print(f"\n{'-'*70}")
        print(f"Step 4: OLS Estimation")
        print(f"{'-'*70}")
    
    try:
        beta_ols = np.linalg.lstsq(X, y_dep, rcond=None)[0]
        residuals = y_dep - X @ beta_ols
        
        if verbose:
            print(f"  ✓ OLS completed successfully")
            print(f"  Coefficients shape: {beta_ols.shape}")
            print(f"  Residuals shape: {residuals.shape}")
            print(f"  Residual std: {np.std(residuals, axis=0)}")
            
    except np.linalg.LinAlgError as e:
        raise RuntimeError(f"OLS estimation failed: {e}")
    
    # Step 5: Construct v̂_t for corrections
    if verbose:
        print(f"\n{'-'*70}")
        print(f"Step 5: Constructing v̂_t (THIS IS WHERE ERRORS TYPICALLY OCCUR)")
        print(f"{'-'*70}")
    
    # v̂_t = (v̂'_{1t}, v̂'_{2t})' where:
    # v̂_{1t} = Δ²y_{t-1}
    # v̂_{2t} = Δy_{t-1} - N̂Δy_{t-2}
    
    # KEY FIX: Ensure all arrays have T_eff observations
    
    # v̂_{1t} = Δ²y_{t-1}
    # Since delta2_y[i] is at time i+2, and we want lag 1,
    # for regression times p+1,...,p+T_eff, we need delta2_y at times p,...,p+T_eff-1
    # These are delta2_y[p-2:p-2+T_eff] BUT p-2 might be negative!
    
    v1t_start = max(0, p - 2)
    v1t_end = v1t_start + T_eff
    
    # Check if we have enough data
    if v1t_end > len(delta2_y):
        # Reduce T_eff
        T_eff_new = len(delta2_y) - v1t_start
        if verbose:
            print(f"  WARNING: Reducing T_eff from {T_eff} to {T_eff_new}")
        T_eff = T_eff_new
        v1t_end = v1t_start + T_eff
        
        # Also reduce other arrays
        X = X[:T_eff, :]
        y_dep = y_dep[:T_eff, :]
        residuals = residuals[:T_eff, :]
        W = W[:T_eff, :]
        delta_y_t1 = delta_y_t1[:T_eff, :]
    
    v1t = delta2_y[v1t_start:v1t_end, :]
    
    if verbose:
        print(f"  v̂_{{1t}} = Δ²y_{{t-1}}")
        print(f"    Indices: [{v1t_start}:{v1t_end}]")
        print(f"    Shape: {v1t.shape}")
    
    assert v1t.shape[0] == T_eff, \
        f"ERROR: v1t has {v1t.shape[0]} rows, but T_eff = {T_eff}"
    
    # For v̂_{2t} = Δy_{t-1} - N̂Δy_{t-2}
    # We need Δy_{t-1} and Δy_{t-2} aligned
    
    # Δy_{t-1} for regression sample times p+1,...,p+T_eff
    # are at times p,...,p+T_eff-1, which are delta_y[p-1:p-1+T_eff]
    dy_for_v2_t1 = delta_y[p-1:p-1+T_eff, :]
    
    # Δy_{t-2} for regression sample times p+1,...,p+T_eff
    # are at times p-1,...,p+T_eff-2, which are delta_y[p-2:p-2+T_eff]
    # BUT p-2 might be < 0!
    
    dy_t2_start = p - 2
    if dy_t2_start < 0:
        # Cannot compute Δy_{t-2} for early observations
        # Need to further reduce sample
        offset = -dy_t2_start
        dy_t2_start = 0
        
        # Adjust all arrays
        T_eff = T_eff - offset
        v1t = v1t[offset:, :]
        dy_for_v2_t1 = dy_for_v2_t1[offset:, :]
        X = X[offset:, :]
        y_dep = y_dep[offset:, :]
        residuals = residuals[offset:, :]
        W = W[offset:, :]
        
        if verbose:
            print(f"  WARNING: p too large, reducing T_eff to {T_eff}")
    
    dy_for_v2_t2 = delta_y[dy_t2_start:dy_t2_start+T_eff, :]
    
    if verbose:
        print(f"  For N̂ estimation:")
        print(f"    Δy_{{t-1}} shape: {dy_for_v2_t1.shape}")
        print(f"    Δy_{{t-2}} shape: {dy_for_v2_t2.shape}")
    
    # CRITICAL CHECK
    if dy_for_v2_t1.shape[0] != dy_for_v2_t2.shape[0]:
        raise ValueError(
            f"BROADCASTING ERROR WOULD OCCUR HERE!\n"
            f"  Δy_{{t-1}} shape: {dy_for_v2_t1.shape}\n"
            f"  Δy_{{t-2}} shape: {dy_for_v2_t2.shape}\n"
            f"These must have the same number of rows."
        )
    
    if dy_for_v2_t2.shape[0] == 0:
        raise ValueError(
            f"No observations available for Δy_{{t-2}}!\n"
            f"  This means your sample size is too small or lag order too large.\n"
            f"  Try: (1) Using more data, or (2) Reducing p"
        )
    
    # Estimate N̂
    try:
        N_hat = np.linalg.lstsq(dy_for_v2_t2, dy_for_v2_t1, rcond=None)[0]
        v2t = dy_for_v2_t1 - dy_for_v2_t2 @ N_hat
        
        if verbose:
            print(f"  ✓ N̂ estimated successfully")
            print(f"  v̂_{{2t}} shape: {v2t.shape}")
            
    except np.linalg.LinAlgError:
        warnings.warn("Singular matrix in N estimation")
        v2t = dy_for_v2_t1
    
    # Final check
    assert v1t.shape[0] == v2t.shape[0] == T_eff, \
        f"Final dimension mismatch: v1t={v1t.shape}, v2t={v2t.shape}, T_eff={T_eff}"
    
    v_hat = np.hstack([v1t, v2t])
    
    if verbose:
        print(f"\n  ✓ v̂_t constructed successfully")
        print(f"    v̂_t shape: {v_hat.shape}")
        print(f"    All arrays aligned with T_eff = {T_eff}")
    
    # Return results
    return {
        'coefficients': beta_ols,
        'residuals': residuals,
        'T_eff': T_eff,
        'v_hat': v_hat,
        'X': X,
        'y_dep': y_dep,
        'success': True
    }


def diagnose_data(y, p):
    """
    Run diagnostic checks on data before estimation.
    """
    print(f"\n{'='*70}")
    print(f"PRE-ESTIMATION DIAGNOSTICS")
    print(f"{'='*70}")
    
    y = np.asarray(y)
    T, n = y.shape
    
    print(f"\nData characteristics:")
    print(f"  Shape: {y.shape}")
    print(f"  T (observations) = {T}")
    print(f"  n (variables) = {n}")
    print(f"  p (lag order) = {p}")
    
    # Check for sufficient sample
    print(f"\nSample size check:")
    T_after_diff = T - 2
    print(f"  After Δ²y: {T_after_diff} observations")
    
    T_after_lags = T_after_diff - (p - 1)
    print(f"  After lags: {T_after_lags} observations")
    
    if T_after_lags < 10:
        print(f"  ⚠ WARNING: Very small effective sample!")
        print(f"  Recommendation: Use p ≤ {max(1, T-12)} or get more data")
    else:
        print(f"  ✓ Sample size adequate")
    
    # Check for missing values
    if np.any(np.isnan(y)):
        print(f"\n  ⚠ WARNING: Data contains NaN values!")
        print(f"    Number of NaNs: {np.sum(np.isnan(y))}")
    else:
        print(f"\n  ✓ No missing values")
    
    # Check for constant series
    for i in range(n):
        if np.std(y[:, i]) < 1e-10:
            print(f"  ⚠ WARNING: Variable {i+1} appears constant!")
    
    print(f"\n{'='*70}\n")


# Example usage
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("RBFM-VAR Broadcasting Error Fix - Demo")
    print("="*70)
    
    # Example 1: Data that would cause the error (too small sample)
    print("\n\nExample 1: Small sample (will show warnings)")
    print("-" * 70)
    
    np.random.seed(42)
    T_small = 50  # Small sample
    n = 3
    p = 2
    
    # Generate simple I(2) data
    epsilon = np.random.randn(T_small, n)
    delta_y = np.cumsum(epsilon, axis=0)
    y_small = np.cumsum(delta_y, axis=0)
    
    diagnose_data(y_small, p)
    
    try:
        results1 = rbfm_var_simple(y_small, p, verbose=True)
        print("\n✓ Estimation completed successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Example 2: Adequate sample size
    print("\n\n" + "="*70)
    print("Example 2: Adequate sample size")
    print("="*70)
    
    T_adequate = 200
    epsilon = np.random.randn(T_adequate, n)
    delta_y = np.cumsum(epsilon, axis=0)
    y_adequate = np.cumsum(delta_y, axis=0)
    
    diagnose_data(y_adequate, p)
    
    try:
        results2 = rbfm_var_simple(y_adequate, p, verbose=True)
        print("\n✓ Estimation completed successfully!")
        print(f"\nCoefficient estimates:")
        print(results2['coefficients'])
    except Exception as e:
        print(f"\n✗ Error: {e}")
