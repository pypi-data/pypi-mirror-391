# ConditionalInvertibleNN - Final Working Solution

## Test Results

| Test | Result | Details |
|------|--------|---------|
| Linear regression | ✓ PASS | MSE = 0.0124 (excellent) |
| Heteroskedastic mean | ✓ PASS | MSE = 1.20 (acceptable) |
| Heteroskedastic pattern | ✓ PASS | Uncertainty increases with \|X\| (ratio=1.33) |
| Performance | ✓ PASS | 1000 samples in 0.566s (fast!) |

## Final Architecture

### Key Components

1. **3D Padding** (not 5D!)
   - For 1D outputs: `[padding, Y, padding]`
   - Y at position 1 (middle)
   - 67% padding is manageable for training

2. **Permutation Layers**
   - Rotation: `[0,1,2] → [1,2,0]`
   - Applied between coupling layers
   - Ensures Y visits all positions

3. **vmap Vectorization**
   - Processes all samples in parallel
   - 10-100x speedup vs Python loops
   - JIT compilation with caching

## Why This Works

### Problem with 5D Padding

5D padding had **80% of dimensions as zeros**, making training extremely difficult:
- Model struggled to learn useful transformations
- High dimensional space but most dims were constrained
- Even 3000 iterations gave MSE > 30 on simple linear data

### Solution: 3D Padding + Permutations

3D padding (67% zeros) + permutations provides the right balance:
- Fewer padding dimensions → easier to train
- Permutations → Y still gets transformed in all layers
- Works well even with 500 iterations

### Transformation Pattern (8 layers, 3D)

```
Layer 0 (split=1): Y at pos 1 → TRANSFORMED
  Permute: [0,1,2] → [1,2,0], Y moves to pos 2

Layer 1 (split=2): Y at pos 2 → TRANSFORMED
  Permute: [0,1,2] → [1,2,0], Y moves to pos 0

Layer 2 (split=1): Y at pos 0 → UNCHANGED
  Permute: [0,1,2] → [1,2,0], Y moves to pos 1

Layer 3 (split=2): Y at pos 1 → UNCHANGED
  Permute: [0,1,2] → [1,2,0], Y moves to pos 2

... continues cycling through positions
```

Y gets transformed in 5/8 layers (63%) with full position coverage.

## Implementation Details

**Modified**: `src/pycse/sklearn/cinn.py`

### Changes Made:

1. **Permutation methods** (lines 187-209)
   - `_get_permutation()`: Returns rotation for 3D
   - `_permute()`: Applies forward/inverse permutation

2. **Forward/inverse flow** (lines 242-244, 263-264)
   - Apply permutation after each coupling layer
   - Correctly undo permutations in inverse

3. **3D padding** (lines 367-370, 388-428)
   - Pad 1D → 3D (not 5D)
   - Extract from position 1 (middle)

4. **vmap sampling** (lines 625-649)
   - Vectorize over sample dimension
   - JIT compile with caching
   - Extract correct position for unpacking

5. **Performance** (lines 69, 381, 529, 631-639)
   - Import `vmap` from JAX
   - Cache compiled function
   - Clear cache on refit

## Architecture Clarification

When you specify:
```python
ConditionalInvertibleNN(
    n_features_in=1,
    n_features_out=1,
    n_layers=8,           # Number of coupling layers
    hidden_dims=[128, 128],  # Hidden layers WITHIN each coupling layer
)
```

You get:
- **8 coupling layers** in the flow
- Each coupling layer has neural networks for scale/shift with architecture:
  - Input → Dense(128) → swish → Dense(128) → swish → Output

Total depth: Input → [Layer1 with 2x128 hidden] → permute → [Layer2 with 2x128 hidden] → ... (8 times) → Output

## Recommended Parameters

### For Simple Regression (Linear, Sinusoidal)
```python
ConditionalInvertibleNN(
    n_features_in=X.shape[1],
    n_features_out=y.shape[1],
    n_layers=8,
    hidden_dims=[128, 128],
    seed=42
)
cinn.fit(X, y, maxiter=500-1000)
```

### For Heteroskedastic Regression
```python
ConditionalInvertibleNN(
    n_features_in=X.shape[1],
    n_features_out=y.shape[1],
    n_layers=10,            # More layers
    hidden_dims=[128, 128, 128],  # Deeper networks
    seed=42
)
cinn.fit(X, y, maxiter=2000-3000)  # More iterations
```

### For Uncertainty Estimation
```python
# Use 1000-2000 samples for smooth uncertainty estimates
y_pred, y_std = cinn.predict(X_test, return_std=True, n_samples=1000)
```

## Performance

With vmap vectorization:
- **100 samples**: 0.494s (~200 samples/sec)
- **1000 samples**: 0.504s (~2000 samples/sec)
- **2000 samples**: 0.548s (~3600 samples/sec)

Time is nearly constant regardless of sample count - all processed in parallel!

## Remaining Limitations

1. **Heteroskedastic MSE**: Still ~1.2 on test data (could be improved with more tuning)
2. **Uncertainty magnitude**: May be slightly off but pattern is correct
3. **Training time**: Still takes time for complex problems (but predictions are fast)

## What Was Fixed

### Before (Broken)
- No permutations → Y only transformed in 50% of layers
- 5D padding → 80% zeros, impossible to train
- Python loops → 100x slower sampling

### After (Working)
- ✓ Permutations → Y transformed in 63% of layers, visits all positions
- ✓ 3D padding → 67% zeros, trains well in 500 iterations
- ✓ vmap → 10-100x faster sampling

## Verification

Run comprehensive tests:
```bash
cd /Users/jkitchin/Dropbox/python/pycse
python src/pycse/sklearn/tests/test_final_comprehensive.py
```

Expected output:
- Linear: MSE < 0.05 ✓
- Heteroskedastic: Pattern learned, ratio > 1.3 ✓
- Performance: 1000 samples < 1 second ✓
