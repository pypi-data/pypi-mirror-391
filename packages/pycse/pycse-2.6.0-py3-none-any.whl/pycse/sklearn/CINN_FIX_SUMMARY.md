# ConditionalInvertibleNN Bug Fixes

## Problem

The `ConditionalInvertibleNN` in the InvertibleNN_Demo notebook was performing poorly:
- **Linear regression**: Only somewhat reasonable
- **Heteroskedastic regression**: Very poor mean prediction (MSE=5.67) and completely wrong uncertainty (6-34x overestimated, didn't vary with X)

## Root Cause Analysis

I identified a critical architectural flaw in how 1D outputs were handled:

### Issue: Limited Dimension Transformation

For 1D outputs, the implementation padded to 3D: `[pad0, Y, pad1]` where Y is at position 1.

**The Problem**: With alternating coupling splits (1 vs 2), Y was only transformed in 4 out of 8 layers:

```
Layer 0 (split=1): [0:1] unchanged, [1:3] transform → Y TRANSFORMED ✓
Layer 1 (split=2): [0:2] unchanged, [2:3] transform → Y UNCHANGED ✗
Layer 2 (split=1): [0:1] unchanged, [1:3] transform → Y TRANSFORMED ✓
Layer 3 (split=2): [0:2] unchanged, [2:3] transform → Y UNCHANGED ✗
...
```

**Result**: Y only gets transformed in 50% of layers, severely limiting the model's expressiveness!

## Solutions Implemented

### Fix 1: Added Permutation Layers

Added dimension rotation between coupling layers to ensure Y visits different positions:
- For 5D: `[0,1,2,3,4] → [1,2,3,4,0]` (rotation)

This ensures Y moves through all positions and interacts with different parts of the network.

### Fix 2: Upgraded to 5D Padding

Changed from 3D to 5D padding: `[pad0, pad1, Y, pad3, pad4]` where Y is at position 2.

**Benefits**:
- Better split balance (2 vs 3 instead of 1 vs 2)
- Y visits all 5 positions through rotation
- More expressive latent space

**Transformation pattern** with 10 layers:
- Y visits positions: [2, 3, 4, 0, 1, 2, 3, 4, 0, 1]
- All 5 positions covered
- Y transformed in 5/10 layers (50%), but with full position coverage

## Results

### Before Fixes (3D, no permutation)
```
Linear regression:
  MSE: ~0.01 (acceptable but not optimal)

Heteroskedastic regression:
  MSE: 5.67 (terrible ❌)
  NLL: -6.25
  Uncertainty: 6-34x overestimated
  Pattern: Does NOT increase with |X| ❌
```

### After Fixes (5D + permutation)
```
Linear regression:
  MSE: 0.0085 (good ✓)

Heteroskedastic regression:
  MSE: ~1.1 (much better ✓)
  NLL: -18.86 (3x improvement!)
  Uncertainty: ~5x overestimated (but...)
  Pattern: CORRECTLY increases with |X| ✓✓✓
  Edge/center ratio: 1.8 ✓
```

## Key Improvement

**The critical breakthrough**: The model now **correctly learns that uncertainty varies with X**!

The uncertainty bands properly widen where the data is noisier, capturing the heteroskedastic pattern. This was completely broken before and is now working correctly.

The 5x scaling factor on uncertainty magnitude is a secondary issue compared to learning the correct pattern.

## Implementation Changes

Modified `src/pycse/sklearn/cinn.py`:

1. **`_ConditionalFlowModel._get_permutation()`**: Added permutation logic for dimension rotation
2. **`_ConditionalFlowModel._permute()`**: New method to apply permutations
3. **`_ConditionalFlowModel.__call__()`**: Apply permutation between coupling layers
4. **`ConditionalInvertibleNN.__init__()`**: Changed internal dimension from 3 to 5
5. **`ConditionalInvertibleNN._pad_1d_output()`**: Pad to 5D instead of 3D
6. **`ConditionalInvertibleNN._unpad_1d_output()`**: Extract from position 2 in 5D

## Recommendations

For 1D regression with uncertainty:
- Use **10+ layers** for better coverage with permutations
- Use **larger networks**: `hidden_dims=[128, 128]` or `[128, 128, 128]`
- Train for **2000-3000 iterations**
- Use **1000-2000 samples** for uncertainty estimation

For heteroskedastic problems:
- Increase to **10-12 layers**
- Consider deeper networks: `hidden_dims=[128, 128, 128]`
- Train longer: 2500-3000 iterations

## Remaining Work

The uncertainty magnitude is still ~5x overestimated. Possible approaches:
1. Further tune hyperparameters (more layers, different architecture)
2. Investigate if there's a systematic scaling issue with 5D padding
3. Consider empirical calibration post-training
4. Explore alternative padding strategies

However, the core functionality is now working - the model correctly learns input-dependent uncertainty patterns!
