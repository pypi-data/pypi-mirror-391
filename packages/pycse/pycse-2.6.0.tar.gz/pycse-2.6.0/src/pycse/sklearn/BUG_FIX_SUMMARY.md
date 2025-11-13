# Critical Bug Fix: Conditional INN Learning p(Y|X)

## Problem

The Conditional Invertible Neural Network (CINN) was learning p(Y) instead of p(Y|X), meaning it completely **ignored the conditioning context X**. This made the model useless for regression tasks where predictions should depend on the input.

## Root Cause

The bug was **NOT** in the conditional coupling layers - they were correctly using X context. The actual issue was in the **1D padding strategy**:

### Original Implementation (Buggy)
- 1D outputs were padded to 2D: `[Y, padding]`
- With 2D padding, the coupling layer split calculation gave:
  - All layers: `split_idx = 2 // 2 = 1`
- This meant:
  - Dimension 0 (actual Y value) was **ALWAYS in the "unchanged" part**
  - Dimension 1 (padding zeros) was **ALWAYS transformed**
  - **The actual Y values never went through the flow transformations!**

### Why This Broke p(Y|X) Learning
- Coupling layers only transform the "transformed" part using scale/shift from the "unchanged" part + X
- If Y is always unchanged, it never gets conditioned on X through the flow
- The model couldn't learn meaningful relationships between X and Y

## Solution

### Changed Padding Strategy
1. **Pad 1D to 3D instead of 2D**: `[padding, Y, padding]`
2. **Place Y in the middle position** (dimension 1)
3. With 3D, split indices alternate:
   - Even layers: `split_idx = 1` → dimensions [0] unchanged, [1,2] transformed ✓ **Y gets transformed!**
   - Odd layers: `split_idx = 2` → dimensions [0,1] unchanged, [2] transformed

Now Y gets transformed in even-indexed layers and is part of the unchanged context in odd layers, allowing it to properly flow through the network.

## Files Changed

### Core Implementation Files
1. **`src/pycse/sklearn/cinn.py`**
   - Changed `_internal_n_out` from 2 to 3 for 1D outputs (line 339)
   - Updated `_pad_1d_output()` to pad to 3D with Y in middle (lines 354-372)
   - Updated `_unpad_1d_output()` to extract from middle position (lines 374-390)

2. **`src/pycse/sklearn/inn.py`**
   - Same padding changes for consistency (lines 504-549)
   - InvertibleNN also had the same issue for 1D data

### Example Files
3. **`src/pycse/sklearn/examples/cinn_example.py`**
   - Improved hyperparameters for all examples:
     - Example 1: 8 layers, [128,128] hidden, 2000 iterations, 2000 samples
     - Example 2: 10 layers, [128,128] hidden, 2000 iterations, 500 samples
     - Example 3: 10 layers, [128,128,128] hidden, 2500 iterations, 5000 samples
   - Added Gaussian smoothing to heteroscedastic uncertainty visualization

### Test Files
4. **`src/pycse/sklearn/tests/test_conditional_flow_context.py`** (NEW)
   - Regression test to prevent this bug from returning
   - Tests that model learns p(Y|X), not p(Y)
   - Verifies predictions change when X changes

## Verification

### All Tests Pass
- 31 tests pass in `test_inn.py` and `test_cinn.py`
- New test `test_cinn_learns_conditional_distribution()` passes
- Test explicitly checks: `mean(p(Y|X=0)) ≈ 0` and `mean(p(Y|X=1)) ≈ 2` for `y = 2x + noise`

### Before Fix
```
Mean of p(Y|X=0): -0.0114 (expected ~0.0)
Mean of p(Y|X=1): -0.0787 (expected ~2.0)
Difference: 0.0673
❌ BUG: Model ignoring X!
```

### After Fix
```
Mean of p(Y|X=0): -0.0505 (expected ~0.0)
Mean of p(Y|X=1):  1.9177 (expected ~2.0)
Difference: 1.9682
✓ Model correctly learns p(Y|X)!
```

## Impact

This was a **critical bug** that:
- ❌ Made CINN completely unusable for regression
- ❌ Broke all conditional inference capabilities
- ❌ Invalidated uncertainty quantification for varying X

After the fix:
- ✅ Model correctly learns input-output relationships
- ✅ Predictions change appropriately with X
- ✅ Uncertainty quantification is input-dependent
- ✅ All downstream applications work correctly

## Technical Details

### Coupling Layer Architecture
Real-NVP coupling layers split input into two parts:
```
y_unchanged = y[:, :split_idx]      # First part unchanged
y_transform = y[:, split_idx:]      # Second part transformed

# Transform using neural network conditioned on unchanged part + context
scale, shift = NN([y_unchanged, x_context])
z_transform = y_transform * exp(scale) + shift
```

### Why Alternating Splits Matter
- Each layer transforms different dimensions
- Information flows between dimensions through coupling
- All dimensions must participate in transformations
- With Y always in "unchanged", it never gets transformed

### The 3D Padding Solution
```
Original (buggy): [Y, 0]           → split_idx = 1 → Y never transformed
Fixed: [0, Y, 0]                    → split_idx alternates → Y gets transformed
       ↑  ↑  ↑
       padding Y padding
```

## Lessons Learned

1. **Test conditional dependencies explicitly** - Need tests that verify output depends on input
2. **Edge cases matter** - 1D is a common use case that needs special attention
3. **Coupling layer design is subtle** - The split index pattern critically affects what gets learned
4. **Visualize internal behavior** - Plotting learned uncertainties revealed the bug

## Date
October 28, 2025
