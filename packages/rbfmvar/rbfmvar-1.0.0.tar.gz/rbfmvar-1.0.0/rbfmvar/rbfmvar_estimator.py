"""
RBFM-VAR Estimator
==================

Residual-Based Fully Modified Vector Autoregression Estimator
Based on Chang, Y. (2000). "Vector Autoregressions with Unknown Mixtures 
of I(0), I(1), and I(2) Components." Econometric Theory, 16(6), 905-926.

Author: Implementation by Claude for Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Dict
import warnings

from .kernel_estimators import KernelCovarianceEstimator
from .utils import construct_var_matrices, lag_matrix


class RBFMVAREstimator:
    """
    Residual-Based Fully Modified Vector Autoregression Estimator.
    
    This estimator handles VAR models with unknown mixtures of I(0), I(1), 
    and I(2) components without requiring prior knowledge about unit roots.
    
    Parameters
    ----------
    data : np.ndarray
        The (T x n) data matrix where T is sample size and n is number of variables
    p : int
        VAR lag order
    kernel : str, optional
        Kernel function for long-run covariance estimation. 
        Options: 'bartlett', 'parzen', 'quadratic_spectral', 'tukey_hanning'
        Default: 'bartlett'
    bandwidth : int or str, optional
        Bandwidth for kernel estimation. If 'auto', uses Andrews (1991) automatic selection.
        Default: 'auto'
    
    Attributes
    ----------
    Phi_plus : np.ndarray
        RBFM-VAR estimate of Φ (stationary component coefficients)
    A_plus : np.ndarray
        RBFM-VAR estimate of A (potentially nonstationary component coefficients)
    residuals : np.ndarray
        Estimated residuals
    Sigma_epsilon : np.ndarray
        Estimated error covariance matrix
    """
    
    def __init__(
        self,
        data: np.ndarray,
        p: int,
        kernel: str = 'bartlett',
        bandwidth: Optional[int] = None
    ):
        """Initialize RBFM-VAR estimator."""
        self.data = np.asarray(data)
        self.T, self.n = self.data.shape
        self.p = p
        self.kernel = kernel
        self.bandwidth = bandwidth
        
        # Check data shape
        if self.T < self.p + 10:
            raise ValueError(f"Sample size {self.T} too small for lag order {self.p}")
        
        # Initialize results storage
        self.Phi_plus = None
        self.A_plus = None
        self.residuals = None
        self.Sigma_epsilon = None
        self.N_hat = None
        self.v_hat = None
        
        # Long-run covariance estimates
        self.Omega_ev = None
        self.Omega_vv = None
        self.Delta_vDeltaw = None
        
    def fit(self) -> 'RBFMVAREstimator':
        """
        Fit the RBFM-VAR model.
        
        Follows equations (12)-(13) in Chang (2000).
        
        Returns
        -------
        self : RBFMVAREstimator
            Fitted estimator
        """
        # Step 1: Construct Z, W matrices (equation 3)
        Z, W, Y = self._construct_regression_matrices()
        
        # Step 2: Get OLS residuals and construct v_hat (equation 11)
        ols_residuals, self.N_hat = self._compute_ols_residuals(Y, W)
        self.v_hat = self._construct_v_hat(W, self.N_hat)
        
        # Step 3: Estimate long-run covariances
        self._estimate_long_run_covariances(ols_residuals, self.v_hat, W)
        
        # Step 4: Construct correction terms (equation 13)
        Y_plus, Delta_plus = self._compute_corrections(Y, self.v_hat, W)
        
        # Step 5: Compute RBFM-VAR estimates (equation 12)
        X = np.hstack([Z, W])
        XtX_inv = np.linalg.inv(X.T @ X)
        
        F_plus = (Y_plus.T @ Z, Y_plus.T @ W + self.T * Delta_plus) @ XtX_inv
        
        # Extract Phi and A from F = (Phi, A)
        n_z = Z.shape[1]
        self.Phi_plus = F_plus[:, :n_z]
        self.A_plus = F_plus[:, n_z:]
        
        # Compute residuals
        self.residuals = Y - X @ F_plus.T
        self.Sigma_epsilon = (self.residuals.T @ self.residuals) / self.T
        
        return self
    
    def _construct_regression_matrices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Construct Z, W, Y matrices for regression (equation 3).
        
        Model: y_t = Φ z_t + A w_t + ε_t
        where z_t = (Δ²y_{t-1}, ..., Δ²y_{t-p+2})'  (stationary regressors)
              w_t = (Δy_{t-1}, y_{t-1})'              (potentially nonstationary)
        
        Returns
        -------
        Z : np.ndarray
            (T_eff x n(p-2)) matrix of second-differenced lags
        W : np.ndarray
            (T_eff x 2n) matrix of first differences and levels
        Y : np.ndarray
            (T_eff x n) dependent variable matrix
        """
        y = self.data
        n, p = self.n, self.p
        
        # Effective sample size after losing observations for lags and differencing
        T_eff = self.T - p
        
        # Initialize matrices
        Z_list = []
        
        # Construct Z: second differences Δ²y_{t-1}, ..., Δ²y_{t-p+2}
        # Δ²y_t = y_t - 2y_{t-1} + y_{t-2}
        for lag in range(1, p - 1):
            # Second difference at lag
            if lag == 1:
                # Δ²y_{t-1} = y_{t-1} - 2y_{t-2} + y_{t-3}
                delta2_y = y[p-1-lag:self.T-lag] - 2*y[p-2-lag:self.T-lag-1] + y[p-3-lag:self.T-lag-2]
            else:
                delta2_y = y[p-1-lag:self.T-lag] - 2*y[p-2-lag:self.T-lag-1] + y[p-3-lag:self.T-lag-2]
            Z_list.append(delta2_y[:T_eff])
        
        if len(Z_list) > 0:
            Z = np.column_stack(Z_list)
        else:
            # If p = 1, Z is empty
            Z = np.zeros((T_eff, 0))
        
        # Construct W: [Δy_{t-1}, y_{t-1}]
        # Δy_{t-1} = y_{t-1} - y_{t-2}
        Delta_y_lag1 = y[p-1:self.T-1] - y[p-2:self.T-2]
        y_lag1 = y[p-1:self.T-1]
        W = np.column_stack([Delta_y_lag1[:T_eff], y_lag1[:T_eff]])
        
        # Y: y_t for t = p+1, ..., T
        Y = y[p:self.T]
        
        return Z, W, Y
    
    def _compute_ols_residuals(
        self, 
        Y: np.ndarray, 
        W: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute OLS residuals and estimate N (equation 11).
        
        The residual process v_hat is constructed as:
        v_hat_t = [Δ²y_{t-1}, Δy_{t-1} - N̂Δy_{t-2}]'
        
        where N̂ is from regressing Δy_{t-1} on Δy_{t-2}.
        
        Returns
        -------
        ols_residuals : np.ndarray
            OLS residuals from full model
        N_hat : np.ndarray
            Estimated N matrix
        """
        # First get OLS estimates for the full model
        Z, W_full, Y_full = self._construct_regression_matrices()
        X = np.hstack([Z, W_full])
        
        # OLS: F_ols = (X'X)^{-1}X'Y
        XtX_inv = np.linalg.inv(X.T @ X)
        F_ols = XtX_inv @ X.T @ Y_full
        ols_residuals = Y_full - X @ F_ols
        
        # Estimate N from regression of Δy_{t-1} on Δy_{t-2}
        # Extract Δy from data
        Delta_y = np.diff(self.data, axis=0)
        
        # Δy_{t-1} and Δy_{t-2}
        Delta_y_lag1 = Delta_y[self.p-1:self.T-2]  # Δy_{t-1}
        Delta_y_lag2 = Delta_y[self.p-2:self.T-3]  # Δy_{t-2}
        
        # Make sure dimensions match
        min_len = min(len(Delta_y_lag1), len(Delta_y_lag2))
        Delta_y_lag1 = Delta_y_lag1[:min_len]
        Delta_y_lag2 = Delta_y_lag2[:min_len]
        
        # OLS regression: Δy_{t-1} = N Δy_{t-2} + error
        N_hat = Delta_y_lag1.T @ Delta_y_lag2 @ np.linalg.inv(Delta_y_lag2.T @ Delta_y_lag2)
        
        return ols_residuals, N_hat
    
    def _construct_v_hat(self, W: np.ndarray, N_hat: np.ndarray) -> np.ndarray:
        """
        Construct the v_hat process (equation 11).
        
        v_hat_t = [v̂_{1t}, v̂_{2t}]' where:
        v̂_{1t} = Δ²y_{t-1}
        v̂_{2t} = Δy_{t-1} - N̂Δy_{t-2}
        
        Parameters
        ----------
        W : np.ndarray
            W matrix containing [Δy_{t-1}, y_{t-1}]
        N_hat : np.ndarray
            Estimated N matrix
        
        Returns
        -------
        v_hat : np.ndarray
            The v_hat process
        """
        n = self.n
        p = self.p
        
        # Compute Δ²y_{t-1} = y_{t-1} - 2y_{t-2} + y_{t-3}
        y = self.data
        T_eff = len(W)
        
        # Δ²y_{t-1}
        v1 = y[p-1:p-1+T_eff] - 2*y[p-2:p-2+T_eff] + y[p-3:p-3+T_eff]
        
        # Δy_{t-1} - N̂Δy_{t-2}
        Delta_y_lag1 = y[p-1:p-1+T_eff] - y[p-2:p-2+T_eff]
        Delta_y_lag2 = y[p-2:p-2+T_eff] - y[p-3:p-3+T_eff]
        
        v2 = Delta_y_lag1 - Delta_y_lag2 @ N_hat.T
        
        # Stack v1 and v2
        v_hat = np.column_stack([v1, v2])
        
        return v_hat
    
    def _estimate_long_run_covariances(
        self,
        epsilon_hat: np.ndarray,
        v_hat: np.ndarray,
        W: np.ndarray
    ) -> None:
        """
        Estimate long-run covariance matrices using kernel methods.
        
        Estimates:
        - Ω̂_{εv̂}: long-run covariance of (ε_t, v̂_t)
        - Ω̂_{v̂v̂}: long-run covariance of v̂_t
        - Δ̂_{v̂Δw}: one-sided long-run covariance of v̂_t and Δw_t
        
        Parameters
        ----------
        epsilon_hat : np.ndarray
            OLS residuals
        v_hat : np.ndarray
            The v_hat process
        W : np.ndarray
            W matrix
        """
        kernel_estimator = KernelCovarianceEstimator(
            kernel=self.kernel,
            bandwidth=self.bandwidth
        )
        
        # Ω̂_{εv̂}: long-run covariance of (ε, v̂)
        self.Omega_ev = kernel_estimator.estimate_long_run_covariance(
            epsilon_hat, v_hat
        )
        
        # Ω̂_{v̂v̂}: long-run covariance of v̂
        self.Omega_vv = kernel_estimator.estimate_long_run_covariance(
            v_hat, v_hat
        )
        
        # Compute Δw_t
        Delta_w = np.diff(W, axis=0)
        # Align v_hat and Delta_w
        v_hat_aligned = v_hat[1:]
        
        # Δ̂_{v̂Δw}: one-sided long-run covariance
        self.Delta_vDeltaw = kernel_estimator.estimate_one_sided_long_run_covariance(
            v_hat_aligned, Delta_w
        )
    
    def _compute_corrections(
        self,
        Y: np.ndarray,
        v_hat: np.ndarray,
        W: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute correction terms Y^+ and Δ^+ (equation 13).
        
        Y^{+} = Y' - Ω̂_{εv̂} Ω̂_{v̂v̂}^{-1} V̂'
        Δ̂^{+} = Ω̂_{εv̂} Ω̂_{v̂v̂}^{-1} Δ̂_{v̂Δw}
        
        Parameters
        ----------
        Y : np.ndarray
            Dependent variable matrix
        v_hat : np.ndarray
            The v_hat process
        W : np.ndarray
            W matrix
        
        Returns
        -------
        Y_plus : np.ndarray
            Corrected Y
        Delta_plus : np.ndarray
            Correction for serial correlation
        """
        # Handle potential singularity in Omega_vv using Moore-Penrose inverse
        try:
            Omega_vv_inv = np.linalg.inv(self.Omega_vv)
        except np.linalg.LinAlgError:
            warnings.warn("Omega_vv is singular, using pseudo-inverse")
            Omega_vv_inv = np.linalg.pinv(self.Omega_vv)
        
        # Y^{+} = Y' - Ω̂_{εv̂} Ω̂_{v̂v̂}^{-1} V̂'
        correction_Y = self.Omega_ev @ Omega_vv_inv @ v_hat.T
        Y_plus = Y.T - correction_Y
        Y_plus = Y_plus.T  # Transpose back
        
        # Δ̂^{+} = Ω̂_{εv̂} Ω̂_{v̂v̂}^{-1} Δ̂_{v̂Δw}
        Delta_plus = self.Omega_ev @ Omega_vv_inv @ self.Delta_vDeltaw
        
        return Y_plus, Delta_plus
    
    def predict(self, steps: int = 1) -> np.ndarray:
        """
        Generate forecasts from fitted RBFM-VAR model.
        
        Parameters
        ----------
        steps : int
            Number of steps ahead to forecast
        
        Returns
        -------
        forecasts : np.ndarray
            (steps x n) array of forecasts
        """
        if self.Phi_plus is None or self.A_plus is None:
            raise ValueError("Model must be fitted before prediction")
        
        # Get last p observations
        y_hist = self.data[-self.p:].copy()
        forecasts = []
        
        for _ in range(steps):
            # Construct Z_t and W_t for forecast
            Z_t, W_t = self._construct_forecast_regressors(y_hist)
            
            # Forecast: y_{T+h} = Φ̂^+ z_{T+h} + Â^+ w_{T+h}
            y_forecast = self.Phi_plus @ Z_t + self.A_plus @ W_t
            
            forecasts.append(y_forecast)
            
            # Update history
            y_hist = np.vstack([y_hist[1:], y_forecast])
        
        return np.array(forecasts)
    
    def _construct_forecast_regressors(
        self, 
        y_hist: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Construct Z and W for forecasting.
        
        Parameters
        ----------
        y_hist : np.ndarray
            Last p observations
        
        Returns
        -------
        Z_t : np.ndarray
            Second differences
        W_t : np.ndarray
            First difference and level
        """
        # Construct Z: second differences
        Z_components = []
        for lag in range(1, self.p - 1):
            delta2_y = (y_hist[-lag] - 2*y_hist[-lag-1] + y_hist[-lag-2]).flatten()
            Z_components.append(delta2_y)
        
        if Z_components:
            Z_t = np.concatenate(Z_components)
        else:
            Z_t = np.array([])
        
        # Construct W: [Δy_{-1}, y_{-1}]
        Delta_y = (y_hist[-1] - y_hist[-2]).flatten()
        y_level = y_hist[-1].flatten()
        W_t = np.concatenate([Delta_y, y_level])
        
        return Z_t, W_t
    
    def summary(self) -> Dict:
        """
        Provide summary statistics of fitted model.
        
        Returns
        -------
        summary : dict
            Dictionary containing model summary statistics
        """
        if self.Phi_plus is None:
            raise ValueError("Model must be fitted first")
        
        summary = {
            'n_vars': self.n,
            'lag_order': self.p,
            'sample_size': self.T,
            'effective_sample_size': self.T - self.p,
            'Phi_estimate': self.Phi_plus,
            'A_estimate': self.A_plus,
            'Sigma_epsilon': self.Sigma_epsilon,
            'residual_std': np.sqrt(np.diag(self.Sigma_epsilon)),
            'log_likelihood': self._compute_log_likelihood(),
            'AIC': self._compute_aic(),
            'BIC': self._compute_bic()
        }
        
        return summary
    
    def _compute_log_likelihood(self) -> float:
        """Compute log-likelihood of fitted model."""
        T_eff = self.T - self.p
        k = self.n
        
        # Log-likelihood for Gaussian VAR
        log_lik = -0.5 * T_eff * k * np.log(2 * np.pi)
        log_lik -= 0.5 * T_eff * np.log(np.linalg.det(self.Sigma_epsilon))
        log_lik -= 0.5 * T_eff * k
        
        return log_lik
    
    def _compute_aic(self) -> float:
        """Compute Akaike Information Criterion."""
        n_params = self.n * (self.n * self.p + self.n)  # Total parameters
        return -2 * self._compute_log_likelihood() + 2 * n_params
    
    def _compute_bic(self) -> float:
        """Compute Bayesian Information Criterion."""
        T_eff = self.T - self.p
        n_params = self.n * (self.n * self.p + self.n)
        return -2 * self._compute_log_likelihood() + np.log(T_eff) * n_params
