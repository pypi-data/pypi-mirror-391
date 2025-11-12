"""
Kernel-based Long-Run Covariance Estimators
==========================================

Implements kernel-based estimators for long-run covariance matrices
as used in Chang (2000) following Andrews (1991) and Newey-West (1987).

Author: Implementation by Claude for Dr. Merwan Roudane
"""

import numpy as np
from typing import Optional, Callable
import warnings


class KernelCovarianceEstimator:
    """
    Kernel-based estimator for long-run covariance matrices.
    
    Parameters
    ----------
    kernel : str
        Kernel function. Options:
        - 'bartlett': Bartlett (Newey-West) kernel
        - 'parzen': Parzen kernel  
        - 'quadratic_spectral': Quadratic Spectral (Andrews) kernel
        - 'tukey_hanning': Tukey-Hanning kernel
    bandwidth : int or None
        Bandwidth parameter K. If None, uses automatic selection.
    """
    
    AVAILABLE_KERNELS = ['bartlett', 'parzen', 'quadratic_spectral', 'tukey_hanning']
    
    def __init__(self, kernel: str = 'bartlett', bandwidth: Optional[int] = None):
        """Initialize kernel covariance estimator."""
        if kernel not in self.AVAILABLE_KERNELS:
            raise ValueError(f"Kernel must be one of {self.AVAILABLE_KERNELS}")
        
        self.kernel = kernel
        self.bandwidth = bandwidth
        self._kernel_func = self._get_kernel_function(kernel)
    
    def _get_kernel_function(self, kernel: str) -> Callable:
        """Get the kernel weight function."""
        if kernel == 'bartlett':
            return self._bartlett_kernel
        elif kernel == 'parzen':
            return self._parzen_kernel
        elif kernel == 'quadratic_spectral':
            return self._quadratic_spectral_kernel
        elif kernel == 'tukey_hanning':
            return self._tukey_hanning_kernel
    
    @staticmethod
    def _bartlett_kernel(x: np.ndarray) -> np.ndarray:
        """
        Bartlett (Newey-West) kernel.
        
        k(x) = 1 - |x| for |x| ≤ 1, 0 otherwise
        """
        return np.maximum(1 - np.abs(x), 0)
    
    @staticmethod
    def _parzen_kernel(x: np.ndarray) -> np.ndarray:
        """
        Parzen kernel.
        
        k(x) = 1 - 6x² + 6|x|³ for |x| ≤ 1/2
             = 2(1-|x|)³ for 1/2 < |x| ≤ 1
             = 0 otherwise
        """
        abs_x = np.abs(x)
        kernel = np.zeros_like(x)
        
        # Region 1: |x| ≤ 1/2
        mask1 = abs_x <= 0.5
        kernel[mask1] = 1 - 6*abs_x[mask1]**2 + 6*abs_x[mask1]**3
        
        # Region 2: 1/2 < |x| ≤ 1
        mask2 = (abs_x > 0.5) & (abs_x <= 1)
        kernel[mask2] = 2 * (1 - abs_x[mask2])**3
        
        return kernel
    
    @staticmethod
    def _quadratic_spectral_kernel(x: np.ndarray) -> np.ndarray:
        """
        Quadratic Spectral (Andrews) kernel.
        
        k(x) = (25/(12π²x²)) * [sin(6πx/5)/(6πx/5) - cos(6πx/5)]
        """
        # Handle x = 0 separately
        kernel = np.ones_like(x, dtype=float)
        
        nonzero = x != 0
        if np.any(nonzero):
            x_nz = x[nonzero]
            arg = 6 * np.pi * x_nz / 5
            kernel[nonzero] = (25 / (12 * np.pi**2 * x_nz**2)) * \
                              (np.sin(arg) / arg - np.cos(arg))
        
        return kernel
    
    @staticmethod
    def _tukey_hanning_kernel(x: np.ndarray) -> np.ndarray:
        """
        Tukey-Hanning kernel.
        
        k(x) = (1 + cos(πx))/2 for |x| ≤ 1, 0 otherwise
        """
        mask = np.abs(x) <= 1
        kernel = np.zeros_like(x)
        kernel[mask] = (1 + np.cos(np.pi * x[mask])) / 2
        return kernel
    
    def select_bandwidth_andrews(self, residuals: np.ndarray) -> int:
        """
        Automatic bandwidth selection following Andrews (1991).
        
        Parameters
        ----------
        residuals : np.ndarray
            Residuals for bandwidth selection
        
        Returns
        -------
        bandwidth : int
            Selected bandwidth
        """
        T = len(residuals)
        
        # Fit AR(1) to each series to get rho
        if residuals.ndim == 1:
            residuals = residuals.reshape(-1, 1)
        
        rhos = []
        sigmas = []
        
        for i in range(residuals.shape[1]):
            u = residuals[:, i]
            u_lag = u[:-1]
            u_lead = u[1:]
            
            # AR(1): u_t = ρ u_{t-1} + η_t
            rho = np.sum(u_lead * u_lag) / np.sum(u_lag * u_lag)
            rho = np.clip(rho, -0.97, 0.97)  # Bound for stability
            
            # Variance of innovations
            residual_ar = u_lead - rho * u_lag
            sigma_sq = np.mean(residual_ar**2)
            
            rhos.append(rho)
            sigmas.append(sigma_sq)
        
        # Average across series
        rho = np.mean(rhos)
        sigma_sq = np.mean(sigmas)
        
        # Compute alpha parameters (Andrews 1991, Table 1)
        if self.kernel == 'bartlett':
            alpha = (1.1447 * ((rho/(1-rho))**2))**(1/3)
        elif self.kernel == 'parzen':
            alpha = (2.6614 * ((rho/(1-rho))**2))**(1/5)
        elif self.kernel == 'quadratic_spectral':
            alpha = (1.3221 * ((rho/(1-rho))**2))**(1/5)
        elif self.kernel == 'tukey_hanning':
            alpha = (1.7462 * ((rho/(1-rho))**2))**(1/5)
        else:
            alpha = 1.0
        
        # Bandwidth
        bandwidth = int(np.ceil(alpha * (T**(1/3))))
        
        return max(bandwidth, 1)  # At least 1
    
    def estimate_long_run_covariance(
        self, 
        X: np.ndarray, 
        Y: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Estimate long-run covariance matrix Ω = Σ_{k=-∞}^{∞} E[X_t Y'_{t-k}].
        
        If Y is None, estimates Ω_XX. Otherwise estimates Ω_XY.
        
        Parameters
        ----------
        X : np.ndarray
            (T x n_x) time series
        Y : np.ndarray, optional
            (T x n_y) time series. If None, Y = X.
        
        Returns
        -------
        Omega : np.ndarray
            (n_x x n_y) long-run covariance matrix
        """
        if Y is None:
            Y = X
        
        X = np.atleast_2d(X)
        Y = np.atleast_2d(Y)
        
        if X.shape[0] != Y.shape[0]:
            raise ValueError("X and Y must have same length")
        
        T = X.shape[0]
        
        # Select bandwidth if not provided
        if self.bandwidth is None:
            K = self.select_bandwidth_andrews(X)
        else:
            K = self.bandwidth
        
        # Gamma_0: contemporaneous covariance
        Gamma_0 = (X.T @ Y) / T
        
        # Sum of weighted autocovariances
        Omega = Gamma_0.copy()
        
        for k in range(1, K + 1):
            # Weight
            w_k = self._kernel_func(k / K)
            
            # Gamma_k = E[X_t Y'_{t-k}]
            Gamma_k = (X[k:].T @ Y[:-k]) / T
            
            # Gamma_{-k} = E[X_t Y'_{t+k}] = Gamma_k'
            Gamma_minus_k = Gamma_k.T
            
            # Add weighted terms
            Omega += w_k * (Gamma_k + Gamma_minus_k)
        
        return Omega
    
    def estimate_one_sided_long_run_covariance(
        self,
        X: np.ndarray,
        Y: np.ndarray
    ) -> np.ndarray:
        """
        Estimate one-sided long-run covariance Δ_XY = Σ_{k=0}^{∞} E[X_t Y'_{t-k}].
        
        This is used for the serial correlation correction term.
        
        Parameters
        ----------
        X : np.ndarray
            (T x n_x) time series
        Y : np.ndarray
            (T x n_y) time series
        
        Returns
        -------
        Delta : np.ndarray
            (n_x x n_y) one-sided long-run covariance
        """
        X = np.atleast_2d(X)
        Y = np.atleast_2d(Y)
        
        if X.shape[0] != Y.shape[0]:
            raise ValueError("X and Y must have same length")
        
        T = X.shape[0]
        
        # Select bandwidth
        if self.bandwidth is None:
            K = self.select_bandwidth_andrews(X)
        else:
            K = self.bandwidth
        
        # Gamma_0
        Gamma_0 = (X.T @ Y) / T
        Delta = Gamma_0.copy()
        
        # Sum forward autocovariances only
        for k in range(1, K + 1):
            w_k = self._kernel_func(k / K)
            Gamma_k = (X[k:].T @ Y[:-k]) / T
            Delta += w_k * Gamma_k
        
        return Delta
    
    def estimate_spectral_density(
        self,
        X: np.ndarray,
        frequency: float = 0.0
    ) -> np.ndarray:
        """
        Estimate spectral density matrix at given frequency.
        
        S(ω) = (1/2π) Σ_{k=-∞}^{∞} Γ_k exp(-ikω)
        
        Parameters
        ----------
        X : np.ndarray
            Time series data
        frequency : float
            Frequency at which to evaluate (default: 0 for long-run)
        
        Returns
        -------
        S : np.ndarray
            Spectral density matrix at frequency
        """
        X = np.atleast_2d(X)
        T = X.shape[0]
        
        if self.bandwidth is None:
            K = self.select_bandwidth_andrews(X)
        else:
            K = self.bandwidth
        
        # Gamma_0
        Gamma_0 = (X.T @ X) / T
        S = Gamma_0.copy()
        
        for k in range(1, K + 1):
            w_k = self._kernel_func(k / K)
            Gamma_k = (X[k:].T @ X[:-k]) / T
            
            # Add complex exponential weights
            weight = np.exp(-1j * k * frequency)
            S += w_k * (Gamma_k * weight + Gamma_k.T * np.conj(weight))
        
        return S / (2 * np.pi)
    
    def prewhiten(self, X: np.ndarray, ar_order: int = 1) -> np.ndarray:
        """
        Prewhiten data using VAR(ar_order) filter.
        
        Can improve finite-sample properties of kernel estimates.
        
        Parameters
        ----------
        X : np.ndarray
            Data to prewhiten
        ar_order : int
            Order of AR filter
        
        Returns
        -------
        X_white : np.ndarray
            Prewhitened data
        """
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        T, n = X.shape
        
        # Fit VAR(ar_order)
        Y = X[ar_order:]
        X_lags = np.column_stack([X[ar_order-i:-i] for i in range(1, ar_order+1)])
        
        # OLS
        A = np.linalg.lstsq(X_lags, Y, rcond=None)[0]
        
        # Residuals are prewhitened data
        X_white = Y - X_lags @ A
        
        return X_white


def bartlett_weights(lags: int) -> np.ndarray:
    """
    Generate Bartlett kernel weights.
    
    Parameters
    ----------
    lags : int
        Maximum lag
    
    Returns
    -------
    weights : np.ndarray
        Bartlett weights for lags 0 to lags
    """
    k = np.arange(lags + 1)
    weights = 1 - k / (lags + 1)
    return weights


def newey_west_covariance(
    X: np.ndarray,
    lags: Optional[int] = None
) -> np.ndarray:
    """
    Compute Newey-West HAC covariance matrix.
    
    Convenience function for Bartlett kernel with automatic lag selection.
    
    Parameters
    ----------
    X : np.ndarray
        (T x k) data matrix
    lags : int, optional
        Number of lags. If None, uses floor(4(T/100)^(2/9))
    
    Returns
    -------
    Omega : np.ndarray
        HAC covariance matrix
    """
    X = np.atleast_2d(X)
    T = X.shape[0]
    
    if lags is None:
        lags = int(np.floor(4 * (T / 100)**(2/9)))
    
    estimator = KernelCovarianceEstimator(kernel='bartlett', bandwidth=lags)
    return estimator.estimate_long_run_covariance(X)
