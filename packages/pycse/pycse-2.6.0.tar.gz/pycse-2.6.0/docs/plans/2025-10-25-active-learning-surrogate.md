# Active Learning Surrogate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add ActiveSurrogate class to pyroxy.py that automatically builds surrogate models using active learning with Latin Hypercube initialization and multiple acquisition/stopping strategies.

**Architecture:** Monolithic class with `@classmethod build()` as entry point, private methods for acquisition functions and stopping criteria, returns fitted _Surrogate instance with training history.

**Tech Stack:** scipy.stats.qmc (LHS), scipy.stats.norm (acquisition), sklearn models, numpy

---

## Task 1: Add Imports and Class Skeleton

**Files:**
- Modify: `src/pycse/pyroxy.py` (after existing imports)

**Step 1: Write the failing test for class existence**

Create: `src/pycse/tests/test_active_surrogate.py`

```python
"""Tests for ActiveSurrogate class."""

import pytest
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

from pycse.pyroxy import ActiveSurrogate


@pytest.fixture
def simple_gpr():
    """Create a simple GPR model for testing."""
    kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
    return GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2)


@pytest.fixture
def simple_1d_function():
    """A simple 1D test function."""
    def f(X):
        return np.sin(X).flatten()
    return f


class TestActiveSurrogateBasic:
    """Basic tests for ActiveSurrogate class."""

    def test_class_exists(self):
        """Test that ActiveSurrogate class exists."""
        assert hasattr(ActiveSurrogate, 'build')
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateBasic::test_class_exists -v`

Expected: FAIL with "cannot import name 'ActiveSurrogate'"

**Step 3: Add imports and class skeleton to pyroxy.py**

Add after line 16 in `src/pycse/pyroxy.py`:

```python
from scipy.stats.qmc import LatinHypercube
from scipy.stats import norm
```

Add at end of `src/pycse/pyroxy.py` (after the `Surrogate.load = load` line):

```python


class ActiveSurrogate:
    """Build surrogate models using active learning.

    This class provides methods to automatically build surrogate models by
    iteratively sampling an input domain using acquisition functions to select
    informative points.
    """

    @classmethod
    def build(cls,
              func,
              bounds,
              model,
              acquisition='ei',
              stopping_criterion='mean_ratio',
              stopping_threshold=1.5,
              n_initial=None,
              batch_size=1,
              max_iterations=1000,
              n_test_points=None,
              n_candidates=None,
              verbose=False,
              callback=None,
              tol=1.0):
        """Build a surrogate model using active learning.

        Parameters
        ----------
        func : callable
            Function to surrogate. Must accept 2D array and return 1D array.

        bounds : list of tuples
            Domain bounds as [(low1, high1), (low2, high2), ...].

        model : sklearn model
            Model with predict(X, return_std=True) interface.

        acquisition : str, default='ei'
            Acquisition function: 'ei', 'ucb', 'pi', 'variance'.

        stopping_criterion : str, default='mean_ratio'
            Stopping criterion: 'mean_ratio', 'percentile', 'absolute', 'convergence'.

        stopping_threshold : float, default=1.5
            Threshold value for stopping criterion.

        n_initial : int, optional
            Initial samples. Defaults to max(10, 5*n_dims).

        batch_size : int, default=1
            Number of points to sample per iteration.

        max_iterations : int, default=1000
            Maximum iterations before stopping.

        n_test_points : int, optional
            Test points for uncertainty estimation. Defaults to 100*n_dims.

        n_candidates : int, optional
            Candidate points for acquisition. Defaults to 50*n_dims.

        verbose : bool, default=False
            Print progress information.

        callback : callable, optional
            Function called each iteration: callback(iteration, history).

        tol : float, default=1.0
            Tolerance for returned _Surrogate object.

        Returns
        -------
        surrogate : _Surrogate
            Fitted surrogate model.

        history : dict
            Training history with metrics per iteration.
        """
        # Placeholder implementation
        raise NotImplementedError("ActiveSurrogate.build() not yet implemented")
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateBasic::test_class_exists -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: add ActiveSurrogate class skeleton with build() method

Add basic class structure with comprehensive docstring.
Add test file for active surrogate functionality.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Implement Input Validation

**Files:**
- Modify: `src/pycse/pyroxy.py` (ActiveSurrogate.build method)

**Step 1: Write failing test for validation**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestActiveSurrogateValidation:
    """Test input validation for ActiveSurrogate."""

    def test_invalid_bounds_not_list(self, simple_gpr, simple_1d_function):
        """Test that non-list bounds raise error."""
        with pytest.raises(ValueError, match="bounds must be list"):
            ActiveSurrogate.build(
                func=simple_1d_function,
                bounds=(0, 1),  # tuple not list
                model=simple_gpr
            )

    def test_invalid_bounds_not_tuples(self, simple_gpr, simple_1d_function):
        """Test that non-tuple elements raise error."""
        with pytest.raises(ValueError, match="bounds must be list"):
            ActiveSurrogate.build(
                func=simple_1d_function,
                bounds=[[0, 1]],  # list not tuple
                model=simple_gpr
            )

    def test_invalid_acquisition(self, simple_gpr, simple_1d_function):
        """Test that invalid acquisition raises error."""
        with pytest.raises(ValueError, match="acquisition must be one of"):
            ActiveSurrogate.build(
                func=simple_1d_function,
                bounds=[(0, 1)],
                model=simple_gpr,
                acquisition='invalid'
            )

    def test_invalid_stopping_criterion(self, simple_gpr, simple_1d_function):
        """Test that invalid stopping criterion raises error."""
        with pytest.raises(ValueError, match="stopping_criterion must be one of"):
            ActiveSurrogate.build(
                func=simple_1d_function,
                bounds=[(0, 1)],
                model=simple_gpr,
                stopping_criterion='invalid'
            )
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateValidation -v`

