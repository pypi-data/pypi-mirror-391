# Active Learning Surrogate Design

**Date:** 2025-10-24
**Status:** Approved for implementation
**Module:** `pycse.pyroxy`

## Overview

This design adds an `ActiveSurrogate` class to the pyroxy module that automatically builds surrogate models using active learning. The class iteratively samples a user-specified input domain, starting with Latin Hypercube sampling and then using acquisition functions to intelligently select additional sample points until convergence criteria are met.

## Requirements

### Functional Requirements
- Start with Latin Hypercube sampling for initialization
- Support multiple acquisition functions: Expected Improvement (EI), Upper Confidence Bound (UCB), Probability of Improvement (PI), Maximum Variance
- Support multiple stopping criteria: mean ratio, percentile-based, absolute threshold, convergence-based
- Support both sequential (one point at a time) and batch sampling
- Track training history and provide monitoring capabilities
- Return a fitted `_Surrogate` object ready for use

### Design Constraints
- Implement as new class in existing `pyroxy.py` module
- Accept sklearn models with `predict(return_std=True)` interface
- Use `scipy.stats.qmc.LatinHypercube` for sampling
- Domain specified as list of (low, high) tuples
- Maintain consistency with existing pyroxy API patterns

## Architecture

### High-Level API

```python
from pycse.pyroxy import ActiveSurrogate

surrogate, history = ActiveSurrogate.build(
    func=expensive_function,
    bounds=[(0, 10), (-5, 5)],
    model=GaussianProcessRegressor(),
    acquisition='ei',
    stopping_criterion='mean_ratio',
    stopping_threshold=1.5,
    n_initial=None,  # defaults to max(10, 5*n_dims)
    batch_size=1,
    max_iterations=1000,
    verbose=True
)

# Use the returned surrogate
y_pred = surrogate(X_new)
```

### Class Structure

**Monolithic class with method selection:**
- Single `ActiveSurrogate` class with `@classmethod build()`
- Private methods for each acquisition function
- Private methods for each stopping criterion
- Dispatcher methods route to appropriate implementation based on string parameters

**Return values:**
- `surrogate`: Fitted `_Surrogate` instance
- `history`: Dictionary with training metrics per iteration

## Core Components

### 1. Initialization

**Latin Hypercube Sampling:**
```python
from scipy.stats.qmc import LatinHypercube

n_dims = len(bounds)
n_initial = n_initial or max(10, 5 * n_dims)

sampler = LatinHypercube(d=n_dims)
sample = sampler.random(n=n_initial)

# Scale from [0,1] to actual bounds
X_initial = np.zeros_like(sample)
for i, (low, high) in enumerate(bounds):
    X_initial[:, i] = low + sample[:, i] * (high - low)
```

**Initial model fitting:**
- Evaluate function at all initial points
- Fit model to initial data
- Store X_train, y_train for subsequent iterations

### 2. Active Learning Loop

**Each iteration:**
1. Generate test points via LHS (`n_test = 100 * n_dims`)
2. Evaluate model uncertainty at test points
3. Check stopping criterion - if met, return
4. Generate candidate points via LHS (`n_candidates = 50 * n_dims`)
5. Compute acquisition function at candidates
6. Select best point(s) using batch selection strategy
7. Evaluate function at selected points
8. Add to training data and refit model
9. Update history
10. Call callback if provided

**Loop termination:**
- Stopping criterion met, OR
- Maximum iterations reached

### 3. Acquisition Functions

**Expected Improvement (EI):**
```python
def _acquisition_ei(self, X_candidates, model, y_best):
    mu, sigma = model.predict(X_candidates, return_std=True)
    Z = (mu - y_best) / (sigma + 1e-9)
    ei = (mu - y_best) * norm.cdf(Z) + sigma * norm.pdf(Z)
    ei[sigma == 0.0] = 0.0
    return ei.flatten()
```

**Upper Confidence Bound (UCB):**
```python
def _acquisition_ucb(self, X_candidates, model, kappa=2.0):
    mu, sigma = model.predict(X_candidates, return_std=True)
    return (mu + kappa * sigma).flatten()
```

**Probability of Improvement (PI):**
```python
def _acquisition_pi(self, X_candidates, model, y_best):
    mu, sigma = model.predict(X_candidates, return_std=True)
    Z = (mu - y_best) / (sigma + 1e-9)
    return norm.cdf(Z).flatten()
```

**Maximum Variance:**
```python
def _acquisition_variance(self, X_candidates, model):
    _, sigma = model.predict(X_candidates, return_std=True)
    return sigma.flatten()
```

### 4. Stopping Criteria

