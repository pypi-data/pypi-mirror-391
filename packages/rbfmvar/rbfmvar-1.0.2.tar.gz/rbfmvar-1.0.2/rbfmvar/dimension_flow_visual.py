"""
RBFM-VAR DIMENSION FLOW - Visual Guide
=======================================

This shows how array dimensions change through the RBFM-VAR estimation
and WHERE the broadcasting error occurs.
"""

def print_dimension_flow(T=50, n=3, p=2):
    """Visualize dimension changes through RBFM-VAR."""
    
    print("\n" + "="*80)
    print("RBFM-VAR DIMENSION FLOW ANALYSIS")
    print("="*80)
    print(f"\nInputs: T={T} observations, n={n} variables, p={p} lags")
    
    print("\n" + "-"*80)
    print("STEP 1: ORIGINAL DATA")
    print("-"*80)
    print(f"  y                    : ({T}, {n})")
    print(f"                         ↓")
    
    print("\n" + "-"*80)
    print("STEP 2: FIRST DIFFERENCE")
    print("-"*80)
    print(f"  Δy = diff(y)         : ({T-1}, {n})    [Lost 1 observation]")
    print(f"                         ↓")
    
    print("\n" + "-"*80)
    print("STEP 3: SECOND DIFFERENCE")
    print("-"*80)
    print(f"  Δ²y = diff(Δy)       : ({T-2}, {n})    [Lost 2 observations total]")
    print(f"                         ↓")
    
    print("\n" + "-"*80)
    print("STEP 4: EFFECTIVE SAMPLE SIZE")
    print("-"*80)
    T_eff = T - 2 - (p - 1)
    print(f"  T_eff = T - 2 - (p-1)")
    print(f"        = {T} - 2 - {p-1}")
    print(f"        = {T_eff}")
    print(f"                         ↓")
    
    print("\n" + "-"*80)
    print("STEP 5: CONSTRUCT REGRESSORS (for times t = p+1, ..., p+T_eff)")
    print("-"*80)
    
    # Δy_{t-1}
    dy_t1_start = p - 1
    dy_t1_end = p - 1 + T_eff
    print(f"\n  A. Δy_{{t-1}}:")
    print(f"     Indices: [{dy_t1_start}:{dy_t1_end}]")
    print(f"     delta_y[{dy_t1_start}:{dy_t1_end}] : ({T_eff}, {n})  ✓")
    
    # y_{t-1}
    print(f"\n  B. y_{{t-1}}:")
    print(f"     Indices: [{dy_t1_start}:{dy_t1_end}]")
    print(f"     y[{dy_t1_start}:{dy_t1_end}]       : ({T_eff}, {n})  ✓")
    
    # W
    print(f"\n  C. W = [Δy_{{t-1}}, y_{{t-1}}]:")
    print(f"     Shape: ({T_eff}, {2*n})  ✓")
    
    # Dependent variable
    y_start = p - 1
    y_end = p - 1 + T_eff
    print(f"\n  D. Dependent: Δ²y_t")
    print(f"     Indices: [{y_start}:{y_end}]")
    print(f"     delta2_y[{y_start}:{y_end}] : ({T_eff}, {n})  ✓")
    
    print(f"\n  → All regression arrays have {T_eff} observations ✓")
    
    print("\n" + "-"*80)
    print("STEP 6: OLS ESTIMATION")
    print("-"*80)
    print(f"  X (regressors)       : ({T_eff}, {2*n})")
    print(f"  y (dependent)        : ({T_eff}, {n})")
    print(f"  β_OLS = (X'X)^(-1)X'y: ({2*n}, {n})")
    print(f"  residuals = y - Xβ   : ({T_eff}, {n})  ✓")
    
    print("\n" + "="*80)
    print("STEP 7: CONSTRUCT v̂_t (⚠️ ERROR-PRONE STEP)")
    print("="*80)
    
    print("\n  v̂_t = (v̂_{1t}, v̂_{2t}) where:")
    print("\n  A. v̂_{1t} = Δ²y_{t-1}")
    print("     " + "-"*60)
    
    v1t_start = max(0, p - 2)
    v1t_end = v1t_start + T_eff
    
    if v1t_start < 0:
        print(f"     ⚠️  WARNING: Calculated start index = {p-2} < 0!")
        print(f"     →  Adjusted to start at 0")
    
    print(f"     Indices: [{v1t_start}:{v1t_end}]")
    
    if v1t_end <= len(range(T-2)):
        print(f"     delta2_y[{v1t_start}:{v1t_end}] : ({T_eff}, {n})  ✓")
    else:
        print(f"     ⚠️  WARNING: End index {v1t_end} > {T-2} (length of Δ²y)")
    
    print("\n  B. v̂_{2t} = Δy_{t-1} - N̂Δy_{t-2}")
    print("     " + "-"*60)
    
    # Δy_{t-1} for v2
    print(f"     For Δy_{{t-1}}:")
    print(f"       Indices: [{dy_t1_start}:{dy_t1_end}]")
    print(f"       delta_y[{dy_t1_start}:{dy_t1_end}] : ({T_eff}, {n})  ✓")
    
    # Δy_{t-2} - THIS IS WHERE THE ERROR OCCURS!
    print(f"\n     For Δy_{{t-2}} (⚠️ CRITICAL):")
    dy_t2_start = p - 2
    dy_t2_end = dy_t2_start + T_eff
    
    print(f"       Calculated start: p - 2 = {p} - 2 = {dy_t2_start}")
    
    if dy_t2_start < 0:
        print(f"       ❌ ERROR: Start index is NEGATIVE!")
        print(f"       delta_y[{dy_t2_start}:{dy_t2_end}] would give:")
        print(f"         - Unexpected results")
        print(f"         - Possibly empty array (0, {n})")
        print(f"         - BROADCASTING ERROR: ({T_eff}, {n}) vs (0, {n})")
        print(f"\n       💡 FIX: Use max(0, {dy_t2_start}) = {max(0, dy_t2_start)}")
        dy_t2_start = max(0, dy_t2_start)
        dy_t2_end = dy_t2_start + T_eff
        print(f"       ✓ Adjusted indices: [{dy_t2_start}:{dy_t2_end}]")
    else:
        print(f"       Indices: [{dy_t2_start}:{dy_t2_end}]")
    
    if dy_t2_end <= len(range(T-1)):
        print(f"       delta_y[{dy_t2_start}:{dy_t2_end}] : ({T_eff}, {n})  ✓")
    else:
        print(f"       ⚠️  End index {dy_t2_end} > {T-1} (length of Δy)")
    
    print("\n     Computing N̂:")
    print(f"       N̂ = lstsq(Δy_{{t-2}}, Δy_{{t-1}})")
    print(f"       N̂ shape: ({n}, {n})")
    
    print("\n     Computing v̂_{2t}:")
    print(f"       v̂_{{2t}} = Δy_{{t-1}} - Δy_{{t-2}} @ N̂")
    print(f"              = ({T_eff},{n}) - ({T_eff},{n}) @ ({n},{n})")
    print(f"              = ({T_eff},{n}) - ({T_eff},{n})")
    print(f"              = ({T_eff},{n})  ✓")
    
    print("\n  C. Combine v̂_{1t} and v̂_{2t}:")
    print(f"     v̂_t = [v̂_{{1t}}, v̂_{{2t}}]")
    print(f"         = [({T_eff},{n}), ({T_eff},{n})]")
    print(f"         = ({T_eff}, {2*n})  ✓")
    
    print("\n" + "="*80)
    print("KEY TAKEAWAYS")
    print("="*80)
    print(f"""
1. The broadcasting error occurs when computing Δy_{{t-2}}
   
2. Root cause: Index p-2 can be NEGATIVE when p is small
   
3. Example with p={p}:
   - For Δy_{{t-2}}, index = {p} - 2 = {p-2}
   {f'- This is NEGATIVE! → Empty array (0,{n})' if p-2 < 0 else f'- This is OK (≥0) ✓'}
   
4. Fix: Always use max(0, p-2) for the start index
   
5. Prevention: Ensure T ≥ p + 10 for reliable estimates
   - Current: T = {T}
   - Required: T ≥ {p + 10}
   {f'- Status: ✓ ADEQUATE' if T >= p + 10 else f'- Status: ❌ TOO SMALL'}
""")
    
    print("="*80)