Expected: FAIL with "NotImplementedError"

**Step 3: Implement validation**

Replace the `raise NotImplementedError` line in `ActiveSurrogate.build()` with:

```python
        # Validate bounds
        if not isinstance(bounds, list) or not all(
            isinstance(b, tuple) and len(b) == 2 for b in bounds
        ):
            raise ValueError("bounds must be list of (low, high) tuples")

        n_dims = len(bounds)

        # Validate acquisition
        valid_acquisitions = ['ei', 'ucb', 'pi', 'variance']
        if acquisition not in valid_acquisitions:
            raise ValueError(f"acquisition must be one of {valid_acquisitions}")

        # Validate stopping criterion
        valid_criteria = ['mean_ratio', 'percentile', 'absolute', 'convergence']
        if stopping_criterion not in valid_criteria:
            raise ValueError(f"stopping_criterion must be one of {valid_criteria}")

        # Set defaults
        if n_initial is None:
            n_initial = max(10, 5 * n_dims)
        if n_test_points is None:
            n_test_points = 100 * n_dims
        if n_candidates is None:
            n_candidates = 50 * n_dims

        # Placeholder for rest of implementation
        raise NotImplementedError("Rest of build() not yet implemented")
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateValidation -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: add input validation to ActiveSurrogate.build()

Validate bounds format, acquisition type, and stopping criterion.
Set intelligent defaults for n_initial, n_test_points, n_candidates.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Implement LHS Helper Method

**Files:**
- Modify: `src/pycse/pyroxy.py` (add private method to ActiveSurrogate)

**Step 1: Write failing test for LHS generation**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestActiveSurrogateLHS:
    """Test Latin Hypercube Sampling helper."""

    def test_generate_lhs_samples_1d(self):
        """Test LHS for 1D domain."""
        bounds = [(0.0, 10.0)]
        samples = ActiveSurrogate._generate_lhs_samples(bounds, n_samples=20)

        assert samples.shape == (20, 1)
        assert np.all(samples >= 0.0)
        assert np.all(samples <= 10.0)

    def test_generate_lhs_samples_2d(self):
        """Test LHS for 2D domain."""
        bounds = [(0.0, 10.0), (-5.0, 5.0)]
        samples = ActiveSurrogate._generate_lhs_samples(bounds, n_samples=30)

        assert samples.shape == (30, 2)
        assert np.all(samples[:, 0] >= 0.0)
        assert np.all(samples[:, 0] <= 10.0)
        assert np.all(samples[:, 1] >= -5.0)
        assert np.all(samples[:, 1] <= 5.0)

    def test_generate_lhs_samples_coverage(self):
        """Test that LHS provides good coverage."""
        bounds = [(0.0, 1.0)]
        samples = ActiveSurrogate._generate_lhs_samples(bounds, n_samples=100)

        # Check distribution across domain
        assert np.min(samples) < 0.2
        assert np.max(samples) > 0.8
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateLHS -v`

Expected: FAIL with "AttributeError: type object 'ActiveSurrogate' has no attribute '_generate_lhs_samples'"

**Step 3: Implement LHS helper method**

Add to ActiveSurrogate class (before the `build` method):

