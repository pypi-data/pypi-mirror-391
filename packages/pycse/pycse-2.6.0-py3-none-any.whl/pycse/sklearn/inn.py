"""Invertible Neural Networks (Normalizing Flows) for sklearn.

This module provides invertible neural networks (INNs), also known as normalizing flows,
using JAX/Flax. These networks learn bijective (invertible) transformations between
data and latent distributions, enabling exact likelihood computation, sampling, and
inverse problem solving.

Key Concepts
------------
An invertible neural network learns a bijective function f: X → Z that transforms
complex data distributions into simple latent distributions (typically Gaussian).
The transformation is:

1. **Forward**: z = f(x) transforms data to latent space
2. **Inverse**: x = f⁻¹(z) generates data from latent samples
3. **Likelihood**: Uses change of variables formula:
   log p(x) = log p(z) + log |det(df/dx)|

Architecture
------------
This implementation uses **Real-NVP** (Real-valued Non-Volume Preserving) coupling layers:

- **Affine Coupling**: Split input, transform half using neural network outputs from other half
- **Permutation**: Alternate which dimensions are transformed to ensure all get processed
- **Stacking**: Multiple coupling layers create expressive transformations

Benefits over standard neural networks:
- Exact likelihood (no approximation like VAE)
- Efficient sampling (no MCMC needed)
- Invertibility enables solving inverse problems
- Density estimation for anomaly detection

Use Cases
---------
- Density estimation and generative modeling
- Anomaly detection (outliers have low likelihood)
- Data augmentation (sample from learned distribution)
- Inverse problems (map from observations to parameters)
- Uncertainty quantification in scientific computing

Classes
-------
InvertibleNN
    sklearn-compatible invertible neural network for density estimation and generation.

Notes
-----
- Requires JAX, Flax, and jaxopt
- Uses LBFGS optimizer for maximum likelihood training
- Compatible with sklearn pipelines
- Best suited for continuous data distributions

Examples
--------
Basic density estimation and sampling:

>>> import jax
>>> import numpy as np
>>> from pycse.sklearn.inn import InvertibleNN
>>>
>>> # Generate 2D spiral data
>>> key = jax.random.PRNGKey(42)
>>> theta = np.linspace(0, 4*np.pi, 500)
>>> r = theta / (4*np.pi)
>>> x = np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)
>>> x += 0.05 * jax.random.normal(key, x.shape)
>>>
>>> # Train invertible NN
>>> inn = InvertibleNN(n_features=2, n_layers=8, hidden_dims=[64, 64])
>>> inn.fit(x)
>>>
>>> # Generate new samples
>>> samples = inn.sample(100, key=jax.random.PRNGKey(1))
>>>
>>> # Compute likelihood
>>> log_prob = inn.log_prob(x[:10])
>>> print(f"Average log-likelihood: {np.mean(log_prob):.3f}")
>>>
>>> # Detect anomalies
>>> test_points = np.array([[5.0, 5.0], [0.0, 0.0]])  # far, close
>>> lp = inn.log_prob(test_points)
>>> print(f"Outlier likelihood: {lp[0]:.3f}")  # Lower
>>> print(f"Inlier likelihood: {lp[1]:.3f}")   # Higher

References
----------
.. [1] Dinh et al., "Density estimation using Real NVP", ICLR 2017
.. [2] Ardizzone et al., "Analyzing Inverse Problems with Invertible Neural Networks", ICLR 2019
"""

import os
import warnings
import jax
import jax.numpy as np
from jax import jit, value_and_grad
from jaxopt import LBFGS
from sklearn.base import BaseEstimator, DensityMixin
from flax import linen as nn
from typing import Tuple, List, Optional, Callable
import matplotlib.pyplot as plt

# Enable 64-bit precision for numerical stability
os.environ["JAX_ENABLE_X64"] = "True"
jax.config.update("jax_enable_x64", True)


