"""
Installation Test Script for RBFM-VAR Package
=============================================

Run this script after installing the package to verify everything works correctly.

Usage:
    python test_installation.py

Author: Dr. Merwan Roudane
"""

import sys
import numpy as np

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        import rbfmvar
        print(f"✓ rbfmvar imported successfully (version {rbfmvar.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import rbfmvar: {e}")
        return False
    
    try:
        from rbfmvar import (
            RBFMVAREstimator,
            RBFMWaldTest,
            KernelCovarianceEstimator,
            select_lag_order
        )
        print("✓ Main classes imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import classes: {e}")
        return False
    
    return True


def test_basic_estimation():
    """Test basic estimation functionality."""
    print("\nTesting basic estimation...")
    
    try:
        from rbfmvar import RBFMVAREstimator
        
        # Generate simple test data
        np.random.seed(42)
        T = 100
        n = 2
        data = np.cumsum(np.random.randn(T, n), axis=0)
        
        # Estimate model
        model = RBFMVAREstimator(data, p=1, kernel='bartlett')
        model.fit()
        
        # Check results
        assert model.Phi_plus is not None, "Phi_plus not estimated"
        assert model.A_plus is not None, "A_plus not estimated"
        assert model.residuals is not None, "Residuals not computed"
        
        print(f"✓ Basic estimation successful")
        print(f"  - Phi shape: {model.Phi_plus.shape}")
        print(f"  - A shape: {model.A_plus.shape}")
        print(f"  - Residuals shape: {model.residuals.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic estimation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hypothesis_testing():
    """Test hypothesis testing functionality."""
    print("\nTesting hypothesis testing...")
    
    try:
        from rbfmvar import RBFMVAREstimator, RBFMWaldTest
        
        # Generate test data
        np.random.seed(42)
        data = np.cumsum(np.random.randn(100, 2), axis=0)
        
        # Fit model
        model = RBFMVAREstimator(data, p=1)
        model.fit()
        
        # Test Granger causality
        test = RBFMWaldTest(model)
        result = test.test_granger_causality(
            causing_vars=[0],
            caused_vars=[1]
        )
        
        # Check result structure
        assert 'statistic' in result, "Test statistic missing"
        assert 'p_value' in result, "P-value missing"
        assert 'reject' in result, "Decision missing"
        
        print(f"✓ Hypothesis testing successful")
        print(f"  - Test statistic: {result['statistic']:.4f}")
        print(f"  - P-value: {result['p_value']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Hypothesis testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_forecasting():
    """Test forecasting functionality."""
    print("\nTesting forecasting...")
    
    try:
        from rbfmvar import RBFMVAREstimator
        
        # Generate test data
        np.random.seed(42)
        data = np.cumsum(np.random.randn(100, 2), axis=0)
        
        # Fit and forecast
        model = RBFMVAREstimator(data, p=1)
        model.fit()
        
        forecasts = model.predict(steps=5)
        
        # Check forecast shape
        assert forecasts.shape == (5, 2), f"Unexpected forecast shape: {forecasts.shape}"
        assert not np.any(np.isnan(forecasts)), "Forecasts contain NaN"
        
        print(f"✓ Forecasting successful")
        print(f"  - Forecast shape: {forecasts.shape}")
        print(f"  - Forecasts:\n{forecasts}")
        
        return True
        
    except Exception as e:
        print(f"✗ Forecasting failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kernel_estimation():
    """Test kernel covariance estimation."""
    print("\nTesting kernel estimation...")
    
    try:
        from rbfmvar.kernel_estimators import KernelCovarianceEstimator
        
        # Generate test data
        np.random.seed(42)
        X = np.random.randn(100, 2)
        
        # Test each kernel
        kernels = ['bartlett', 'parzen', 'quadratic_spectral', 'tukey_hanning']
        
        for kernel in kernels:
            estimator = KernelCovarianceEstimator(kernel=kernel)
            Omega = estimator.estimate_long_run_covariance(X)
            
            assert Omega.shape == (2, 2), f"Unexpected Omega shape for {kernel}"
            assert np.allclose(Omega, Omega.T), f"Omega not symmetric for {kernel}"
        
        print(f"✓ Kernel estimation successful")
        print(f"  - Tested kernels: {', '.join(kernels)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Kernel estimation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from rbfmvar import (
            construct_var_matrices,
            lag_matrix,
            difference,
            portmanteau_test,
            arch_test
        )
        
        # Generate test data
        np.random.seed(42)
        data = np.random.randn(100, 2)
        
        # Test construct_var_matrices
        Y, X = construct_var_matrices(data, p=2)
        assert Y.shape[0] == X.shape[0], "Y and X rows don't match"
        
        # Test lag_matrix
        lagged = lag_matrix(data, lags=3)
        assert lagged.shape == (100, 6), f"Unexpected lagged shape: {lagged.shape}"
        
        # Test difference
        diff = difference(data, order=1)
        assert diff.shape == (99, 2), f"Unexpected diff shape: {diff.shape}"
        
        # Test portmanteau
        Q, p_val = portmanteau_test(data, lags=5)
        assert isinstance(Q, (int, float)), "Q statistic not numeric"
        assert 0 <= p_val <= 1, "P-value out of range"
        
        # Test ARCH
        LM, p_val = arch_test(data, lags=4)
        assert isinstance(LM, (int, float)), "LM statistic not numeric"
        assert 0 <= p_val <= 1, "P-value out of range"
        
        print(f"✓ Utility functions successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Utility functions failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("RBFM-VAR INSTALLATION TEST")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("Basic Estimation", test_basic_estimation),
        ("Hypothesis Testing", test_hypothesis_testing),
        ("Forecasting", test_forecasting),
        ("Kernel Estimation", test_kernel_estimation),
        ("Utilities", test_utilities)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name} test encountered error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:<25} {status}")
    
    print("-"*70)
    print(f"Total: {passed_count}/{total_count} tests passed")
    print("="*70)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! The package is installed correctly.")
        print("\nNext steps:")
        print("  1. Try running: python examples/simple_example.py")
        print("  2. Read the USER_GUIDE.md for detailed usage")
        print("  3. Check out examples/ directory for more examples")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        print("\nIf you need help:")
        print("  - Check the installation: pip install -e .")
        print("  - Verify dependencies: pip install -r requirements.txt")
        print("  - Open an issue: https://github.com/merwanroudane/RBFMVAR/issues")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