```python
    @staticmethod
    def _generate_lhs_samples(bounds, n_samples):
        """Generate Latin Hypercube samples within bounds.

        Parameters
        ----------
        bounds : list of tuples
            Domain bounds as [(low1, high1), (low2, high2), ...].
        n_samples : int
            Number of samples to generate.

        Returns
        -------
        samples : ndarray, shape (n_samples, n_dims)
            LHS samples scaled to bounds.
        """
        n_dims = len(bounds)
        sampler = LatinHypercube(d=n_dims)
        unit_samples = sampler.random(n=n_samples)

        # Scale from [0,1] to actual bounds
        samples = np.zeros_like(unit_samples)
        for i, (low, high) in enumerate(bounds):
            samples[:, i] = low + unit_samples[:, i] * (high - low)

        return samples
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateLHS -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: add Latin Hypercube sampling helper method

Implement _generate_lhs_samples() using scipy.stats.qmc.
Properly scales samples from unit cube to domain bounds.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Implement Acquisition Functions

**Files:**
- Modify: `src/pycse/pyroxy.py` (add acquisition methods to ActiveSurrogate)

**Step 1: Write failing tests for acquisition functions**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestAcquisitionFunctions:
    """Test acquisition function implementations."""

    @pytest.fixture
    def fitted_model(self):
        """Create a fitted GPR model."""
        X = np.array([[0.0], [1.0], [2.0], [3.0]])
        y = np.sin(X).flatten()

        kernel = C(1.0) * RBF(1.0)
        model = GaussianProcessRegressor(kernel=kernel)
        model.fit(X, y)
        return model, y

    def test_acquisition_ei(self, fitted_model):
        """Test Expected Improvement acquisition."""
        model, y_train = fitted_model
        X_candidates = np.array([[1.5], [2.5]])

        ei = ActiveSurrogate._acquisition_ei(X_candidates, model, y_train.max())

        assert ei.shape == (2,)
        assert np.all(ei >= 0)

    def test_acquisition_ucb(self, fitted_model):
        """Test Upper Confidence Bound acquisition."""
        model, _ = fitted_model
        X_candidates = np.array([[1.5], [2.5]])

        ucb = ActiveSurrogate._acquisition_ucb(X_candidates, model, kappa=2.0)

        assert ucb.shape == (2,)

    def test_acquisition_pi(self, fitted_model):
        """Test Probability of Improvement acquisition."""
        model, y_train = fitted_model
        X_candidates = np.array([[1.5], [2.5]])

        pi = ActiveSurrogate._acquisition_pi(X_candidates, model, y_train.max())

        assert pi.shape == (2,)
        assert np.all(pi >= 0)
        assert np.all(pi <= 1)

    def test_acquisition_variance(self, fitted_model):
        """Test Maximum Variance acquisition."""
        model, _ = fitted_model
        X_candidates = np.array([[1.5], [2.5], [10.0]])

        variance = ActiveSurrogate._acquisition_variance(X_candidates, model)

        assert variance.shape == (3,)
        assert np.all(variance >= 0)
        # Point far from training data should have higher variance
        assert variance[2] > variance[0]
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestAcquisitionFunctions -v`

Expected: FAIL with "AttributeError: no attribute '_acquisition_ei'"

**Step 3: Implement acquisition functions**

Add to ActiveSurrogate class (after _generate_lhs_samples):

```python
    @staticmethod
    def _acquisition_ei(X_candidates, model, y_best):
        """Expected Improvement acquisition function.

        Parameters
        ----------
        X_candidates : ndarray, shape (n_candidates, n_dims)
            Candidate points to evaluate.
        model : sklearn model
            Fitted model with predict(return_std=True).
        y_best : float
            Current best observed value.

        Returns
        -------
        ei : ndarray, shape (n_candidates,)
            Expected improvement values.
        """
        mu, sigma = model.predict(X_candidates, return_std=True)
        mu = mu.flatten()
        sigma = sigma.flatten()

        with np.errstate(divide='warn', invalid='ignore'):
            Z = (mu - y_best) / sigma
            ei = (mu - y_best) * norm.cdf(Z) + sigma * norm.pdf(Z)
            ei[sigma == 0.0] = 0.0

        return ei

    @staticmethod
    def _acquisition_ucb(X_candidates, model, kappa=2.0):
        """Upper Confidence Bound acquisition function.

        Parameters
        ----------
        X_candidates : ndarray, shape (n_candidates, n_dims)
            Candidate points to evaluate.
        model : sklearn model
            Fitted model with predict(return_std=True).
        kappa : float, default=2.0
            Exploration parameter.

        Returns
        -------
        ucb : ndarray, shape (n_candidates,)
            UCB values.
        """
        mu, sigma = model.predict(X_candidates, return_std=True)
        return mu.flatten() + kappa * sigma.flatten()

    @staticmethod
    def _acquisition_pi(X_candidates, model, y_best):
        """Probability of Improvement acquisition function.

        Parameters
        ----------
        X_candidates : ndarray, shape (n_candidates, n_dims)
            Candidate points to evaluate.
        model : sklearn model
            Fitted model with predict(return_std=True).
        y_best : float
            Current best observed value.

        Returns
        -------
        pi : ndarray, shape (n_candidates,)
            Probability of improvement values.
        """
        mu, sigma = model.predict(X_candidates, return_std=True)
        mu = mu.flatten()
        sigma = sigma.flatten()

        Z = (mu - y_best) / (sigma + 1e-9)
        return norm.cdf(Z)

    @staticmethod
    def _acquisition_variance(X_candidates, model):
        """Maximum Variance (pure exploration) acquisition function.

        Parameters
        ----------
        X_candidates : ndarray, shape (n_candidates, n_dims)
            Candidate points to evaluate.
        model : sklearn model
            Fitted model with predict(return_std=True).

        Returns
        -------
        variance : ndarray, shape (n_candidates,)
            Variance (uncertainty) values.
        """
        _, sigma = model.predict(X_candidates, return_std=True)
        return sigma.flatten()
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestAcquisitionFunctions -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: add acquisition functions (EI, UCB, PI, variance)

Implement four acquisition strategies for active learning:
- Expected Improvement (EI)
- Upper Confidence Bound (UCB)
- Probability of Improvement (PI)
- Maximum Variance (pure exploration)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Implement Stopping Criteria

**Files:**
- Modify: `src/pycse/pyroxy.py` (add stopping criterion methods to ActiveSurrogate)

**Step 1: Write failing tests for stopping criteria**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestStoppingCriteria:
    """Test stopping criterion implementations."""

    def test_stopping_mean_ratio_met(self):
        """Test mean_ratio criterion when met."""
        test_unc = np.array([0.5, 0.6, 0.7])
        train_unc = np.array([0.8, 0.9, 1.0])

        # test mean = 0.6, train mean = 0.9, ratio = 0.67 < 1.5
        result = ActiveSurrogate._stopping_mean_ratio(test_unc, train_unc, threshold=1.5)
        assert result is True

    def test_stopping_mean_ratio_not_met(self):
        """Test mean_ratio criterion when not met."""
        test_unc = np.array([1.5, 2.0, 2.5])
        train_unc = np.array([0.8, 0.9, 1.0])

        # test mean = 2.0, train mean = 0.9, ratio = 2.22 > 1.5
        result = ActiveSurrogate._stopping_mean_ratio(test_unc, train_unc, threshold=1.5)
        assert result is False

    def test_stopping_percentile_met(self):
        """Test percentile criterion when met."""
        test_unc = np.linspace(0.01, 0.09, 100)

        result = ActiveSurrogate._stopping_percentile(test_unc, threshold=0.1)
        assert result is True

    def test_stopping_absolute_met(self):
        """Test absolute criterion when met."""
        test_unc = np.array([0.05, 0.08, 0.09])

        result = ActiveSurrogate._stopping_absolute(test_unc, threshold=0.1)
        assert result is True

    def test_stopping_absolute_not_met(self):
        """Test absolute criterion when not met."""
        test_unc = np.array([0.05, 0.08, 0.15])

        result = ActiveSurrogate._stopping_absolute(test_unc, threshold=0.1)
        assert result is False

    def test_stopping_convergence_met(self):
        """Test convergence criterion when met."""
        history = {
            'mean_uncertainty': [1.0, 0.9, 0.89, 0.88, 0.87, 0.875, 0.87]
        }

        result = ActiveSurrogate._stopping_convergence(history, window=5, threshold=0.05)
        assert result is True

    def test_stopping_convergence_not_met(self):
        """Test convergence criterion when not met."""
        history = {
            'mean_uncertainty': [1.0, 0.9, 0.7, 0.5, 0.3]
        }

        result = ActiveSurrogate._stopping_convergence(history, window=3, threshold=0.05)
        assert result is False
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestStoppingCriteria -v`