class _CouplingLayer(nn.Module):
    """Affine coupling layer for invertible transformations.

    This implements the Real-NVP coupling layer which splits the input,
    keeps half unchanged, and transforms the other half using scale and
    shift parameters computed by a neural network.

    Attributes
    ----------
    hidden_dims : list of int
        Number of neurons in each hidden layer of the scale/shift network.
    n_features : int
        Total number of features.
    split_idx : int
        Index where to split features (first part unchanged, second transformed).

    Notes
    -----
    The transformation is:
        y[:split_idx] = x[:split_idx]  (unchanged)
        y[split_idx:] = x[split_idx:] * exp(s(x[:split_idx])) + t(x[:split_idx])

    where s and t are neural network outputs (scale and shift).
    """

    hidden_dims: List[int]
    n_features: int
    split_idx: int

    def _compute_scale_shift(self, h):
        """Compute scale and shift parameters from input.

        Parameters
        ----------
        h : jax.numpy.ndarray
            Input to the conditioning network.

        Returns
        -------
        log_scale : jax.numpy.ndarray
            Log-scale parameters (bounded by tanh).
        shift : jax.numpy.ndarray
            Shift parameters.
        """
        # Number of outputs = number of transformed dimensions
        n_out = self.n_features - self.split_idx

        # Scale network
        h_scale = h
        for i, dim in enumerate(self.hidden_dims):
            h_scale = nn.Dense(dim, name=f'scale_dense_{i}')(h_scale)
            h_scale = nn.swish(h_scale)

        log_scale = nn.Dense(n_out, name='scale_out')(h_scale)
        log_scale = np.tanh(log_scale)  # Bound for stability

        # Shift network
        h_shift = h
        for i, dim in enumerate(self.hidden_dims):
            h_shift = nn.Dense(dim, name=f'shift_dense_{i}')(h_shift)
            h_shift = nn.swish(h_shift)

        shift = nn.Dense(n_out, name='shift_out')(h_shift)

        return log_scale, shift

    @nn.compact
    def forward_and_log_det(self, x):
        """Forward pass with log determinant computation.

        Parameters
        ----------
        x : jax.numpy.ndarray
            Input of shape (n_samples, n_features).

        Returns
        -------
        y : jax.numpy.ndarray
            Transformed output of shape (n_samples, n_features).
        log_det : jax.numpy.ndarray
            Log determinant of Jacobian of shape (n_samples,).
        """
        # Split input based on split_idx
        x_unchanged = x[:, :self.split_idx]
        x_transform = x[:, self.split_idx:]

        # Compute scale and shift from unchanged part
        log_scale, shift = self._compute_scale_shift(x_unchanged)

        # Apply affine transformation to second half
        y_transform = x_transform * np.exp(log_scale) + shift

        # Concatenate unchanged and transformed parts
        y = np.concatenate([x_unchanged, y_transform], axis=1)

        # Log determinant is sum of log scales
        log_det = np.sum(log_scale, axis=1)

        return y, log_det

    @nn.compact
    def inverse(self, y):
        """Inverse transformation (z → x).

        Parameters
        ----------
        y : jax.numpy.ndarray
            Latent representation of shape (n_samples, n_features).

        Returns
        -------
        x : jax.numpy.ndarray
            Reconstructed input of shape (n_samples, n_features).
        """
        # Split based on split_idx
        y_unchanged = y[:, :self.split_idx]
        y_transform = y[:, self.split_idx:]

        # Compute scale and shift from unchanged part
        log_scale, shift = self._compute_scale_shift(y_unchanged)

        # Invert affine transformation
        x_transform = (y_transform - shift) * np.exp(-log_scale)

        # Concatenate unchanged and transformed parts
        x = np.concatenate([y_unchanged, x_transform], axis=1)

        return x

    @nn.compact
    def __call__(self, x, inverse=False):
        """Forward or inverse transformation.

        Parameters
        ----------
        x : jax.numpy.ndarray
            Input array.
        inverse : bool, default=False
            If True, perform inverse transformation.

        Returns
        -------
        output : jax.numpy.ndarray or tuple
            If inverse=False: (y, log_det)
            If inverse=True: x
        """
        if inverse:
            return self.inverse(x)
        else:
            return self.forward_and_log_det(x)


