"""
Simple Practical Example: Using RBFM-VAR for Economic Data Analysis
===================================================================

This example demonstrates how to use RBFM-VAR for analyzing economic time series
that may contain unit roots and cointegration.

Example: GDP, Consumption, and Investment Analysis

Author: Dr. Merwan Roudane
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('..')

from rbfmvar import (
    rbfm_var,
    RBFMWaldTest,
    select_lag_order,
    format_summary_table,
    format_results,
    portmanteau_test,
    arch_test
)


def generate_example_data(T=200, seed=42):
    """
    Generate synthetic economic data for demonstration.
    
    Simulates GDP, Consumption, and Investment with realistic properties:
    - All variables are I(1)  
    - GDP and Consumption are cointegrated
    - Bidirectional causality between variables
    """
    np.random.seed(seed)
    
    # Error term covariance (correlated shocks)
    Sigma = np.array([
        [1.0, 0.6, 0.4],  # GDP shocks
        [0.6, 0.8, 0.3],  # Consumption shocks
        [0.4, 0.3, 1.2]   # Investment shocks
    ])
    
    # Generate innovations
    innovations = np.random.multivariate_normal([0, 0, 0], Sigma, size=T+100)
    
    # Initialize
    gdp = np.zeros(T+100)
    consumption = np.zeros(T+100)
    investment = np.zeros(T+100)
    
    # Generate I(1) processes with cointegration
    for t in range(1, T+100):
        # GDP growth depends on past consumption and investment
        gdp_growth = 0.7 * (consumption[t-1] - gdp[t-1]) + 0.3 * investment[t-1] + innovations[t, 0]
        gdp[t] = gdp[t-1] + gdp_growth
        
        # Consumption tracks GDP (cointegration)
        consumption_growth = 0.8 * gdp[t] + innovations[t, 1]
        consumption[t] = consumption_growth
        
        # Investment is more volatile
        investment_growth = 0.5 * gdp[t-1] + innovations[t, 2]
        investment[t] = investment[t-1] + investment_growth
    
    # Remove burn-in and create DataFrame
    data = pd.DataFrame({
        'GDP': gdp[100:],
        'Consumption': consumption[100:],
        'Investment': investment[100:]
    })
    
    return data


def main():
    """
    Main analysis workflow.
    """
    print("\n" + "="*80)
    print("RBFM-VAR EXAMPLE: ECONOMIC DATA ANALYSIS")
    print("="*80 + "\n")
    
    # Step 1: Generate/Load Data
    print("Step 1: Loading Data")
    print("-" * 80)
    data_df = generate_example_data(T=200)
    data = data_df.values
    variable_names = data_df.columns.tolist()
    
    print(f"Data shape: {data.shape}")
    print(f"Variables: {', '.join(variable_names)}")
    print(f"\nData summary:")
    print(data_df.describe())
    
    # Step 2: Select Lag Order
    print("\n\nStep 2: Selecting Optimal Lag Order")
    print("-" * 80)
    optimal_p = select_lag_order(data, max_lag=8, criterion='bic')
    print(f"Optimal lag order (BIC): p = {optimal_p}")
    
    # Step 3: Estimate RBFM-VAR Model
    print("\n\nStep 3: Estimating RBFM-VAR Model")
    print("-" * 80)
    model = RBFMVAREstimator(data, p=optimal_p, kernel='bartlett')
    model.fit()
    
    summary = model.summary()
    print(format_summary_table(summary))
    
    print("\nEstimated Coefficient Matrices:")
    print("\nΦ (Stationary Component):")
    print(model.Phi_plus)
    print("\nA (Nonstationary Component):")
    print(model.A_plus)
    
    # Step 4: Diagnostic Tests
    print("\n\nStep 4: Diagnostic Tests")
    print("-" * 80)
    
    # Portmanteau test for autocorrelation
    Q_stat, Q_pval = portmanteau_test(model.residuals, lags=10)
    print(f"Portmanteau Test (Q-statistic): {Q_stat:.4f}")
    print(f"P-value: {Q_pval:.4f}")
    if Q_pval > 0.05:
        print("✓ No significant residual autocorrelation detected")
    else:
        print("✗ Significant residual autocorrelation detected")
    
    # ARCH test
    arch_stat, arch_pval = arch_test(model.residuals, lags=4)
    print(f"\nARCH Test (LM-statistic): {arch_stat:.4f}")
    print(f"P-value: {arch_pval:.4f}")
    if arch_pval > 0.05:
        print("✓ No significant ARCH effects detected")
    else:
        print("✗ Significant ARCH effects detected")
    
    # Step 5: Granger Causality Tests
    print("\n\nStep 5: Granger Causality Tests")
    print("-" * 80)
    
    test = RBFMWaldTest(model)
    
    # Test each pairwise causality
    n = len(variable_names)
    causality_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                result = test.test_granger_causality(
                    causing_vars=[j],
                    caused_vars=[i],
                    alpha=0.05
                )
                causality_matrix[i, j] = 1 if result['reject'] else 0
                
                print(f"\nTest: {variable_names[j]} → {variable_names[i]}")
                print(f"Statistic: {result['statistic']:.4f}, P-value: {result['p_value']:.4f}")
                if result['reject']:
                    print(f"✓ {variable_names[j]} Granger-causes {variable_names[i]}")
                else:
                    print(f"✗ No Granger causality detected")
    
    # Display causality matrix
    print("\n\nGranger Causality Matrix:")
    print("(1 = causes, 0 = does not cause)")
    causality_df = pd.DataFrame(
        causality_matrix,
        index=variable_names,
        columns=variable_names
    )
    print(causality_df)
    
    # Step 6: Forecasting
    print("\n\nStep 6: Generating Forecasts")
    print("-" * 80)
    
    forecast_horizon = 10
    forecasts = model.predict(steps=forecast_horizon)
    
    forecast_df = pd.DataFrame(
        forecasts,
        columns=variable_names
    )
    forecast_df.index = range(len(data), len(data) + forecast_horizon)
    forecast_df.index.name = 'Period'
    
    print(f"\n{forecast_horizon}-step ahead forecasts:")
    print(forecast_df)
    
    # Step 7: Visualization
    print("\n\nStep 7: Creating Visualizations")
    print("-" * 80)
    
    try:
        fig, axes = plt.subplots(n, 1, figsize=(12, 4*n))
        
        if n == 1:
            axes = [axes]
        
        for i, (ax, var_name) in enumerate(zip(axes, variable_names)):
            # Plot actual data
            ax.plot(range(len(data)), data[:, i], 
                   label='Actual', color='blue', linewidth=1.5)
            
            # Plot forecasts
            forecast_periods = range(len(data), len(data) + forecast_horizon)
            ax.plot(forecast_periods, forecasts[:, i],
                   label='Forecast', color='red', linestyle='--', linewidth=2)
            
            # Formatting
            ax.set_title(f'{var_name}: Actual vs Forecast', fontsize=12, fontweight='bold')
            ax.set_xlabel('Period')
            ax.set_ylabel(var_name)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            # Highlight forecast region
            ax.axvspan(len(data), len(data) + forecast_horizon, 
                      alpha=0.1, color='red')
        
        plt.tight_layout()
        plt.savefig('rbfmvar_forecasts.png', dpi=300, bbox_inches='tight')
        print("✓ Forecast plot saved as 'rbfmvar_forecasts.png'")
        plt.show()
        
    except Exception as e:
        print(f"Could not create plots: {e}")
    
    # Step 8: Save Results
    print("\n\nStep 8: Saving Results")
    print("-" * 80)
    
    # Save forecasts
    forecast_df.to_csv('forecasts.csv')
    print("✓ Forecasts saved to 'forecasts.csv'")
    
    # Save residuals
    residuals_df = pd.DataFrame(
        model.residuals,
        columns=variable_names
    )
    residuals_df.to_csv('residuals.csv', index=False)
    print("✓ Residuals saved to 'residuals.csv'")
    
    # Save summary
    with open('model_summary.txt', 'w') as f:
        f.write(format_summary_table(summary))
        f.write("\n\nCoefficient Estimates:\n")
        f.write("\nΦ (Stationary Component):\n")
        f.write(str(model.Phi_plus))
        f.write("\n\nA (Nonstationary Component):\n")
        f.write(str(model.A_plus))
    print("✓ Model summary saved to 'model_summary.txt'")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