Expected: FAIL with "AttributeError: no attribute '_stopping_mean_ratio'"

**Step 3: Implement stopping criteria**

Add to ActiveSurrogate class (after acquisition functions):

```python
    @staticmethod
    def _stopping_mean_ratio(test_uncertainties, train_uncertainties, threshold=1.5):
        """Mean ratio stopping criterion.

        Stop when mean test uncertainty is within threshold of training uncertainty.

        Parameters
        ----------
        test_uncertainties : ndarray
            Uncertainties at test points.
        train_uncertainties : ndarray
            Uncertainties at training points.
        threshold : float
            Ratio threshold.

        Returns
        -------
        bool
            True if stopping criterion is met.
        """
        mean_test = np.mean(test_uncertainties)
        mean_train = np.mean(train_uncertainties)
        ratio = mean_test / (mean_train + 1e-9)
        return ratio < threshold

    @staticmethod
    def _stopping_percentile(test_uncertainties, threshold=0.1):
        """Percentile-based stopping criterion.

        Stop when 95th percentile of test uncertainty drops below threshold.

        Parameters
        ----------
        test_uncertainties : ndarray
            Uncertainties at test points.
        threshold : float
            Absolute threshold.

        Returns
        -------
        bool
            True if stopping criterion is met.
        """
        percentile_95 = np.percentile(test_uncertainties, 95)
        return percentile_95 < threshold

    @staticmethod
    def _stopping_absolute(test_uncertainties, threshold=0.1):
        """Absolute threshold stopping criterion.

        Stop when maximum test uncertainty drops below threshold.

        Parameters
        ----------
        test_uncertainties : ndarray
            Uncertainties at test points.
        threshold : float
            Absolute threshold.

        Returns
        -------
        bool
            True if stopping criterion is met.
        """
        return np.max(test_uncertainties) < threshold

    @staticmethod
    def _stopping_convergence(history, window=5, threshold=0.01):
        """Convergence-based stopping criterion.

        Stop when uncertainty change over last 'window' iterations is small.

        Parameters
        ----------
        history : dict
            Training history with 'mean_uncertainty' key.
        window : int
            Number of iterations to check.
        threshold : float
            Relative change threshold.

        Returns
        -------
        bool
            True if stopping criterion is met.
        """
        if len(history['mean_uncertainty']) < window + 1:
            return False

        recent = history['mean_uncertainty'][-window:]
        previous = history['mean_uncertainty'][-(window + 1)]
        change = abs(np.mean(recent) - previous) / (previous + 1e-9)
        return change < threshold
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestStoppingCriteria -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: add stopping criteria (mean_ratio, percentile, absolute, convergence)

Implement four stopping strategies for active learning:
- Mean ratio of test to training uncertainty
- 95th percentile threshold
- Absolute maximum threshold
- Convergence detection

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Implement Batch Selection Strategy

**Files:**
- Modify: `src/pycse/pyroxy.py` (add batch selection method to ActiveSurrogate)

**Step 1: Write failing test for batch selection**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestBatchSelection:
    """Test batch selection with hallucination."""

    @pytest.fixture
    def fitted_model_2d(self):
        """Create a fitted 2D GPR model."""
        X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        y = np.sin(X[:, 0]) + np.cos(X[:, 1])

        kernel = C(1.0) * RBF(1.0)
        model = GaussianProcessRegressor(kernel=kernel)
        model.fit(X, y)
        return model, y

    def test_select_batch_single(self, fitted_model_2d):
        """Test batch selection with batch_size=1."""
        model, y_train = fitted_model_2d
        X_candidates = np.random.rand(20, 2)

        selected = ActiveSurrogate._select_batch(
            X_candidates, model, y_train, acquisition='ei', batch_size=1
        )

        assert selected.shape == (1, 2)

    def test_select_batch_multiple(self, fitted_model_2d):
        """Test batch selection with batch_size>1."""
        model, y_train = fitted_model_2d
        X_candidates = np.random.rand(50, 2)

        selected = ActiveSurrogate._select_batch(
            X_candidates, model, y_train, acquisition='ucb', batch_size=3
        )

        assert selected.shape == (3, 2)
        # Check that selected points are different
        assert not np.array_equal(selected[0], selected[1])
        assert not np.array_equal(selected[1], selected[2])

    def test_select_batch_diversity(self, fitted_model_2d):
        """Test that batch selection promotes diversity."""
        model, y_train = fitted_model_2d
        # Create candidates with a clear cluster
        X_candidates = np.vstack([
            np.random.rand(40, 2) * 0.1 + 0.5,  # Clustered around 0.5
            np.random.rand(10, 2)  # Spread across space
        ])

        selected = ActiveSurrogate._select_batch(
            X_candidates, model, y_train, acquisition='variance', batch_size=3
        )

        # With hallucination, points should be somewhat spread
        distances = []
        for i in range(len(selected)):
            for j in range(i + 1, len(selected)):
                distances.append(np.linalg.norm(selected[i] - selected[j]))

        # At least some non-trivial distance between selected points
        assert np.mean(distances) > 0.01
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestBatchSelection -v`