def demonstrate_error():
    """Show the actual error happening."""
    import numpy as np
    
    print("\n" + "="*80)
    print("DEMONSTRATING THE ERROR")
    print("="*80)
    
    T = 50
    n = 3
    p = 2
    
    # Create data
    y = np.random.randn(T, n)
    delta_y = np.diff(y, axis=0)
    
    print(f"\nSetup: T={T}, n={n}, p={p}")
    print(f"delta_y shape: {delta_y.shape}")
    
    T_eff = T - 2 - (p - 1)
    print(f"T_eff = {T_eff}")
    
    # WRONG way (causes error)
    print("\n" + "-"*80)
    print("WRONG WAY (causes error):")
    print("-"*80)
    
    dy_t1_start = p - 1
    dy_t2_start_wrong = p - 3  # THIS IS WRONG!
    
    print(f"Δy_{{t-1}} start index: {dy_t1_start}")
    print(f"Δy_{{t-2}} start index: {dy_t2_start_wrong} ← NEGATIVE!")
    
    dy_t1 = delta_y[dy_t1_start:dy_t1_start + T_eff, :]
    
    try:
        # This might create an empty or wrong-sized array
        dy_t2_wrong = delta_y[dy_t2_start_wrong:dy_t2_start_wrong + T_eff, :]
        print(f"\nResult:")
        print(f"  Δy_{{t-1}} shape: {dy_t1.shape}")
        print(f"  Δy_{{t-2}} shape: {dy_t2_wrong.shape}")
        
        if dy_t2_wrong.shape[0] != dy_t1.shape[0]:
            print(f"\n  ❌ SHAPE MISMATCH!")
            print(f"  Cannot broadcast ({dy_t1.shape[0]},{n}) with ({dy_t2_wrong.shape[0]},{n})")
            print(f"  This would cause: ValueError: operands could not be broadcast...")
        
    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")
    
    # CORRECT way
    print("\n" + "-"*80)
    print("CORRECT WAY:")
    print("-"*80)
    
    dy_t2_start_correct = max(0, p - 2)  # THIS IS CORRECT!
    
    print(f"Δy_{{t-1}} start index: {dy_t1_start}")
    print(f"Δy_{{t-2}} start index: {dy_t2_start_correct} ← Using max(0, p-2)")
    
    dy_t2_correct = delta_y[dy_t2_start_correct:dy_t2_start_correct + T_eff, :]
    
    print(f"\nResult:")
    print(f"  Δy_{{t-1}} shape: {dy_t1.shape}")
    print(f"  Δy_{{t-2}} shape: {dy_t2_correct.shape}")
    
    if dy_t2_correct.shape[0] == dy_t1.shape[0]:
        print(f"\n  ✓ SHAPES MATCH!")
        print(f"  Can safely compute: v̂_{{2t}} = Δy_{{t-1}} - Δy_{{t-2}} @ N̂")
    else:
        print(f"\n  Still have issues - may need to adjust T_eff")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # Show dimension flow for different scenarios
    
    print("\n\n" + "#"*80)
    print("SCENARIO 1: Small sample (may cause issues)")
    print("#"*80)
    print_dimension_flow(T=50, n=3, p=2)
    
    print("\n\n" + "#"*80)
    print("SCENARIO 2: Adequate sample")
    print("#"*80)
    print_dimension_flow(T=200, n=3, p=2)
    
    print("\n\n" + "#"*80)
    print("SCENARIO 3: Large lag order (problematic)")
    print("#"*80)
    print_dimension_flow(T=50, n=3, p=5)
    
    # Demonstrate the actual error
    demonstrate_error()
    
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
The broadcasting error happens in Step 7 when constructing v̂_t.

KEY INSIGHT:
When p=2, the index for Δy_{t-2} is p-2 = 0 (OK)
When p=1, the index for Δy_{t-2} is p-2 = -1 (NEGATIVE!)

SOLUTION:
Always use: start_index = max(0, p-2)

This ensures you never get a negative index that would create
an empty or wrong-sized array causing the broadcasting error.
""")