**Mean Ratio:**
Stop when `mean(test_uncertainty) / mean(train_uncertainty) < threshold`

**Percentile:**
Stop when `percentile_95(test_uncertainty) < threshold`

**Absolute:**
Stop when `max(test_uncertainty) < threshold`

**Convergence:**
Stop when change in mean uncertainty over last N iterations is below threshold

### 5. Batch Sampling Strategy

**Sequential hallucination for batch_size > 1:**
1. Select point with highest acquisition value
2. "Hallucinate" its value using model prediction
3. Temporarily add to training set
4. Recompute acquisition (selected point now has low value)
5. Repeat for batch_size iterations

This prevents selecting clustered redundant points.

### 6. Monitoring & Visualization

**Verbose output per iteration:**
- Iteration number
- Total samples
- Best acquisition value
- Domain uncertainty statistics

**History tracking:**
```python
history = {
    'iterations': [1, 2, 3, ...],
    'n_samples': [10, 11, 12, ...],
    'acquisition_values': [0.5, 0.3, ...],
    'mean_uncertainty': [1.2, 0.8, ...],
    'max_uncertainty': [2.1, 1.5, ...],
    'X_sampled': [array(...), ...]
}
```

**Progress callback:**
User can provide function called each iteration:
```python
def callback(iteration, surrogate, history):
    # Custom logging/plotting
    pass
```

## Parameters

### Required Parameters
- `func`: Callable to surrogate
- `bounds`: List of (low, high) tuples
- `model`: sklearn model with `predict(return_std=True)`

### Optional Parameters
- `acquisition`: str, default='ei' - Acquisition function ('ei', 'ucb', 'pi', 'variance')
- `stopping_criterion`: str, default='mean_ratio' - Stopping criterion type
- `stopping_threshold`: float, default=1.5 - Threshold for stopping criterion
- `n_initial`: int or None - Initial samples, defaults to max(10, 5*n_dims)
- `batch_size`: int, default=1 - Points sampled per iteration
- `max_iterations`: int, default=1000 - Safety limit
- `n_test_points`: int or None - Test points for uncertainty, defaults to 100*n_dims
- `n_candidates`: int or None - Candidate points for acquisition, defaults to 50*n_dims
- `verbose`: bool, default=False - Print progress
- `callback`: callable or None - Function called each iteration
- `tol`: float, default=1.0 - Tolerance for returned _Surrogate object

## Error Handling

**Input validation:**
- Bounds must be list of (low, high) tuples
- Model must support `predict(X, return_std=True)`
- Acquisition must be in ['ei', 'ucb', 'pi', 'variance']
- Stopping criterion must be in ['mean_ratio', 'percentile', 'absolute', 'convergence']
- batch_size must be positive integer
- max_iterations must be positive integer

**Runtime safety:**
- Catch model fitting failures and provide clear error messages
- Handle edge cases (sigma=0, division by zero in acquisition functions)
- Ensure iteration limit prevents runaway sampling

## Integration with Existing Code

**Relationship to _Surrogate:**
- `ActiveSurrogate.build()` returns a fitted `_Surrogate` instance
- Populates `xtrain`, `ytrain`, `func_calls`, `ntrain` attributes
- The returned surrogate works exactly like manually created ones

**Dependencies:**
- `scipy.stats.qmc` for Latin Hypercube sampling
- `scipy.stats.norm` for EI/PI acquisition functions
- Uses existing `_Surrogate` class from pyroxy.py

## Testing Strategy

**Unit tests needed:**
- Each acquisition function (verify correct computation)
- Each stopping criterion (verify triggering conditions)
- Batch selection (verify diversity)
- LHS initialization (verify coverage)
- Parameter validation (verify error handling)

**Integration tests:**
- End-to-end on simple 1D function (verify convergence)
- Multi-dimensional test function
- Batch sampling vs sequential comparison
- Different acquisition/stopping combinations

**Test fixtures:**
- Simple analytical functions (sin, polynomial)
- Mock sklearn models for isolated testing
- Pre-defined bounds for reproducibility

## Future Enhancements

**Not in scope for initial implementation:**
- Constrained optimization (linear/nonlinear constraints)
- Multi-objective acquisition functions
- Adaptive batch sizing
- Parallelization of function evaluations
- Saving/loading partial progress
- Alternative batch selection strategies (local penalization, Kriging Believer)

These can be added later based on user needs.

## Implementation Notes

- All acquisition and stopping methods are private (prefixed with `_`)
- The `build()` classmethod is the only public interface
- Total code ~400-500 lines including docstrings
- Add to existing `pyroxy.py` file (don't create new module)
- Maintain consistent style with existing pyroxy code