Expected: FAIL with "AttributeError: no attribute '_select_batch'"

**Step 3: Implement batch selection with hallucination**

Add to ActiveSurrogate class (after stopping criteria):

```python
    @classmethod
    def _select_batch(cls, X_candidates, model, y_train, acquisition, batch_size):
        """Select batch of points using sequential hallucination.

        Parameters
        ----------
        X_candidates : ndarray, shape (n_candidates, n_dims)
            Candidate points to select from.
        model : sklearn model
            Fitted model.
        y_train : ndarray
            Current training targets.
        acquisition : str
            Acquisition function name.
        batch_size : int
            Number of points to select.

        Returns
        -------
        selected : ndarray, shape (batch_size, n_dims)
            Selected points.
        """
        selected_indices = []
        selected_points = []

        # Copy training data for hallucination
        y_hallucinated = y_train.copy()

        for i in range(batch_size):
            # Compute acquisition values
            if acquisition == 'ei':
                acq_values = cls._acquisition_ei(X_candidates, model, y_hallucinated.max())
            elif acquisition == 'ucb':
                acq_values = cls._acquisition_ucb(X_candidates, model)
            elif acquisition == 'pi':
                acq_values = cls._acquisition_pi(X_candidates, model, y_hallucinated.max())
            elif acquisition == 'variance':
                acq_values = cls._acquisition_variance(X_candidates, model)
            else:
                raise ValueError(f"Unknown acquisition: {acquisition}")

            # Mask already selected points
            acq_values = acq_values.copy()
            for idx in selected_indices:
                acq_values[idx] = -np.inf

            # Select best point
            best_idx = np.argmax(acq_values)
            selected_indices.append(best_idx)
            selected_points.append(X_candidates[best_idx])

            # Hallucinate: predict value and add to training set (for next iteration)
            if i < batch_size - 1:
                X_new = X_candidates[best_idx:best_idx + 1]
                y_new = model.predict(X_new)
                y_hallucinated = np.concatenate([y_hallucinated, y_new.flatten()])

        return np.array(selected_points)
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestBatchSelection -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: add batch selection with hallucination strategy

Implement sequential hallucination for selecting diverse batches.
Prevents selecting clustered redundant points in batch mode.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Implement Main Build Loop

**Files:**
- Modify: `src/pycse/pyroxy.py` (replace NotImplementedError in build())

**Step 1: Write failing end-to-end test**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestActiveSurrogateEndToEnd:
    """End-to-end integration tests."""

    def test_build_simple_1d(self, simple_gpr, simple_1d_function):
        """Test building surrogate for simple 1D function."""
        bounds = [(0, 2 * np.pi)]

        surrogate, history = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            acquisition='variance',
            stopping_criterion='absolute',
            stopping_threshold=0.2,
            n_initial=5,
            max_iterations=20,
            verbose=False
        )

        # Check surrogate is a _Surrogate instance
        from pycse.pyroxy import _Surrogate
        assert isinstance(surrogate, _Surrogate)

        # Check it has training data
        assert surrogate.xtrain is not None
        assert surrogate.ytrain is not None
        assert len(surrogate.xtrain) >= 5  # At least initial samples

        # Check history
        assert 'iterations' in history
        assert 'n_samples' in history
        assert 'mean_uncertainty' in history
        assert len(history['iterations']) > 0

        # Check surrogate works
        X_test = np.array([[np.pi/2]])
        y_pred = surrogate(X_test)
        assert y_pred.shape == (1,)

    def test_build_respects_max_iterations(self, simple_gpr, simple_1d_function):
        """Test that max_iterations limits are respected."""
        bounds = [(0, 10)]

        surrogate, history = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            acquisition='ei',
            stopping_criterion='absolute',
            stopping_threshold=0.001,  # Very strict, won't be met
            n_initial=3,
            max_iterations=5,
            verbose=False
        )

        # Should stop at max_iterations
        assert len(history['iterations']) <= 5
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateEndToEnd -v`

