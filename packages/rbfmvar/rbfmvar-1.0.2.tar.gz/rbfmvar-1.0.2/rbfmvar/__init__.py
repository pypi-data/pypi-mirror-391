"""
RBFM-VAR: Residual-Based Fully Modified Vector Autoregression
==============================================================

A Python package for estimating and testing Vector Autoregression models
with unknown mixtures of I(0), I(1), and I(2) components.

Based on:
Chang, Y. (2000). "Vector Autoregressions with Unknown Mixtures of I(0), I(1), 
and I(2) Components." Econometric Theory, 16(6), 905-926.

The RBFM-VAR procedure:
- Does not require prior knowledge about unit roots
- Handles mixtures of I(0), I(1), and I(2) processes
- Allows for various forms of cointegration
- Provides optimal inference without pretesting
- Modified Wald tests with better finite-sample properties

Author: Implementation by Claude for Dr. Merwan Roudane
Email: merwanroudane920@gmail.com  
GitHub: https://github.com/merwanroudane/RBFMVAR
"""

__version__ = '1.0.2'
__author__ = 'Dr. Merwan Roudane'
__email__ = 'merwanroudane920@gmail.com'

# Main estimator
from .rbfmvar_estimator import rbfm_var, format_results

# Hypothesis tests
from .hypothesis_tests import (
    RBFMWaldTest,
    StandardWaldTest,
    format_test_results
)

# Kernel estimators
from .kernel_estimators import (
    KernelCovarianceEstimator,
    newey_west_covariance,
    bartlett_weights
)

# Utility functions
from .utils import (
    construct_var_matrices,
    lag_matrix,
    difference,
    select_lag_order,
    impulse_response,
    forecast_error_variance_decomposition,
    portmanteau_test,
    arch_test,
    stability_check,
    plot_residual_diagnostics,
    format_summary_table
)

__all__ = [
    # Main classes
    'RBFMVAREstimator',
    'RBFMWaldTest',
    'StandardWaldTest',
    'KernelCovarianceEstimator',
    
    # Functions
    'construct_var_matrices',
    'lag_matrix',
    'difference',
    'select_lag_order',
    'impulse_response',
    'forecast_error_variance_decomposition',
    'portmanteau_test',
    'arch_test',
    'stability_check',
    'plot_residual_diagnostics',
    'format_test_results',
    'format_summary_table',
    'newey_west_covariance',
    'bartlett_weights',
]


def get_citation():
    """Return citation information for the paper."""
    citation = """
    If you use this package, please cite the original paper:
    
    Chang, Y. (2000). Vector Autoregressions with Unknown Mixtures of I(0), I(1),  
    and I(2) Components. Econometric Theory, 16(6), 905-926.
    https://doi.org/10.1017/S0266466600166046
    
    BibTeX:
    @article{chang2000vector,
      title={Vector Autoregressions with Unknown Mixtures of I(0), I(1), and I(2) Components},
      author={Chang, Yoosoon},
      journal={Econometric Theory},
      volume={16},
      number={6},
      pages={905--926},
      year={2000},
      publisher={Cambridge University Press}
    }
    """
    return citation


def quick_start_example():
    """Print a quick start example."""
    example = """
    Quick Start Example:
    ====================
    
    import numpy as np
    from rbfmvar import RBFMVAREstimator, RBFMWaldTest
    
    # Generate or load your data
    # data should be a (T x n) numpy array
    data = np.random.randn(200, 3)
    
    # Fit RBFM-VAR model
    model = RBFMVAREstimator(data, p=2)
    model.fit()
    
    # View summary
    summary = model.summary()
    print(format_summary_table(summary))
    
    # Test Granger causality
    test = RBFMWaldTest(model)
    result = test.test_granger_causality(
        causing_vars=[0],
        caused_vars=[1, 2]
    )
    print(format_test_results(result))
    
    # Generate forecasts
    forecasts = model.predict(steps=10)
    print(f"Forecasts shape: {forecasts.shape}")
    
    For more examples, see the examples/ directory.
    """
    return example


# Print welcome message on import
def _welcome_message():
    """Print welcome message."""
    msg = f"""
    {'='*70}
    RBFM-VAR v{__version__}
    Residual-Based Fully Modified Vector Autoregression
    
    Implementation of Chang (2000) for mixtures of I(0), I(1), I(2) processes
    Author: {__author__}
    GitHub: https://github.com/merwanroudane/RBFMVAR
    {'='*70}
    
    For citation info: rbfmvar.get_citation()
    For quick start: rbfmvar.quick_start_example()
    """
    return msg


# Optionally print on import (comment out if not desired)
# print(_welcome_message())