class _FlowModel(nn.Module):
    """Complete normalizing flow model with multiple coupling layers.

    Attributes
    ----------
    n_features : int
        Dimensionality of the data.
    n_layers : int
        Number of coupling layers.
    hidden_dims : list of int
        Hidden layer dimensions for each coupling layer's neural networks.
    """

    n_features: int
    n_layers: int
    hidden_dims: List[int]

    def _get_split_idx(self, layer_idx):
        """Get split index for a given layer.

        Alternates between splitting at first half and second half
        to ensure all dimensions get transformed.
        """
        if layer_idx % 2 == 0:
            # First half unchanged, second half transformed
            return self.n_features // 2
        else:
            # Second half unchanged, first half transformed
            return self.n_features - self.n_features // 2

    @nn.compact
    def __call__(self, x, inverse=False):
        """Forward or inverse transformation.

        Parameters
        ----------
        x : jax.numpy.ndarray
            Input array.
        inverse : bool, default=False
            If True, perform inverse (generative) transformation.

        Returns
        -------
        output : jax.numpy.ndarray or tuple
            If inverse=False: (z, log_det)
            If inverse=True: x
        """
        if inverse:
            # Inverse: apply layers in reverse order
            result = x
            for i in reversed(range(self.n_layers)):
                split_idx = self._get_split_idx(i)
                layer = _CouplingLayer(
                    hidden_dims=self.hidden_dims,
                    n_features=self.n_features,
                    split_idx=split_idx,
                    name=f'coupling_{i}'
                )
                result = layer.inverse(result)
            return result
        else:
            # Forward: apply layers in order
            z = x
            log_det_sum = np.zeros(x.shape[0])

            for i in range(self.n_layers):
                split_idx = self._get_split_idx(i)
                layer = _CouplingLayer(
                    hidden_dims=self.hidden_dims,
                    n_features=self.n_features,
                    split_idx=split_idx,
                    name=f'coupling_{i}'
                )
                z, log_det = layer.forward_and_log_det(z)
                log_det_sum += log_det

            return z, log_det_sum