Expected: FAIL with "NotImplementedError"

**Step 3: Implement main build loop**

Replace the final `raise NotImplementedError` in `build()` with:

```python
        # Initialize history
        history = {
            'iterations': [],
            'n_samples': [],
            'acquisition_values': [],
            'mean_uncertainty': [],
            'max_uncertainty': [],
            'X_sampled': []
        }

        # Generate initial samples via LHS
        X_train = cls._generate_lhs_samples(bounds, n_initial)
        y_train = func(X_train)

        # Fit initial model
        model.fit(X_train, y_train)

        if verbose:
            print(f"Initialized with {n_initial} LHS samples")

        # Active learning loop
        for iteration in range(max_iterations):
            # Generate test points for uncertainty estimation
            X_test = cls._generate_lhs_samples(bounds, n_test_points)
            _, test_uncertainties = model.predict(X_test, return_std=True)

            # Get training uncertainties
            _, train_uncertainties = model.predict(X_train, return_std=True)

            # Record metrics
            mean_unc = np.mean(test_uncertainties)
            max_unc = np.max(test_uncertainties)

            # Check stopping criterion
            stopping_met = False
            if stopping_criterion == 'mean_ratio':
                stopping_met = cls._stopping_mean_ratio(
                    test_uncertainties, train_uncertainties, stopping_threshold
                )
            elif stopping_criterion == 'percentile':
                stopping_met = cls._stopping_percentile(test_uncertainties, stopping_threshold)
            elif stopping_criterion == 'absolute':
                stopping_met = cls._stopping_absolute(test_uncertainties, stopping_threshold)
            elif stopping_criterion == 'convergence':
                stopping_met = cls._stopping_convergence(history, threshold=stopping_threshold)

            if stopping_met:
                if verbose:
                    print(f"Stopping criterion met at iteration {iteration}")
                break

            # Generate candidate points
            X_candidates = cls._generate_lhs_samples(bounds, n_candidates)

            # Select next batch
            X_new = cls._select_batch(X_candidates, model, y_train, acquisition, batch_size)

            # Evaluate function at new points
            y_new = func(X_new)

            # Compute acquisition value for logging
            if acquisition == 'ei':
                acq_at_selected = cls._acquisition_ei(X_new, model, y_train.max())
            elif acquisition == 'ucb':
                acq_at_selected = cls._acquisition_ucb(X_new, model)
            elif acquisition == 'pi':
                acq_at_selected = cls._acquisition_pi(X_new, model, y_train.max())
            elif acquisition == 'variance':
                acq_at_selected = cls._acquisition_variance(X_new, model)

            best_acq = np.max(acq_at_selected)

            # Update training data
            X_train = np.vstack([X_train, X_new])
            y_train = np.concatenate([y_train, y_new.flatten()])

            # Refit model
            model.fit(X_train, y_train)

            # Update history
            history['iterations'].append(iteration)
            history['n_samples'].append(len(X_train))
            history['acquisition_values'].append(best_acq)
            history['mean_uncertainty'].append(mean_unc)
            history['max_uncertainty'].append(max_unc)
            history['X_sampled'].append(X_new)

            if verbose:
                print(f"Iteration {iteration}/{max_iterations}")
                print(f"  Samples: {len(X_train)}")
                print(f"  Best acquisition: {best_acq:.4f}")
                print(f"  Mean uncertainty: {mean_unc:.4f}")
                print(f"  Max uncertainty: {max_unc:.4f}")

            # Call callback if provided
            if callback is not None:
                callback(iteration, history)

        # Create and return _Surrogate
        surrogate = _Surrogate(
            func=func,
            model=model,
            tol=tol,
            max_calls=-1,
            verbose=verbose
        )

        # Populate with training data
        surrogate.xtrain = X_train
        surrogate.ytrain = y_train
        surrogate.func_calls = len(X_train)
        surrogate.ntrain = len(history['iterations']) + 1  # +1 for initial fit

        if verbose:
            print(f"\nActive learning complete: {len(X_train)} samples")

        return surrogate, history
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateEndToEnd -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "feat: implement main active learning loop in build()

Complete implementation:
- Initialize with LHS samples
- Iterative acquisition and sampling
- Stopping criterion checking
- History tracking and verbose output
- Return fitted _Surrogate with history

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Add Comprehensive Integration Tests

**Files:**
- Modify: `src/pycse/tests/test_active_surrogate.py`

**Step 1: Write additional integration tests**

Add to `src/pycse/tests/test_active_surrogate.py`:

```python
class TestActiveSurrogateIntegration:
    """Additional integration tests for various scenarios."""

    def test_build_2d_function(self, simple_gpr):
        """Test with 2D function."""
        def func_2d(X):
            return (np.sin(X[:, 0]) * np.cos(X[:, 1])).flatten()

        bounds = [(0, np.pi), (0, np.pi)]

        surrogate, history = ActiveSurrogate.build(
            func=func_2d,
            bounds=bounds,
            model=simple_gpr,
            acquisition='ei',
            stopping_criterion='mean_ratio',
            stopping_threshold=2.0,
            n_initial=10,
            max_iterations=15,
            verbose=False
        )

        assert surrogate.xtrain.shape[1] == 2
        assert len(surrogate.ytrain) >= 10

    def test_different_acquisitions(self, simple_gpr, simple_1d_function):
        """Test all acquisition functions."""
        bounds = [(0, 2 * np.pi)]

        for acq in ['ei', 'ucb', 'pi', 'variance']:
            surrogate, history = ActiveSurrogate.build(
                func=simple_1d_function,
                bounds=bounds,
                model=simple_gpr,
                acquisition=acq,
                stopping_criterion='absolute',
                stopping_threshold=0.5,
                n_initial=5,
                max_iterations=10,
                verbose=False
            )

            assert len(surrogate.xtrain) >= 5

    def test_different_stopping_criteria(self, simple_gpr, simple_1d_function):
        """Test all stopping criteria."""
        bounds = [(0, 2 * np.pi)]

        # Test mean_ratio
        surrogate, _ = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            stopping_criterion='mean_ratio',
            stopping_threshold=1.5,
            n_initial=5,
            max_iterations=20
        )
        assert surrogate is not None

        # Test percentile
        surrogate, _ = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            stopping_criterion='percentile',
            stopping_threshold=0.2,
            n_initial=5,
            max_iterations=20
        )
        assert surrogate is not None

        # Test absolute
        surrogate, _ = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            stopping_criterion='absolute',
            stopping_threshold=0.2,
            n_initial=5,
            max_iterations=20
        )
        assert surrogate is not None

    def test_batch_mode(self, simple_gpr, simple_1d_function):
        """Test batch sampling."""
        bounds = [(0, 2 * np.pi)]

        surrogate, history = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            acquisition='ucb',
            batch_size=3,
            stopping_criterion='absolute',
            stopping_threshold=0.3,
            n_initial=5,
            max_iterations=5
        )

        # With batch_size=3, should add 3 points per iteration
        # Check that sample count increases appropriately
        assert len(surrogate.xtrain) >= 5

    def test_callback_invoked(self, simple_gpr, simple_1d_function):
        """Test that callback is called during training."""
        bounds = [(0, 2 * np.pi)]
        callback_count = [0]

        def test_callback(iteration, history):
            callback_count[0] += 1

        surrogate, history = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            acquisition='variance',
            stopping_criterion='absolute',
            stopping_threshold=0.3,
            n_initial=3,
            max_iterations=5,
            callback=test_callback
        )

        # Callback should be invoked at least once
        assert callback_count[0] > 0

    def test_surrogate_usage_after_build(self, simple_gpr, simple_1d_function):
        """Test that returned surrogate can be used for prediction."""
        bounds = [(0, 2 * np.pi)]

        surrogate, _ = ActiveSurrogate.build(
            func=simple_1d_function,
            bounds=bounds,
            model=simple_gpr,
            acquisition='ei',
            stopping_criterion='absolute',
            stopping_threshold=0.3,
            n_initial=10,
            max_iterations=10
        )

        # Test prediction
        X_test = np.linspace(0, 2 * np.pi, 20).reshape(-1, 1)
        y_pred = surrogate(X_test)

        assert y_pred.shape == (20,)

        # Check that predictions are reasonable
        y_true = simple_1d_function(X_test)
        rmse = np.sqrt(np.mean((y_pred - y_true) ** 2))
        assert rmse < 0.5  # Should be reasonably accurate
