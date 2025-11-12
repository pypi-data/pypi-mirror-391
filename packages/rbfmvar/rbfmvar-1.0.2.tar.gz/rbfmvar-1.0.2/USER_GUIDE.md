# RBFM-VAR User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Mathematical Background](#mathematical-background)
6. [Advanced Topics](#advanced-topics)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Introduction

### What is RBFM-VAR?

RBFM-VAR (Residual-Based Fully Modified Vector Autoregression) is an estimation method for VAR models that may contain mixtures of:
- **I(0)** processes: Stationary variables
- **I(1)** processes: Variables with one unit root
- **I(2)** processes: Variables with two unit roots

### Why Use RBFM-VAR?

**Traditional VAR estimation requires:**
1. Testing each variable for unit roots
2. Determining cointegration relationships
3. Specifying the correct error correction form

**RBFM-VAR eliminates these steps** while maintaining optimal asymptotic properties!

### When to Use RBFM-VAR

Use RBFM-VAR when:
- ✅ You're unsure about the order of integration of your variables
- ✅ You want to avoid pretesting for unit roots
- ✅ Your data may contain I(2) processes
- ✅ You need robust inference without extensive model specification
- ✅ You want to test Granger causality in potentially nonstationary systems

## Installation

### Requirements

- Python >= 3.7
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- Pandas >= 1.3.0
- Matplotlib >= 3.3.0 (optional, for plotting)

### Install from GitHub

```bash
git clone https://github.com/merwanroudane/RBFMVAR.git
cd RBFMVAR
pip install -e .
```

### Verify Installation

```python
import rbfmvar
print(rbfmvar.__version__)
print(rbfmvar.get_citation())
```

## Quick Start

### Basic Example

```python
import numpy as np
from rbfmvar import RBFMVAREstimator

# Your data (T x n matrix)
data = np.loadtxt('your_data.csv', delimiter=',')

# Estimate model
model = RBFMVAREstimator(data, p=2)
model.fit()

# View results
summary = model.summary()
print(f"Log-likelihood: {summary['log_likelihood']:.2f}")
print(f"AIC: {summary['AIC']:.2f}")
print(f"BIC: {summary['BIC']:.2f}")
```

### Testing Granger Causality

```python
from rbfmvar import RBFMWaldTest, format_test_results

# Create test object
test = RBFMWaldTest(model)

# Test if variable 0 causes variable 1
result = test.test_granger_causality(
    causing_vars=[0],
    caused_vars=[1]
)

print(format_test_results(result))
```

### Forecasting

```python
# Generate 10-step ahead forecasts
forecasts = model.predict(steps=10)
print(forecasts)
```

## Detailed Usage

### Data Preparation

#### Required Format

Data must be a NumPy array of shape (T, n) where:
- T = number of time periods
- n = number of variables

```python
import numpy as np
import pandas as pd

# From CSV
data = pd.read_csv('data.csv').values

# From pandas DataFrame
df = pd.DataFrame(...)
data = df.values

# From list
data = np.array([[y1_1, y2_1, y3_1],
                 [y1_2, y2_2, y3_2],
                 ...])
```

#### Data Requirements

- Minimum sample size: T > p + 10 (preferably T > 100)
- No missing values (use interpolation or imputation if needed)
- Variables should be in similar scales (optional but recommended)

### Model Specification

#### Choosing Lag Order

**Method 1: Information Criteria**

```python
from rbfmvar import select_lag_order

optimal_p = select_lag_order(
    data,
    max_lag=10,
    criterion='bic'  # 'aic', 'bic', or 'hqic'
)
print(f"Optimal lag order: {optimal_p}")
```

**Method 2: Theoretical Considerations**

- Quarterly data: Try p = 4, 8
- Monthly data: Try p = 12, 24
- Annual data: Try p = 1, 2

#### Kernel Selection

The package supports four kernel functions for long-run covariance estimation:

```python
# Bartlett (Newey-West) - default, good general choice
model = RBFMVAREstimator(data, p=2, kernel='bartlett')

# Parzen - higher order, better bias properties
model = RBFMVAREstimator(data, p=2, kernel='parzen')

# Quadratic Spectral - optimal rate (Andrews 1991)
model = RBFMVAREstimator(data, p=2, kernel='quadratic_spectral')

# Tukey-Hanning - popular in spectral analysis
model = RBFMVAREstimator(data, p=2, kernel='tukey_hanning')
```

#### Bandwidth Selection

```python
# Automatic (recommended)
model = RBFMVAREstimator(data, p=2, bandwidth=None)

# Manual
model = RBFMVAREstimator(data, p=2, bandwidth=5)
```

### Estimation

```python
# Fit the model
model.fit()

# Access estimates
Phi_hat = model.Phi_plus  # Stationary component
A_hat = model.A_plus      # Nonstationary component
residuals = model.residuals
Sigma_epsilon = model.Sigma_epsilon
```

### Hypothesis Testing

#### Granger Causality

```python
test = RBFMWaldTest(model)

# Single causing variable
result = test.test_granger_causality(
    causing_vars=[0],
    caused_vars=[1, 2]
)

# Multiple causing variables
result = test.test_granger_causality(
    causing_vars=[0, 1],
    caused_vars=[2]
)
```

#### Individual Coefficient Tests

```python
# Test if coefficient equals zero
result = test.test_coefficient_restriction(
    equation_idx=0,    # Which equation
    variable_idx=1,    # Which variable
    lag=1,             # Which lag
    value=0.0,         # H0 value
    alpha=0.05
)
```

#### Joint Significance

```python
# Test if all coefficients of certain variables are zero
result = test.test_joint_significance(
    equation_indices=[0, 1],
    variable_indices=[2],
    alpha=0.05
)
```

### Diagnostics

#### Residual Autocorrelation

```python
from rbfmvar import portmanteau_test

Q_stat, p_value = portmanteau_test(model.residuals, lags=10)
print(f"Portmanteau Q: {Q_stat:.2f} (p={p_value:.4f})")
```

#### ARCH Effects

```python
from rbfmvar import arch_test

LM_stat, p_value = arch_test(model.residuals, lags=4)
print(f"ARCH LM: {LM_stat:.2f} (p={p_value:.4f})")
```

#### Stability

```python
from rbfmvar import stability_check

is_stable, eigenvalues = stability_check(
    model.Phi_plus,
    model.A_plus,
    model.p
)
print(f"Model stable: {is_stable}")
print(f"Max eigenvalue: {np.max(np.abs(eigenvalues)):.4f}")
```

#### Visual Diagnostics

```python
from rbfmvar import plot_residual_diagnostics

plot_residual_diagnostics(
    model.residuals,
    variable_names=['GDP', 'Consumption', 'Investment']
)
```

### Forecasting

#### Point Forecasts

```python
# h-step ahead forecasts
h = 10
forecasts = model.predict(steps=h)

# forecasts is (h x n) array
print(f"Shape: {forecasts.shape}")
```

#### Iterative Forecasting

```python
# Forecast one step at a time
current_data = data.copy()
forecast_path = []

for step in range(10):
    # Refit model with updated data (optional)
    model_updated = RBFMVAREstimator(current_data, p=2)
    model_updated.fit()
    
    # Forecast next period
    next_value = model_updated.predict(steps=1)
    forecast_path.append(next_value[0])
    
    # Update data
    current_data = np.vstack([current_data, next_value])

forecasts_iterative = np.array(forecast_path)
```

## Mathematical Background

### The Model

The VAR(p) model is:

$$y_t = A_1 y_{t-1} + \cdots + A_p y_{t-p} + \varepsilon_t$$

where $y_t$ is an n-dimensional vector and $\varepsilon_t \sim \text{i.i.d.}(0, \Sigma_{\varepsilon\varepsilon})$.

### RBFM-VAR Reformulation

The model is rewritten as:

$$y_t = \Phi z_t + A w_t + \varepsilon_t$$

where:
- $z_t = (\Delta^2 y_{t-1}, \ldots, \Delta^2 y_{t-p+2})'$ (known stationary)
- $w_t = (\Delta y_{t-1}, y_{t-1})'$ (potentially nonstationary)

### Correction Terms

The RBFM-VAR estimator is:

$$\hat{F}^+ = (\hat{\Phi}^+, \hat{A}^+) = (Y^+' Z, Y^+' W + T\hat{\Delta}^+)(X'X)^{-1}$$

with corrections:

$$Y^+ = Y' - \hat{\Omega}_{\varepsilon\hat{v}} \hat{\Omega}_{\hat{v}\hat{v}}^{-1} \hat{V}'$$

$$\hat{\Delta}^+ = \hat{\Omega}_{\varepsilon\hat{v}} \hat{\Omega}_{\hat{v}\hat{v}}^{-1} \hat{\Delta}_{\hat{v}\Delta w}$$

where $\hat{v}_t$ is a process that isolates the I(1) and I(2) components.

### Asymptotic Theory

**For stationary components** (Theorem 1a):

$$\sqrt{T}(\hat{\Phi}^+ - \Phi) \xrightarrow{d} N(0, \Sigma_{\varepsilon\varepsilon} \otimes \Sigma_{x_1 x_1}^{-1})$$

**For nonstationary components** (Theorem 1b):

$$(\hat{F}^+ - F)G^b D_T \xrightarrow{d} \int_0^1 dB_{\varepsilon.2} \bar{B}_b' (\int_0^1 \bar{B}_b \bar{B}_b')^{-1}$$

This is mixed normal distribution!

### Modified Wald Test

For linear restrictions $R_1 vec(F) R_2 = r$:

$$W_F^+ \xrightarrow{d} \chi^2_{q_1(q_\Phi + q_{A_1})} + \sum_{i=1}^{q_1} d_i \chi^2_{q_{A_b}(i)}$$

where $0 \leq d_i \leq 1$ are data-dependent weights.

**Important:** The distribution is bounded above by $\chi^2$ with known df!

## Advanced Topics

### Custom Linear Restrictions

You can test arbitrary linear restrictions:

```python
# Construct R1 (selects equations) and R2 (selects variables)
n = 3  # number of variables
R1 = np.array([[1, 0, 0]])  # Test restrictions on equation 1
R2 = np.eye(6)[:, [0, 1]]   # Select first two regressors
r = np.zeros((1, 2))         # H0: coefficients = 0

test = RBFMWaldTest(model)
result = test.test_linear_restriction(R1, R2, r)
```

### Comparing with OLS-VAR

```python
from rbfmvar.hypothesis_tests import StandardWaldTest

# RBFM-VAR (recommended)
test_rbfm = RBFMWaldTest(model)
result_rbfm = test_rbfm.test_granger_causality([0], [1])

# Standard Wald (for comparison)
test_std = StandardWaldTest(model)
# ... construct R matrix manually ...

print(f"RBFM-VAR statistic: {result_rbfm['statistic']:.2f}")
print(f"Standard Wald statistic: {result_std['statistic']:.2f}")
```

### Handling I(2) Processes

RBFM-VAR automatically handles I(2) processes! No special treatment needed.

Example: Nominal exchange rates, price levels, or integrated volatility often exhibit I(2) behavior.

```python
# Even if your data contains I(2) variables, just use:
model = RBFMVAREstimator(data, p=2)
model.fit()
# That's it!
```

### Monte Carlo Studies

See `examples/simulation_study.py` for comprehensive Monte Carlo simulations that:
- Replicate Chang (2000) results
- Compare RBFM-VAR vs OLS-VAR
- Show finite-sample properties

```bash
python examples/simulation_study.py --case A --T 150 --n_sim 1000
```

## Troubleshooting

### Common Issues

#### 1. Singular Matrix Errors

**Problem:** `LinAlgError: Singular matrix`

**Solutions:**
- Check for perfect multicollinearity in data
- Reduce lag order
- Ensure sufficient observations (T > np)
- Check for constant variables

```python
# Check for constant variables
np.std(data, axis=0)  # Should all be > 0

# Check condition number
cond_number = np.linalg.cond(data)
print(f"Condition number: {cond_number}")
# Should be < 10^10
```

#### 2. Numerical Instability

**Problem:** Very large or NaN estimates

**Solutions:**
- Standardize variables before estimation
- Use more robust kernel (try 'bartlett')
- Reduce bandwidth
- Check for outliers

```python
# Standardize data
from scipy import stats
data_standardized = stats.zscore(data, axis=0)

model = RBFMVAREstimator(data_standardized, p=2)
```

#### 3. Poor Test Performance

**Problem:** Tests always reject or never reject

**Solutions:**
- Increase sample size (T > 100 recommended)
- Check model specification (lag order)
- Verify data quality
- Consider structural breaks

### Diagnostic Checklist

Before trusting results, check:

- [ ] Residuals have no significant autocorrelation (Portmanteau test)
- [ ] No ARCH effects (ARCH test)
- [ ] Model is stable (stability check)
- [ ] Residuals approximately normal (Q-Q plots)
- [ ] No obvious outliers in residuals

## FAQ

### Q: How do I know if my variables are I(0), I(1), or I(2)?

**A:** You don't need to know! That's the whole point of RBFM-VAR. The method works regardless of the integration order.

### Q: Should I difference my data before using RBFM-VAR?

**A:** No! Use the levels. RBFM-VAR handles differencing internally.

### Q: Can RBFM-VAR detect cointegration?

**A:** RBFM-VAR doesn't explicitly test for cointegration, but it automatically accounts for it in estimation. For explicit cointegration tests, use Johansen's method separately.

### Q: What if I have deterministic trends?

**A:** Include them as exogenous variables or detrend first. RBFM-VAR currently assumes no deterministic trends.

### Q: How large should my sample be?

**A:** Minimum T > p + 10, but T > 100 is recommended for reliable inference. Asymptotic theory works best with large T.

### Q: Can I use RBFM-VAR with panel data?

**A:** This package is for single time series. For panel VAR, consider separate methods.

### Q: What's the computational complexity?

**A:** Estimation is O(T × n² × p²) where T = sample size, n = variables, p = lags. Usually very fast (seconds for n=10, p=5, T=1000).

### Q: How does RBFM-VAR compare to other methods?

**A:** 
- **vs OLS-VAR:** Better inference, handles nonstationarity
- **vs Johansen:** No need to specify cointegration rank
- **vs VECM:** Works with unknown cointegration
- **vs FM-OLS:** Extends to VAR systems and I(2)

### Q: Can I use this for high-frequency data?

**A:** Yes, but be mindful of:
- Increased computational cost
- Potential for microstructure noise
- May need larger bandwidth parameters

### Q: What if I have measurement error?

**A:** RBFM-VAR assumes classical errors. With measurement error, results may be biased. Consider instrumental variables or EIV methods.

### Q: How do I cite this package?

```python
import rbfmvar
print(rbfmvar.get_citation())
```

---

For more questions, please:
- Check the examples in `examples/`
- Open an issue on GitHub
- Email: merwanroudane920@gmail.com

Happy analyzing! 📊