class InvertibleNN(BaseEstimator, DensityMixin):
    """Invertible Neural Network for density estimation and generation.

    This implements a normalizing flow using Real-NVP coupling layers to learn
    invertible transformations between data and latent distributions. The model
    can compute exact likelihoods, generate samples, and solve inverse problems.

    Parameters
    ----------
    n_features : int
        Dimensionality of the input data.
    n_layers : int, default=6
        Number of coupling layers. More layers → more expressive but slower.
        Typical range: 4-12.
    hidden_dims : list of int, default=[64, 64]
        Architecture of the neural networks within each coupling layer.
        Each int specifies neurons in a hidden layer.
    base_dist : str, default='normal'
        Base distribution in latent space. Currently only 'normal' supported.
    seed : int, default=42
        Random seed for reproducibility.

    Attributes
    ----------
    flow : _FlowModel
        Internal Flax flow model.
    key : jax.random.PRNGKey
        Random key for JAX operations.
    params_ : dict, optional
        Trained model parameters (available after fit()).
    state_ : OptStep, optional
        Optimization state (available after fit()).
    data_mean_ : jax.numpy.ndarray, optional
        Mean of training data for normalization.
    data_std_ : jax.numpy.ndarray, optional
        Std of training data for normalization.

    Methods
    -------
    fit(X, normalize=True, **kwargs)
        Train the flow by maximizing likelihood.
    forward(X)
        Transform data to latent space.
    inverse(Z)
        Transform latent samples to data space.
    log_prob(X)
        Compute log probability (likelihood) of data.
    sample(n_samples, key=None)
        Generate samples from the learned distribution.
    score_samples(X)
        Alias for log_prob (sklearn compatibility).
    plot(X, n_samples=1000)
        Visualize the learned distribution (2D only).
    report()
        Print training statistics.

    Examples
    --------
    Learn 2D distribution and generate samples:

    >>> import jax
    >>> import numpy as np
    >>> from pycse.sklearn.inn import InvertibleNN
    >>>
    >>> # Create 2D moons dataset
    >>> from sklearn.datasets import make_moons
    >>> X, _ = make_moons(n_samples=1000, noise=0.05)
    >>>
    >>> # Train invertible NN
    >>> inn = InvertibleNN(n_features=2, n_layers=8, hidden_dims=[64, 64])
    >>> inn.fit(X)
    >>> inn.report()
    >>>
    >>> # Generate new samples
    >>> samples = inn.sample(500, key=jax.random.PRNGKey(123))
    >>>
    >>> # Compute likelihoods
    >>> log_probs = inn.log_prob(X[:10])
    >>> print(f"Mean log-prob: {np.mean(log_probs):.3f}")
    >>>
    >>> # Visualize
    >>> inn.plot(X)

    Anomaly detection example:

    >>> # Train on normal data
    >>> X_train = np.random.randn(1000, 2)
    >>> inn = InvertibleNN(n_features=2, n_layers=6)
    >>> inn.fit(X_train)
    >>>
    >>> # Test on outliers
    >>> X_test = np.array([[0, 0], [10, 10]])  # normal, outlier
    >>> scores = inn.log_prob(X_test)
    >>> print(f"Normal: {scores[0]:.2f}, Outlier: {scores[1]:.2f}")
    >>> # Outlier should have lower (more negative) log probability

    Notes
    -----
    - Training maximizes log-likelihood using LBFGS
    - Data normalization (centering + scaling) recommended for stability
    - Works best with continuous distributions
    - 2D and 3D data supported for visualization
    - Requires sufficient training data (typically 500+ samples)

    See Also
    --------
    sklearn.mixture.GaussianMixture : Alternative density estimator
    sklearn.neighbors.KernelDensity : Non-parametric density estimation

    References
    ----------
    .. [1] Dinh, Sohl-Dickstein, and Bengio. "Density estimation using Real NVP."
           ICLR 2017.
    .. [2] Papamakarios et al. "Normalizing Flows for Probabilistic Modeling
           and Inference." JMLR 2021.
    """

    def __init__(
        self,
        n_features: int,
        n_layers: int = 6,
        hidden_dims: List[int] = None,
        base_dist: str = 'normal',
        seed: int = 42
    ):
        """Initialize the Invertible Neural Network.

        Parameters
        ----------
        n_features : int
            Dimensionality of input data.
        n_layers : int, default=6
            Number of coupling layers.
        hidden_dims : list of int, default=[64, 64]
            Hidden layer architecture for coupling networks.
        base_dist : str, default='normal'
            Base latent distribution ('normal' only for now).
        seed : int, default=42
            Random seed.

        Raises
        ------
        ValueError
            If n_features < 2, n_layers < 1, or invalid parameters.
        """
        if hidden_dims is None:
            hidden_dims = [64, 64]

        # Validate parameters
        if n_features < 1:
            raise ValueError(f"n_features must be >= 1, got {n_features}")
        if n_layers < 1:
            raise ValueError(f"n_layers must be >= 1, got {n_layers}")
        if not all(d > 0 for d in hidden_dims):
            raise ValueError(f"All hidden_dims must be positive, got {hidden_dims}")
        if base_dist != 'normal':
            raise ValueError(f"Only 'normal' base_dist supported, got {base_dist}")

        self.n_features = n_features
        self.n_layers = n_layers
        self.hidden_dims = hidden_dims
        self.base_dist = base_dist
        self.seed = seed

        self.key = jax.random.PRNGKey(seed)

        # For 1D data, pad to 3D internally (2D is too small for proper coupling layer alternation)
        self._is_1d = (n_features == 1)
        flow_features = 3 if self._is_1d else n_features

        self.flow = _FlowModel(
            n_features=flow_features,
            n_layers=n_layers,
            hidden_dims=hidden_dims
        )

    def _pad_1d(self, X):
        """Pad 1D data to 3D for internal processing.

        Parameters
        ----------
        X : array of shape (n_samples, 1)
            1D data to pad.

        Returns
        -------
        X_padded : array of shape (n_samples, 3)
            Padded to 3D with X in middle position.
        """
        if not self._is_1d:
            return X
        # Pad to 3D with X in middle position so it gets transformed in coupling layers
        # Layout: [padding, X, padding]
        return np.concatenate([np.zeros((X.shape[0], 1)), X, np.zeros((X.shape[0], 1))], axis=1)

    def _unpad_1d(self, X_padded):
        """Extract 1D data from padded 3D representation.

        Parameters
        ----------
        X_padded : array of shape (n_samples, 3)
            Padded 3D data with layout [padding, X, padding].

        Returns
        -------
        X : array of shape (n_samples, 1)
            Original 1D data from middle position.
        """
        if not self._is_1d:
            return X_padded
        # Extract X from middle position (dimension 1)
        return X_padded[:, 1:2]

    @property
    def is_fitted(self):
        """Check if model has been fitted.

        Returns
        -------
        bool
            True if fit() has been called.
        """
        return hasattr(self, 'params_')

    def fit(self, X, normalize=True, **kwargs):
        """Train the invertible neural network by maximizing likelihood.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        normalize : bool, default=True
            If True, normalize data to zero mean and unit variance.
            Recommended for numerical stability.
        **kwargs : dict
            Additional arguments for LBFGS optimizer:
            - maxiter : int, default=2000
            - tol : float, default=1e-5

        Returns
        -------
        self
            Returns self for method chaining.

        Raises
        ------
        ValueError
            If X has wrong shape or contains NaN/inf.

        Examples
        --------
        >>> inn = InvertibleNN(n_features=2)
        >>> X = np.random.randn(1000, 2)
        >>> inn.fit(X, maxiter=3000, tol=1e-6)
        """
        X = np.asarray(X)

        # Validate input
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got shape {X.shape}")
        if X.shape[1] != self.n_features:
            raise ValueError(
                f"X has {X.shape[1]} features, expected {self.n_features}"
            )
        if not np.all(np.isfinite(X)):
            raise ValueError("X contains NaN or inf values")

        # Normalize data
        if normalize:
            self.data_mean_ = np.mean(X, axis=0)
            self.data_std_ = np.std(X, axis=0) + 1e-8  # Avoid division by zero
            X_norm = (X - self.data_mean_) / self.data_std_
        else:
            self.data_mean_ = np.zeros(self.n_features)
            self.data_std_ = np.ones(self.n_features)
            X_norm = X

        # Pad 1D data if needed
        X_norm = self._pad_1d(X_norm)

        # Initialize parameters
        self.key, init_key = jax.random.split(self.key)
        dummy_input = np.zeros((1, X_norm.shape[1]))  # Use padded dimensions
        params = self.flow.init(init_key, dummy_input)

        # Define negative log-likelihood objective
        @jit
        def nll_loss(params, X_batch):
            """Negative log-likelihood loss."""
            # Forward pass
            z, log_det = self.flow.apply(params, X_batch)

            # Base distribution log prob (standard normal)
            # For 1D, only first dimension matters
            if self._is_1d:
                z_relevant = z[:, :1]
                log_pz = -0.5 * np.sum(z_relevant**2, axis=1) - 0.5 * np.log(2 * np.pi)
            else:
                log_pz = -0.5 * np.sum(z**2, axis=1) - 0.5 * self.n_features * np.log(2 * np.pi)

            # Change of variables
            log_px = log_pz + log_det

            # Return negative mean log-likelihood
            return -np.mean(log_px)

        # Set optimizer parameters
        if 'maxiter' not in kwargs:
            kwargs['maxiter'] = 2000
        if 'tol' not in kwargs:
            kwargs['tol'] = 1e-5

        self.maxiter = kwargs['maxiter']

        # Run optimization
        solver = LBFGS(fun=value_and_grad(nll_loss), value_and_grad=True, **kwargs)
        self.params_, self.state_ = solver.run(params, X_norm)

        # Store final loss
        self.final_nll_ = float(self.state_.value)

        return self

    def forward(self, X):
        """Transform data to latent space (x → z).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        Z : jax.numpy.ndarray of shape (n_samples, n_features)
            Latent representations.
        log_det : jax.numpy.ndarray of shape (n_samples,)
            Log determinant of Jacobian.

        Raises
        ------
        RuntimeError
            If model not fitted.

        Examples
        --------
        >>> Z, log_det = inn.forward(X_test)
        >>> print(f"Latent mean: {np.mean(Z, axis=0)}")
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        X = np.asarray(X)
        X_norm = (X - self.data_mean_) / self.data_std_
        X_norm = self._pad_1d(X_norm)

        z, log_det = self.flow.apply(self.params_, X_norm)
        z = self._unpad_1d(z)
        return z, log_det

    def inverse(self, Z):
        """Transform latent samples to data space (z → x).

        Parameters
        ----------
        Z : array-like of shape (n_samples, n_features)
            Latent samples (typically from standard normal).

        Returns
        -------
        X : jax.numpy.ndarray of shape (n_samples, n_features)
            Generated data.

        Raises
        ------
        RuntimeError
            If model not fitted.

        Examples
        --------
        >>> Z = np.random.randn(100, 2)
        >>> X_generated = inn.inverse(Z)
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        Z = np.asarray(Z)
        Z_padded = self._pad_1d(Z)
        X_norm = self.flow.apply(self.params_, Z_padded, inverse=True)
        X_norm = self._unpad_1d(X_norm)
        X = X_norm * self.data_std_ + self.data_mean_

        return X

    def log_prob(self, X):
        """Compute log probability density of data.

        This computes the exact log-likelihood using the change of
        variables formula.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        log_prob : jax.numpy.ndarray of shape (n_samples,)
            Log probability for each sample. Higher = more likely.

        Raises
        ------
        RuntimeError
            If model not fitted.

        Examples
        --------
        >>> log_probs = inn.log_prob(X_test)
        >>> print(f"Average log-likelihood: {np.mean(log_probs):.3f}")
        >>>
        >>> # Anomaly detection
        >>> is_anomaly = log_probs < np.percentile(log_probs, 5)
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        X = np.asarray(X)
        X_norm = (X - self.data_mean_) / self.data_std_
        X_norm = self._pad_1d(X_norm)

        # Forward transform
        z, log_det = self.flow.apply(self.params_, X_norm)

        # Base distribution log prob
        # For 1D, only use first dimension
        if self._is_1d:
            z_relevant = z[:, :1]
            log_pz = -0.5 * np.sum(z_relevant**2, axis=1) - 0.5 * np.log(2 * np.pi)
        else:
            log_pz = -0.5 * np.sum(z**2, axis=1) - 0.5 * self.n_features * np.log(2 * np.pi)

        # Adjust for normalization
        log_det_norm = -np.sum(np.log(self.data_std_))

        # Total log probability
        log_px = log_pz + log_det + log_det_norm

        return log_px

    def score_samples(self, X):
        """Compute log-likelihood of samples (sklearn compatibility).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        log_prob : jax.numpy.ndarray of shape (n_samples,)
            Log probability for each sample.
        """
        return self.log_prob(X)

    def score(self, X, y=None):
        """Compute mean log-likelihood (sklearn compatibility).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data.
        y : ignored
            Not used, present for sklearn API consistency.

        Returns
        -------
        score : float
            Mean log-likelihood.
        """
        return float(np.mean(self.log_prob(X)))

    def sample(self, n_samples: int, key=None):
        """Generate samples from the learned distribution.

        Parameters
        ----------
        n_samples : int
            Number of samples to generate.
        key : jax.random.PRNGKey, optional
            Random key. If None, uses internal key.

        Returns
        -------
        X : jax.numpy.ndarray of shape (n_samples, n_features)
            Generated samples.

        Raises
        ------
        RuntimeError
            If model not fitted.

        Examples
        --------
        >>> samples = inn.sample(1000, key=jax.random.PRNGKey(0))
        >>> print(f"Generated {len(samples)} samples")
        >>>
        >>> # Visualize
        >>> import matplotlib.pyplot as plt
        >>> plt.scatter(samples[:, 0], samples[:, 1], alpha=0.5)
        >>> plt.show()
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        if key is None:
            self.key, key = jax.random.split(self.key)

        # Sample from base distribution (standard normal)
        z = jax.random.normal(key, (n_samples, self.n_features))

        # Transform to data space (inverse handles padding/unpadding)
        x = self.inverse(z)

        return x

    def report(self):
        """Print training statistics and model info.

        Examples
        --------
        >>> inn.fit(X)
        >>> inn.report()
        """
        if not self.is_fitted:
            print("Model not fitted yet. Call fit() first.")
            return

        print("=" * 70)
        print("Invertible Neural Network Summary")
        print("=" * 70)

        print(f"\nArchitecture:")
        print(f"  Input dimensions: {self.n_features}")
        print(f"  Number of coupling layers: {self.n_layers}")
        print(f"  Hidden layer dims: {self.hidden_dims}")
        print(f"  Base distribution: {self.base_dist}")

        print(f"\nTraining:")
        print(f"  Iterations: {self.state_.iter_num}")
        print(f"  Final NLL: {self.final_nll_:.6f}")
        print(f"  Converged: {'Yes' if self.state_.iter_num < self.maxiter else 'No'}")

        print(f"\nData normalization:")
        print(f"  Mean: {self.data_mean_}")
        print(f"  Std: {self.data_std_}")

        print("=" * 70)

    def plot(self, X, n_samples=1000, figsize=(14, 5)):
        """Visualize learned distribution (2D data only).

        Parameters
        ----------
        X : array-like of shape (n_samples, 2)
            Original training data for comparison.
        n_samples : int, default=1000
            Number of samples to generate for visualization.
        figsize : tuple, default=(14, 5)
            Figure size.

        Returns
        -------
        fig : matplotlib.figure.Figure
            The generated figure.

        Raises
        ------
        RuntimeError
            If model not fitted.
        ValueError
            If data is not 2D.

        Examples
        --------
        >>> inn.fit(X_train)
        >>> fig = inn.plot(X_train, n_samples=2000)
        >>> plt.show()
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        if self.n_features != 2:
            raise ValueError(
                f"Plotting only supported for 2D data, got {self.n_features}D"
            )

        X = np.asarray(X)

        # Generate samples
        self.key, sample_key = jax.random.split(self.key)
        samples = self.sample(n_samples, key=sample_key)

        # Transform data to latent space
        z, _ = self.forward(X)

        # Create figure
        fig, axes = plt.subplots(1, 3, figsize=figsize)

        # Plot 1: Original data
        ax = axes[0]
        ax.scatter(X[:, 0], X[:, 1], alpha=0.5, s=10, label='Training data')
        ax.set_xlabel('x₁')
        ax.set_ylabel('x₂')
        ax.set_title('Original Data')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

        # Plot 2: Latent space
        ax = axes[1]
        ax.scatter(z[:, 0], z[:, 1], alpha=0.5, s=10, c='orange', label='Latent repr.')
        ax.set_xlabel('z₁')
        ax.set_ylabel('z₂')
        ax.set_title('Latent Space (should be ~ Gaussian)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

        # Plot 3: Generated samples
        ax = axes[2]
        ax.scatter(samples[:, 0], samples[:, 1], alpha=0.5, s=10, c='green', label='Generated')
        ax.scatter(X[:, 0], X[:, 1], alpha=0.3, s=5, c='gray', label='Original')
        ax.set_xlabel('x₁')
        ax.set_ylabel('x₂')
        ax.set_title(f'Generated Samples (n={n_samples})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

        plt.tight_layout()

        return fig

    def __repr__(self):
        """Return detailed string representation with visual architecture."""
        fitted = "✓ fitted" if self.is_fitted else "✗ not fitted"

        # Create visual architecture representation
        lines = []
        lines.append("╔" + "═" * 68 + "╗")
        lines.append("║" + " InvertibleNN - Normalizing Flow ".center(68) + "║")
        lines.append("╠" + "═" * 68 + "╣")

        # Architecture section
        lines.append("║ Architecture:".ljust(69) + "║")
        lines.append("║   Input: " + f"{self.n_features}D".ljust(59) + "║")

        # Visual flow representation
        lines.append("║   │".ljust(69) + "║")

        for i in range(self.n_layers):
            layer_icon = "├─[Coupling Layer " + f"{i+1}".rjust(2) + "]"
            hidden_str = f"({self.hidden_dims})"
            lines.append("║   " + layer_icon.ljust(40) + hidden_str.ljust(25) + "║")
            if i < self.n_layers - 1:
                lines.append("║   │  ↓".ljust(69) + "║")

        lines.append("║   │".ljust(69) + "║")
        lines.append("║   Output: " + f"{self.n_features}D (latent ~ N(0,I))".ljust(57) + "║")

        # Training status section
        lines.append("╠" + "═" * 68 + "╣")
        lines.append("║ Status: " + fitted.ljust(59) + "║")

        if self.is_fitted:
            lines.append("║   Training iterations: " + f"{self.state_.iter_num}".ljust(44) + "║")
            lines.append("║   Final NLL: " + f"{self.final_nll_:.6f}".ljust(54) + "║")
            converged = "Yes" if self.state_.iter_num < self.maxiter else "No"
            lines.append("║   Converged: " + converged.ljust(54) + "║")

        lines.append("╚" + "═" * 68 + "╝")

        return "\n".join(lines)

    def __str__(self):
        """Return readable string description with architecture diagram."""
        fitted_icon = "✓" if self.is_fitted else "✗"
        fitted_text = "fitted" if self.is_fitted else "not fitted"

        # Create simple flow diagram
        desc_lines = []
        desc_lines.append("=" * 70)
        desc_lines.append(f"Invertible Neural Network [{fitted_icon} {fitted_text}]")
        desc_lines.append("=" * 70)
        desc_lines.append("")

        # Architecture
        desc_lines.append("Architecture:")
        desc_lines.append(f"  Data (X)          : {self.n_features}D")
        desc_lines.append(f"  ↓")
        desc_lines.append(f"  Flow Transform    : {self.n_layers} coupling layers")
        desc_lines.append(f"                      Hidden: {self.hidden_dims}")
        desc_lines.append(f"  ↓")
        desc_lines.append(f"  Latent (Z)        : {self.n_features}D ~ N(0, I)")
        desc_lines.append("")

        # Training info
        if self.is_fitted:
            desc_lines.append("Training:")
            desc_lines.append(f"  Optimizer         : LBFGS")
            desc_lines.append(f"  Iterations        : {self.state_.iter_num}/{self.maxiter}")
            desc_lines.append(f"  Final NLL         : {self.final_nll_:.6f}")

            converged = self.state_.iter_num < self.maxiter
            conv_icon = "✓" if converged else "✗"
            desc_lines.append(f"  Converged         : {conv_icon} {converged}")

            desc_lines.append("")
            desc_lines.append("Normalization:")
            desc_lines.append(f"  Mean              : {self.data_mean_}")
            desc_lines.append(f"  Std               : {self.data_std_}")
        else:
            desc_lines.append("Training: Not yet fitted")
            desc_lines.append("  Call .fit(X) to train the model")

        desc_lines.append("")
        desc_lines.append("Capabilities:")
        desc_lines.append("  • forward(X)      : Transform data → latent")
        desc_lines.append("  • inverse(Z)      : Transform latent → data")
        desc_lines.append("  • log_prob(X)     : Compute exact likelihood")
        desc_lines.append("  • sample(n)       : Generate new samples")
        desc_lines.append("=" * 70)

        return "\n".join(desc_lines)