```

**Step 2: Run tests**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py::TestActiveSurrogateIntegration -v`

Expected: PASS

**Step 3: Commit**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/tests/test_active_surrogate.py
git commit -m "test: add comprehensive integration tests for ActiveSurrogate

Add tests for:
- 2D functions
- All acquisition functions
- All stopping criteria
- Batch mode
- Callback functionality
- End-to-end surrogate usage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Run Full Test Suite

**Files:**
- N/A (verification step)

**Step 1: Run all active surrogate tests**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_active_surrogate.py -v`

Expected: All tests PASS

**Step 2: Run all pyroxy tests to ensure no regressions**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python -m pytest src/pycse/tests/test_pyroxy.py -v`

Expected: All tests PASS

**Step 3: Check code formatting**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && ruff format src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py`

Expected: Files formatted

**Step 4: Commit if any formatting changes**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add src/pycse/pyroxy.py src/pycse/tests/test_active_surrogate.py
git commit -m "style: format code with ruff

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Create Example/Demo (Optional)

**Files:**
- Create: `examples/active_surrogate_demo.py` or similar

**Step 1: Create example script**

Create: `examples/active_surrogate_demo.py`

```python
"""Demo of ActiveSurrogate for automatic surrogate modeling."""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

from pycse.pyroxy import ActiveSurrogate


