"""
Hypothesis Testing for RBFM-VAR Models
======================================

Implements modified Wald tests for RBFM-VAR as in Chang (2000), Theorem 2.

The modified Wald test has better properties than standard Wald tests when
testing restrictions that involve nonstationary coefficients.

Author: Implementation by Claude for Dr. Merwan Roudane
"""

import numpy as np
from scipy import stats
from scipy.linalg import sqrtm
from typing import Tuple, Dict, Optional
import warnings


class RBFMWaldTest:
    """
    Modified Wald test for RBFM-VAR models (Theorem 2, Chang 2000).
    
    The modified Wald test has asymptotic distribution that is a weighted sum
    of independent chi-square variates when testing restrictions on 
    nonstationary coefficients.
    
    Parameters
    ----------
    estimator : RBFMVAREstimator
        Fitted RBFM-VAR estimator
    """
    
    def __init__(self, estimator):
        """Initialize Wald test."""
        self.estimator = estimator
        
        if estimator.Phi_plus is None or estimator.A_plus is None:
            raise ValueError("Estimator must be fitted before testing")
    
    def test_granger_causality(
        self,
        causing_vars: np.ndarray,
        caused_vars: np.ndarray,
        alpha: float = 0.05
    ) -> Dict:
        """
        Test Granger causality from causing_vars to caused_vars.
        
        H0: causing_vars does not Granger-cause caused_vars
        
        This tests whether lagged values of causing_vars help predict caused_vars.
        
        Parameters
        ----------
        causing_vars : np.ndarray
            Indices of potentially causing variables
        caused_vars : np.ndarray
            Indices of caused variables
        alpha : float
            Significance level
        
        Returns
        -------
        result : dict
            Test results including statistic, p-value, and decision
        """
        causing_vars = np.atleast_1d(causing_vars)
        caused_vars = np.atleast_1d(caused_vars)
        
        # Construct restriction matrices
        R1, R2, r = self._construct_causality_restrictions(
            causing_vars, caused_vars
        )
        
        # Perform test
        return self.test_linear_restriction(R1, R2, r, alpha=alpha)
    
    def _construct_causality_restrictions(
        self,
        causing_vars: np.ndarray,
        caused_vars: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Construct restriction matrices for Granger causality test.
        
        The null hypothesis is that coefficients of causing_vars in equations
        for caused_vars are zero.
        
        Returns
        -------
        R1 : np.ndarray
            Restriction matrix for equations
        R2 : np.ndarray  
            Restriction matrix for variables
        r : np.ndarray
            Restriction vector (zeros)
        """
        n = self.estimator.n
        p = self.estimator.p
        
        # Number of restrictions
        q1 = len(caused_vars)  # Number of equations
        q2 = len(causing_vars) * p  # Number of lags of causing variables
        
        # R1: Select equations (rows of coefficient matrix)
        R1 = np.zeros((q1, n))
        for i, eq in enumerate(caused_vars):
            R1[i, eq] = 1
        
        # R2: Select variables (columns of coefficient matrix)  
        # Need to select lagged causing variables from both Φ and A
        
        # Total number of regressors
        n_Z = n * (p - 2) if p > 2 else 0  # Second differences
        n_W = 2 * n  # First differences and levels
        total_regressors = n_Z + n_W
        
        R2 = np.zeros((total_regressors, q2))
        
        col_idx = 0
        for var in causing_vars:
            # In Φ: Δ²y_{var,t-1}, ..., Δ²y_{var,t-p+2}
            for lag in range(p - 2):
                if n_Z > 0:
                    R2[var + lag * n, col_idx] = 1
                    col_idx += 1
            
            # In A: Δy_{var,t-1}
            R2[n_Z + var, col_idx] = 1
            col_idx += 1
            
            # In A: y_{var,t-1}
            R2[n_Z + n + var, col_idx] = 1
            col_idx += 1
        
        # Restriction vector (all zeros for causality)
        r = np.zeros((q1, q2))
        
        return R1, R2, r
    
    def test_linear_restriction(
        self,
        R1: np.ndarray,
        R2: np.ndarray,
        r: np.ndarray,
        alpha: float = 0.05
    ) -> Dict:
        """
        Test linear restriction R1 * F * R2 = r using modified Wald test.
        
        Implements Theorem 2 from Chang (2000).
        
        Parameters
        ----------
        R1 : np.ndarray
            (q1 x n) restriction matrix for equations
        R2 : np.ndarray
            (total_regressors x q2) restriction matrix for regressors
        r : np.ndarray
            (q1 x q2) restriction vector
        alpha : float
            Significance level
        
        Returns
        -------
        result : dict
            Contains:
            - 'statistic': test statistic
            - 'df': degrees of freedom  
            - 'critical_value': critical value
            - 'p_value': approximate p-value
            - 'reject': whether to reject null
            - 'test_type': 'modified_wald'
        """
        # Stack Φ and A into F = [Φ, A]
        F = np.hstack([self.estimator.Phi_plus, self.estimator.A_plus])
        
        # Compute restricted coefficients: R1 * F * R2 - r
        restricted = R1 @ F @ R2 - r
        
        # Get covariance matrix components
        Sigma_eps = self.estimator.Sigma_epsilon
        
        # Construct X'X for weighting
        Z, W, Y = self.estimator._construct_regression_matrices()
        X = np.hstack([Z, W])
        XtX = X.T @ X
        T = len(Y)
        
        # Weight matrix: R2' * (X'X)/T * R2
        R2_XtX_R2 = R2.T @ (XtX / T) @ R2
        
        try:
            R2_XtX_R2_inv = np.linalg.inv(R2_XtX_R2)
        except np.linalg.LinAlgError:
            warnings.warn("R2'(X'X)R2 is singular, using pseudo-inverse")
            R2_XtX_R2_inv = np.linalg.pinv(R2_XtX_R2)
        
        # Weight matrix: R1 * Sigma_eps * R1'
        R1_Sigma_R1 = R1 @ Sigma_eps @ R1.T
        
        try:
            R1_Sigma_R1_inv = np.linalg.inv(R1_Sigma_R1)
        except np.linalg.LinAlgError:
            warnings.warn("R1 * Sigma * R1' is singular, using pseudo-inverse")
            R1_Sigma_R1_inv = np.linalg.pinv(R1_Sigma_R1)
        
        # Modified Wald statistic (equation 20)
        # W_F^+ = T * tr((R1*Sigma*R1')^{-1} * restricted * (R2'(X'X)R2)^{-1} * restricted')
        W_stat = T * np.trace(
            R1_Sigma_R1_inv @ restricted @ R2_XtX_R2_inv @ restricted.T
        )
        
        # Degrees of freedom
        q1 = R1.shape[0]
        q2 = R2.shape[1]
        df = q1 * q2
        
        # Conservative test using chi-square
        # The true limit distribution is bounded above by chi-square(df)
        critical_value = stats.chi2.ppf(1 - alpha, df)
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        reject = W_stat > critical_value
        
        return {
            'statistic': W_stat,
            'df': df,
            'critical_value': critical_value,
            'p_value': p_value,
            'reject': reject,
            'significance_level': alpha,
            'test_type': 'modified_wald',
            'note': 'Using conservative chi-square critical values (Theorem 2, Chang 2000)'
        }
    
    def test_coefficient_restriction(
        self,
        equation_idx: int,
        variable_idx: int,
        lag: int,
        value: float = 0.0,
        alpha: float = 0.05
    ) -> Dict:
        """
        Test restriction on individual coefficient.
        
        H0: coefficient of variable_idx at lag in equation_idx equals value
        
        Parameters
        ----------
        equation_idx : int
            Index of equation (0 to n-1)
        variable_idx : int
            Index of variable (0 to n-1)
        lag : int
            Lag number (1 to p)
        value : float
            Null hypothesis value
        alpha : float
            Significance level
        
        Returns
        -------
        result : dict
            Test results
        """
        n = self.estimator.n
        
        # Construct R1: select equation
        R1 = np.zeros((1, n))
        R1[0, equation_idx] = 1
        
        # Construct R2: select variable at lag
        # This depends on whether lag corresponds to Φ or A
        p = self.estimator.p
        n_Z = n * (p - 2) if p > 2 else 0
        n_W = 2 * n
        total_regressors = n_Z + n_W
        
        R2 = np.zeros((total_regressors, 1))
        
        if lag <= p - 2:
            # In Φ (second differences)
            R2[variable_idx + (lag - 1) * n, 0] = 1
        elif lag == p - 1:
            # In A (first difference)
            R2[n_Z + variable_idx, 0] = 1
        else:
            # In A (level)
            R2[n_Z + n + variable_idx, 0] = 1
        
        # Restriction value
        r = np.array([[value]])
        
        return self.test_linear_restriction(R1, R2, r, alpha=alpha)
    
    def test_all_lags_zero(
        self,
        equation_idx: int,
        variable_idx: int,
        alpha: float = 0.05
    ) -> Dict:
        """
        Test if all lags of a variable are zero in an equation.
        
        H0: All coefficients of variable_idx in equation_idx are zero
        
        Parameters
        ----------
        equation_idx : int
            Index of equation
        variable_idx : int
            Index of variable  
        alpha : float
            Significance level
        
        Returns
        -------
        result : dict
            Test results
        """
        # This is equivalent to Granger non-causality from variable_idx to equation_idx
        return self.test_granger_causality(
            causing_vars=np.array([variable_idx]),
            caused_vars=np.array([equation_idx]),
            alpha=alpha
        )
    
    def test_joint_significance(
        self,
        equation_indices: np.ndarray,
        variable_indices: np.ndarray,
        alpha: float = 0.05
    ) -> Dict:
        """
        Test joint significance of specified variables in specified equations.
        
        H0: All specified coefficients are zero
        
        Parameters
        ----------
        equation_indices : np.ndarray
            Indices of equations to test
        variable_indices : np.ndarray
            Indices of variables to test
        alpha : float
            Significance level
        
        Returns
        -------
        result : dict
            Test results
        """
        equation_indices = np.atleast_1d(equation_indices)
        variable_indices = np.atleast_1d(variable_indices)
        
        n = self.estimator.n
        p = self.estimator.p
        
        # R1: select equations
        q1 = len(equation_indices)
        R1 = np.zeros((q1, n))
        for i, eq in enumerate(equation_indices):
            R1[i, eq] = 1
        
        # R2: select all lags of variables
        n_Z = n * (p - 2) if p > 2 else 0
        n_W = 2 * n
        total_regressors = n_Z + n_W
        
        q2 = len(variable_indices) * p
        R2 = np.zeros((total_regressors, q2))
        
        col_idx = 0
        for var in variable_indices:
            # All lags in Φ
            for lag in range(p - 2):
                if n_Z > 0:
                    R2[var + lag * n, col_idx] = 1
                    col_idx += 1
            
            # First difference in A
            R2[n_Z + var, col_idx] = 1
            col_idx += 1
            
            # Level in A  
            R2[n_Z + n + var, col_idx] = 1
            col_idx += 1
        
        r = np.zeros((q1, q2))
        
        return self.test_linear_restriction(R1, R2, r, alpha=alpha)


class StandardWaldTest:
    """
    Standard Wald test for comparison (may have size distortions).
    
    This is the traditional Wald test that can have poor properties
    with nonstationary data.
    """
    
    def __init__(self, estimator):
        """Initialize standard Wald test."""
        self.estimator = estimator
    
    def test_linear_restriction(
        self,
        R: np.ndarray,
        r: np.ndarray,
        alpha: float = 0.05
    ) -> Dict:
        """
        Standard Wald test for R * vec(F) = r.
        
        Parameters
        ----------
        R : np.ndarray
            Restriction matrix
        r : np.ndarray
            Restriction vector
        alpha : float
            Significance level
        
        Returns
        -------
        result : dict
            Test results
        """
        # Stack F = [Φ, A]
        F = np.hstack([self.estimator.Phi_plus, self.estimator.A_plus])
        vec_F = F.flatten(order='F')  # Column-major vectorization
        
        # Restriction
        restricted = R @ vec_F - r
        
        # Covariance matrix
        Sigma_eps = self.estimator.Sigma_epsilon
        Z, W, Y = self.estimator._construct_regression_matrices()
        X = np.hstack([Z, W])
        XtX_inv = np.linalg.inv(X.T @ X)
        
        # Variance of vec(F): Sigma_eps ⊗ (X'X)^{-1}
        # For Wald, we need R * Var(vec F) * R'
        cov_matrix = np.kron(Sigma_eps, XtX_inv)
        R_cov_R = R @ cov_matrix @ R.T
        
        try:
            R_cov_R_inv = np.linalg.inv(R_cov_R)
        except np.linalg.LinAlgError:
            R_cov_R_inv = np.linalg.pinv(R_cov_R)
        
        # Wald statistic
        W_stat = restricted.T @ R_cov_R_inv @ restricted
        
        # Chi-square test
        df = len(restricted)
        critical_value = stats.chi2.ppf(1 - alpha, df)
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        return {
            'statistic': W_stat,
            'df': df,
            'critical_value': critical_value,
            'p_value': p_value,
            'reject': W_stat > critical_value,
            'significance_level': alpha,
            'test_type': 'standard_wald',
            'note': 'May have size distortions with nonstationary data'
        }


def format_test_results(result: Dict) -> str:
    """
    Format test results for printing.
    
    Parameters
    ----------
    result : dict
        Test result dictionary
    
    Returns
    -------
    formatted : str
        Formatted test results
    """
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Hypothesis Test Results ({result['test_type']})")
    output.append(f"{'='*60}")
    output.append(f"Test Statistic: {result['statistic']:.4f}")
    output.append(f"Degrees of Freedom: {result['df']}")
    output.append(f"Critical Value ({result['significance_level']:.0%}): {result['critical_value']:.4f}")
    output.append(f"P-value: {result['p_value']:.4f}")
    output.append(f"Decision: {'Reject H0' if result['reject'] else 'Fail to Reject H0'}")
    
    if 'note' in result:
        output.append(f"\nNote: {result['note']}")
    
    output.append(f"{'='*60}\n")
    
    return '\n'.join(output)