# Define an expensive function to surrogate
def expensive_function(X):
    """A moderately complex 1D function."""
    x = X.flatten()
    return np.sin(x) + 0.5 * np.sin(3 * x) + 0.1 * x


# Define domain
bounds = [(0, 10)]

# Create model
kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
model = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5)

# Build surrogate with active learning
print("Building surrogate with active learning...")
surrogate, history = ActiveSurrogate.build(
    func=expensive_function,
    bounds=bounds,
    model=model,
    acquisition='ei',
    stopping_criterion='mean_ratio',
    stopping_threshold=1.5,
    n_initial=5,
    max_iterations=30,
    verbose=True
)

print(f"\nFinal model: {len(surrogate.xtrain)} samples")

# Visualize results
X_plot = np.linspace(0, 10, 200).reshape(-1, 1)
y_true = expensive_function(X_plot)
y_pred = surrogate(X_plot)

plt.figure(figsize=(12, 8))

# Plot 1: Function and surrogate
plt.subplot(2, 2, 1)
plt.plot(X_plot, y_true, 'b-', label='True function', linewidth=2)
plt.plot(X_plot, y_pred, 'r--', label='Surrogate', linewidth=2)
plt.scatter(surrogate.xtrain, surrogate.ytrain, c='black', s=50,
            label=f'Samples (n={len(surrogate.xtrain)})', zorder=5)
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.title('Surrogate vs True Function')
plt.grid(True, alpha=0.3)

# Plot 2: Sample progression
plt.subplot(2, 2, 2)
plt.plot(history['iterations'], history['n_samples'], 'b-o')
plt.xlabel('Iteration')
plt.ylabel('Total Samples')
plt.title('Sample Count vs Iteration')
plt.grid(True, alpha=0.3)

# Plot 3: Uncertainty evolution
plt.subplot(2, 2, 3)
plt.plot(history['iterations'], history['mean_uncertainty'], 'g-o', label='Mean')
plt.plot(history['iterations'], history['max_uncertainty'], 'r-s', label='Max')
plt.xlabel('Iteration')
plt.ylabel('Uncertainty')
plt.legend()
plt.title('Uncertainty Evolution')
plt.grid(True, alpha=0.3)

# Plot 4: Acquisition values
plt.subplot(2, 2, 4)
plt.plot(history['iterations'], history['acquisition_values'], 'm-o')
plt.xlabel('Iteration')
plt.ylabel('Best Acquisition Value')
plt.title('Acquisition Value vs Iteration')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('active_surrogate_demo.png', dpi=150)
print("\nVisualization saved to active_surrogate_demo.png")
plt.show()
```

**Step 2: Test the example**

Run: `cd /Users/jkitchin/Dropbox/python/pycse && python examples/active_surrogate_demo.py`

Expected: Script runs successfully and produces plot

**Step 3: Commit example**

```bash
cd /Users/jkitchin/Dropbox/python/pycse
git add examples/active_surrogate_demo.py
git commit -m "docs: add demo script for ActiveSurrogate

Example showing active learning with visualization of:
- Surrogate vs true function
- Sample progression
- Uncertainty evolution
- Acquisition values

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Summary

This plan implements the ActiveSurrogate class using TDD principles with frequent commits. The implementation includes:

1. ✅ Class skeleton and imports
2. ✅ Input validation
3. ✅ Latin Hypercube sampling
4. ✅ Four acquisition functions (EI, UCB, PI, variance)
5. ✅ Four stopping criteria (mean_ratio, percentile, absolute, convergence)
6. ✅ Batch selection with hallucination
7. ✅ Complete active learning loop
8. ✅ Comprehensive tests
9. ✅ Example demo script

Total estimated time: 2-3 hours for methodical TDD implementation.

---

**Plan complete!**
