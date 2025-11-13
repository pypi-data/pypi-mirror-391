"""Conditional Invertible Neural Networks for Regression with Uncertainty.

This module provides conditional normalizing flows for regression tasks. Unlike
standard regression models, ConditionalInvertibleNN learns the full conditional
distribution p(Y|X), enabling:

- Point predictions (mean)
- Uncertainty quantification (standard deviation)
- Full predictive distribution sampling
- Exact likelihood computation

Key Differences from InvertibleNN:
----------------------------------
- **InvertibleNN**: Learns p(X) - density estimation
- **ConditionalInvertibleNN**: Learns p(Y|X) - regression

Mathematical Foundation:
-----------------------
The model learns a conditional bijective transformation f(Y|X) such that:

    log p(y|x) = log p(z) + log |det(∂f/∂y)|

where z = f(y|x) and p(z) is a simple base distribution (Gaussian).

The conditioning on X means each layer's transformation depends on the input features,
allowing the model to learn input-dependent distributions over outputs.

Classes:
-------
ConditionalInvertibleNN
    sklearn-compatible conditional flow for regression with uncertainty quantification.

Examples:
--------
Basic regression with uncertainty:

>>> import jax.numpy as np
>>> from pycse.sklearn.cinn import ConditionalInvertibleNN
>>>
>>> # Generate regression data
>>> X = np.linspace(0, 10, 200)[:, None]
>>> y = np.sin(X) + 0.1 * np.random.randn(*X.shape)
>>>
>>> # Train conditional flow
>>> cinn = ConditionalInvertibleNN(n_features_in=1, n_features_out=1,
...                                  n_layers=6, hidden_dims=[64, 64])
>>> cinn.fit(X, y)
>>>
>>> # Predict with uncertainty
>>> X_test = np.array([[5.0]])
>>> y_pred, y_std = cinn.predict(X_test, return_std=True)
>>> print(f"Prediction: {y_pred[0]:.3f} ± {2*y_std[0]:.3f}")
>>>
>>> # Sample from predictive distribution
>>> y_samples = cinn.sample(X_test, n_samples=100)
>>> print(f"Sampled predictions shape: {y_samples.shape}")  # (100, 1)

References:
----------
.. [1] Ardizzone et al., "Analyzing Inverse Problems with Invertible Neural Networks",
       ICLR 2019
.. [2] Winkler et al., "Learning Likelihoods with Conditional Normalizing Flows",
       arXiv:1912.00042
"""

import os
import jax
import jax.numpy as np
from jax import jit, vmap, value_and_grad
from jaxopt import LBFGS
from sklearn.base import BaseEstimator, RegressorMixin
from flax import linen as nn
from typing import List, Tuple
import matplotlib.pyplot as plt

# Enable 64-bit precision
os.environ["JAX_ENABLE_X64"] = "True"
jax.config.update("jax_enable_x64", True)


class _ConditionalCouplingLayer(nn.Module):
    """Conditional affine coupling layer for regression.

    This implements a coupling layer where the transformation depends on
    both the input (Y being transformed) and the conditioning context (X).

    Attributes
    ----------
    hidden_dims : list of int
        Hidden layer dimensions for scale/shift networks.
    n_features_out : int
        Output dimensionality (Y dimension).
    n_features_in : int
        Input dimensionality (X dimension for conditioning).
    split_idx : int
        Where to split Y features.
    """

    hidden_dims: List[int]
    n_features_out: int
    n_features_in: int
    split_idx: int

    @nn.compact
    def __call__(self, y_or_z, x_context, inverse=False):
        """Apply transformation (forward or inverse).

        Parameters
        ----------
        y_or_z : array
            Input (Y for forward, Z for inverse)
        x_context : array
            Conditioning context X
        inverse : bool
            If True, apply inverse transformation

        Returns
        -------
        result : array or tuple
            Transformed output (and log_det if not inverse)
        """
        # Split input
        unchanged = y_or_z[:, :self.split_idx]
        to_transform = y_or_z[:, self.split_idx:]

        # Concatenate unchanged part with conditioning context X
        h = np.concatenate([unchanged, x_context], axis=1)

        # Number of output dimensions
        n_out = self.n_features_out - self.split_idx

        # Compute scale parameters
        h_scale = h
        for i, dim in enumerate(self.hidden_dims):
            h_scale = nn.Dense(dim, name=f'scale_{i}')(h_scale)
            h_scale = nn.swish(h_scale)
        log_scale = nn.Dense(n_out, name='scale_out')(h_scale)
        log_scale = np.tanh(log_scale)  # Bound for stability

        # Compute shift parameters
        h_shift = h
        for i, dim in enumerate(self.hidden_dims):
            h_shift = nn.Dense(dim, name=f'shift_{i}')(h_shift)
            h_shift = nn.swish(h_shift)
        shift = nn.Dense(n_out, name='shift_out')(h_shift)

        if inverse:
            # Inverse: z → y
            transformed = (to_transform - shift) * np.exp(-log_scale)
            result = np.concatenate([unchanged, transformed], axis=1)
            return result
        else:
            # Forward: y → z
            transformed = to_transform * np.exp(log_scale) + shift
            result = np.concatenate([unchanged, transformed], axis=1)
            log_det = np.sum(log_scale, axis=1)
            return result, log_det


class _ConditionalFlowModel(nn.Module):
    """Conditional normalizing flow model.

    Attributes
    ----------
    n_features_out : int
        Output dimensionality.
    n_features_in : int
        Input dimensionality (for conditioning).
    n_layers : int
        Number of coupling layers.
    hidden_dims : list of int
        Hidden dimensions for coupling networks.
    """

    n_features_out: int
    n_features_in: int
    n_layers: int
    hidden_dims: List[int]

    def _get_split_idx(self, layer_idx):
        """Get split index for layer."""
        if layer_idx % 2 == 0:
            return self.n_features_out // 2
        else:
            return self.n_features_out - self.n_features_out // 2

    def _get_permutation(self):
        """Get permutation indices for dimension shuffling.

        For 3D (padded 1D), we use a rotation: [0,1,2] -> [1,2,0]
        This ensures Y (at position 1) cycles through all positions.
        For other dimensions, we reverse: [0,1,2,...,n-1] -> [n-1,...,2,1,0]
        """
        if self.n_features_out == 3:
            # Rotate for 3D (padded 1D case)
            return np.array([1, 2, 0])
        else:
            # Reverse for other cases
            return np.arange(self.n_features_out)[::-1]

    def _permute(self, x, inverse=False):
        """Apply permutation to shuffle dimensions."""
        perm = self._get_permutation()
        if inverse:
            # Inverse permutation
            inv_perm = np.argsort(perm)
            return x[:, inv_perm]
        else:
            return x[:, perm]

    @nn.compact
    def __call__(self, y, x_context, inverse=False):
        """Forward or inverse conditional transformation.

        Parameters
        ----------
        y : array
            Output values (forward) or latent (inverse).
        x_context : array
            Conditioning context X.
        inverse : bool
            If True, perform inverse transformation.

        Returns
        -------
        result : array or tuple
            Transformed values (and log_det if forward).
        """
        if inverse:
            # Inverse: z → y conditioned on x
            result = y
            for i in reversed(range(self.n_layers)):
                split_idx = self._get_split_idx(i)
                layer = _ConditionalCouplingLayer(
                    hidden_dims=self.hidden_dims,
                    n_features_out=self.n_features_out,
                    n_features_in=self.n_features_in,
                    split_idx=split_idx,
                    name=f'coupling_{i}'
                )
                result = layer(result, x_context, inverse=True)
                # Apply inverse permutation after each layer (except first in reverse order)
                if i > 0:
                    result = self._permute(result, inverse=True)
            return result
        else:
            # Forward: y → z conditioned on x
            z = y
            log_det_sum = np.zeros(y.shape[0])

            for i in range(self.n_layers):
                split_idx = self._get_split_idx(i)
                layer = _ConditionalCouplingLayer(
                    hidden_dims=self.hidden_dims,
                    n_features_out=self.n_features_out,
                    n_features_in=self.n_features_in,
                    split_idx=split_idx,
                    name=f'coupling_{i}'
                )
                z, log_det = layer(z, x_context, inverse=False)
                log_det_sum += log_det
                # Apply permutation after each layer (except last)
                if i < self.n_layers - 1:
                    z = self._permute(z, inverse=False)

            return z, log_det_sum


class ConditionalInvertibleNN(BaseEstimator, RegressorMixin):
    """Conditional Invertible Neural Network for regression with uncertainty.

    This model learns the conditional distribution p(Y|X) using normalizing flows,
    enabling both point predictions and uncertainty quantification.

    Parameters
    ----------
    n_features_in : int
        Number of input features (X dimensionality).
    n_features_out : int
        Number of output features (Y dimensionality).
    n_layers : int, default=6
        Number of coupling layers.
    hidden_dims : list of int, default=[64, 64]
        Hidden layer architecture for coupling networks.
    seed : int, default=42
        Random seed for reproducibility.

    Attributes
    ----------
    flow : _ConditionalFlowModel
        Internal conditional flow model.
    params_ : dict
        Trained parameters (available after fit()).
    X_mean_, X_std_ : array
        Input normalization parameters.
    y_mean_, y_std_ : array
        Output normalization parameters.

    Methods
    -------
    fit(X, y, **kwargs)
        Train the model on data.
    predict(X, return_std=False, return_samples=False, n_samples=100)
        Make predictions with optional uncertainty.
    sample(X, n_samples=100)
        Sample from conditional distribution p(Y|X).
    score(X, y)
        Return negative log-likelihood (higher is better).

    Examples
    --------
    Simple 1D regression:

    >>> import numpy as np
    >>> from pycse.sklearn.cinn import ConditionalInvertibleNN
    >>>
    >>> # Generate data
    >>> X = np.linspace(0, 10, 100)[:, None]
    >>> y = np.sin(X) + 0.1 * np.random.randn(*X.shape)
    >>>
    >>> # Fit model
    >>> cinn = ConditionalInvertibleNN(n_features_in=1, n_features_out=1)
    >>> cinn.fit(X, y)
    >>>
    >>> # Predict with uncertainty
    >>> y_pred, y_std = cinn.predict(X, return_std=True)
    >>> print(f"Mean prediction error: {np.mean((y_pred - y)**2):.3f}")

    Multi-output regression:

    >>> # 2D input, 3D output
    >>> X = np.random.randn(200, 2)
    >>> y = np.random.randn(200, 3)
    >>>
    >>> cinn = ConditionalInvertibleNN(n_features_in=2, n_features_out=3,
    ...                                  n_layers=8, hidden_dims=[128, 128])
    >>> cinn.fit(X, y)
    >>> y_pred = cinn.predict(X[:10])
    """

    def __init__(
        self,
        n_features_in: int,
        n_features_out: int,
        n_layers: int = 6,
        hidden_dims: List[int] = None,
        seed: int = 42
    ):
        """Initialize ConditionalInvertibleNN."""
        if hidden_dims is None:
            hidden_dims = [64, 64]

        # Validate
        if n_features_in < 1:
            raise ValueError(f"n_features_in must be >= 1, got {n_features_in}")
        if n_features_out < 1:
            raise ValueError(f"n_features_out must be >= 1, got {n_features_out}")
        if n_layers < 1:
            raise ValueError(f"n_layers must be >= 1, got {n_layers}")

        self.n_features_in = n_features_in
        self.n_features_out = n_features_out
        self.n_layers = n_layers
        self.hidden_dims = hidden_dims
        self.seed = seed

        # Handle 1D output by padding to 3D internally
        # Permutations ensure Y gets transformed in all layers
        self._needs_output_padding = (n_features_out == 1)
        self._internal_n_out = 3 if self._needs_output_padding else n_features_out

        self.key = jax.random.PRNGKey(seed)
        self.flow = _ConditionalFlowModel(
            n_features_out=self._internal_n_out,  # Use padded dimension
            n_features_in=n_features_in,
            n_layers=n_layers,
            hidden_dims=hidden_dims
        )

        # Cache for JIT-compiled functions (created after fitting)
        self._inverse_flow_batched = None

    @property
    def is_fitted(self):
        """Check if model is fitted."""
        return hasattr(self, 'params_')

    def _pad_1d_output(self, y):
        """Pad 1D output to 3D for internal processing.

        Parameters
        ----------
        y : array of shape (n_samples, 1)
            1D output data.

        Returns
        -------
        y_padded : array of shape (n_samples, 3)
            Padded output with zeros. Y is placed in the middle position.
        """
        if not self._needs_output_padding:
            return y
        # Pad with zeros to make 3D, placing Y in middle position (dim 1)
        # Permutations ensure Y visits all positions
        # Layout: [pad, Y, pad]
        return np.concatenate([
            np.zeros_like(y),
            y,
            np.zeros_like(y)
        ], axis=1)

    def _unpad_1d_output(self, y_padded):
        """Remove padding from output.

        Parameters
        ----------
        y_padded : array of shape (n_samples, 3)
            Padded output data with layout [pad, Y, pad].

        Returns
        -------
        y : array of shape (n_samples, 1)
            Original 1D output from middle position.
        """
        if not self._needs_output_padding:
            return y_padded
        # Extract Y from middle position (dimension 1)
        return y_padded[:, 1:2]

    def fit(self, X, y, normalize=True, **kwargs):
        """Train conditional flow by maximizing likelihood.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features_in)
            Input features.
        y : array-like of shape (n_samples, n_features_out) or (n_samples,)
            Target values.
        normalize : bool, default=True
            Whether to normalize inputs and outputs.
        **kwargs : dict
            Additional arguments for LBFGS:
            - maxiter : int, default=2000
            - tol : float, default=1e-5

        Returns
        -------
        self
        """
        X = np.asarray(X)
        y = np.asarray(y)

        # Validate shapes
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got shape {X.shape}")
        if y.ndim == 1:
            y = y[:, None]
        if y.ndim != 2:
            raise ValueError(f"y must be 1D or 2D, got shape {y.shape}")
        if len(X) != len(y):
            raise ValueError(f"X and y length mismatch: {len(X)} vs {len(y)}")
        if X.shape[1] != self.n_features_in:
            raise ValueError(
                f"X has {X.shape[1]} features, expected {self.n_features_in}"
            )
        if y.shape[1] != self.n_features_out:
            raise ValueError(
                f"y has {y.shape[1]} features, expected {self.n_features_out}"
            )

        # Normalize
        if normalize:
            self.X_mean_ = np.mean(X, axis=0)
            self.X_std_ = np.std(X, axis=0) + 1e-8
            self.y_mean_ = np.mean(y, axis=0)
            self.y_std_ = np.std(y, axis=0) + 1e-8

            X_norm = (X - self.X_mean_) / self.X_std_
            y_norm = (y - self.y_mean_) / self.y_std_
        else:
            self.X_mean_ = np.zeros(self.n_features_in)
            self.X_std_ = np.ones(self.n_features_in)
            self.y_mean_ = np.zeros(self.n_features_out)
            self.y_std_ = np.ones(self.n_features_out)

            X_norm = X
            y_norm = y

        # Pad if 1D output
        y_norm_padded = self._pad_1d_output(y_norm)

        # Initialize parameters
        self.key, init_key = jax.random.split(self.key)
        dummy_y = np.zeros((1, self._internal_n_out))  # Use internal dimension
        dummy_x = np.zeros((1, self.n_features_in))
        params = self.flow.init(init_key, dummy_y, dummy_x)

        # NLL loss
        @jit
        def nll_loss(params, X_batch, y_batch_padded):
            """Negative log-likelihood of p(y|x)."""
            # Forward: y → z | x
            z, log_det = self.flow.apply(params, y_batch_padded, X_batch)

            # Base distribution: p(z) = N(0, I)
            log_pz = -0.5 * np.sum(z**2, axis=1) - 0.5 * self._internal_n_out * np.log(2 * np.pi)

            # p(y|x) via change of variables
            log_py_given_x = log_pz + log_det

            return -np.mean(log_py_given_x)

        # Optimizer settings
        if 'maxiter' not in kwargs:
            kwargs['maxiter'] = 2000
        if 'tol' not in kwargs:
            kwargs['tol'] = 1e-5

        self.maxiter = kwargs['maxiter']

        # Train
        solver = LBFGS(fun=value_and_grad(nll_loss), value_and_grad=True, **kwargs)
        self.params_, self.state_ = solver.run(params, X_norm, y_norm_padded)
        self.final_nll_ = float(self.state_.value)

        # Clear cached JIT functions since params changed
        self._inverse_flow_batched = None

        return self

    def predict(self, X, return_std=False, return_samples=False, n_samples=100):
        """Predict outputs with optional uncertainty quantification.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features_in)
            Input features.
        return_std : bool, default=False
            If True, return standard deviation.
        return_samples : bool, default=False
            If True, return sampled predictions.
        n_samples : int, default=100
            Number of samples for uncertainty (if return_std or return_samples).

        Returns
        -------
        y_pred : array of shape (n_samples, n_features_out)
            Mean predictions.
        y_std : array of shape (n_samples, n_features_out), optional
            Predictive standard deviation (if return_std=True).
        y_samples : array of shape (n_samples_pred, n_samples, n_features_out), optional
            Sampled predictions (if return_samples=True).

        Examples
        --------
        >>> y_pred = cinn.predict(X_test)
        >>> y_pred, y_std = cinn.predict(X_test, return_std=True)
        >>> y_pred, y_samples = cinn.predict(X_test, return_samples=True)
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        X = np.asarray(X)
        if X.ndim == 1:
            X = X[:, None]

        # Normalize X
        X_norm = (X - self.X_mean_) / self.X_std_

        if return_std or return_samples:
            # Sample from conditional distribution
            samples = self.sample(X, n_samples=n_samples)  # (n_samples, n_data, n_out)

            # Mean prediction
            y_pred = np.mean(samples, axis=0)

            if return_samples and return_std:
                y_std = np.std(samples, axis=0)
                return y_pred, y_std, samples
            elif return_samples:
                return y_pred, samples
            else:  # return_std only
                y_std = np.std(samples, axis=0)
                return y_pred, y_std
        else:
            # Mode/mean approximation: map from mode of base distribution
            z_mode = np.zeros((len(X_norm), self._internal_n_out))  # Use internal dimension
            y_norm_padded = self.flow.apply(self.params_, z_mode, X_norm, inverse=True)
            y_norm = self._unpad_1d_output(y_norm_padded)  # Unpad if needed
            y_pred = y_norm * self.y_std_ + self.y_mean_

            return y_pred

    def sample(self, X, n_samples=100, key=None):
        """Sample from conditional distribution p(Y|X).

        Parameters
        ----------
        X : array-like of shape (n_data, n_features_in)
            Input features to condition on.
        n_samples : int, default=100
            Number of samples to draw for each input.
        key : jax.random.PRNGKey, optional
            Random key.

        Returns
        -------
        y_samples : array of shape (n_samples, n_data, n_features_out)
            Samples from p(Y|X).
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        if key is None:
            self.key, key = jax.random.split(self.key)

        X = np.asarray(X)
        if X.ndim == 1:
            X = X[:, None]

        X_norm = (X - self.X_mean_) / self.X_std_

        # Sample from base distribution (use internal dimension)
        z = jax.random.normal(key, (n_samples, len(X), self._internal_n_out))

        # Transform through inverse flow conditioned on X
        # Use vmap to vectorize over samples for massive speedup!
        # Cache the JIT-compiled batched function for reuse
        if self._inverse_flow_batched is None:
            @jit
            def inverse_flow_single(z_single, x_context):
                """Apply inverse flow to a single sample batch."""
                return self.flow.apply(self.params_, z_single, x_context, inverse=True)

            # Vectorize over the first dimension (n_samples) and JIT compile
            # vmap in_axes: (0, None) means vectorize over z but broadcast x_context
            self._inverse_flow_batched = jit(vmap(inverse_flow_single, in_axes=(0, None)))

        y_samples_norm_padded = self._inverse_flow_batched(z, X_norm)

        # Unpad if needed (vectorized)
        if self._needs_output_padding:
            # Extract middle dimension (position 1 for 3D) for all samples at once
            y_samples_norm = y_samples_norm_padded[:, :, 1:2]
        else:
            y_samples_norm = y_samples_norm_padded

        # Denormalize
        y_samples = y_samples_norm * self.y_std_ + self.y_mean_

        return y_samples

    def score(self, X, y):
        """Compute negative log-likelihood (higher is better).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features_in)
            Input features.
        y : array-like of shape (n_samples, n_features_out)
            Target values.

        Returns
        -------
        score : float
            Negative NLL (higher is better for sklearn compatibility).
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        X = np.asarray(X)
        y = np.asarray(y)
        if y.ndim == 1:
            y = y[:, None]

        # Normalize
        X_norm = (X - self.X_mean_) / self.X_std_
        y_norm = (y - self.y_mean_) / self.y_std_

        # Pad if needed
        y_norm_padded = self._pad_1d_output(y_norm)

        # Compute NLL
        z, log_det = self.flow.apply(self.params_, y_norm_padded, X_norm)
        log_pz = -0.5 * np.sum(z**2, axis=1) - 0.5 * self._internal_n_out * np.log(2 * np.pi)
        log_py_given_x = log_pz + log_det

        # Return negative NLL (higher is better)
        return float(np.mean(log_py_given_x))

    def report(self):
        """Print training statistics."""
        if not self.is_fitted:
            print("Model not fitted yet.")
            return

        print("=" * 70)
        print("Conditional Invertible NN Summary")
        print("=" * 70)
        print(f"\nArchitecture:")
        print(f"  Input features (X):  {self.n_features_in}")
        print(f"  Output features (Y): {self.n_features_out}")
        print(f"  Coupling layers:     {self.n_layers}")
        print(f"  Hidden dims:         {self.hidden_dims}")
        print(f"\nTraining:")
        print(f"  Iterations:          {self.state_.iter_num}")
        print(f"  Final NLL:           {self.final_nll_:.6f}")
        print(f"  Converged:           {'Yes' if self.state_.iter_num < self.maxiter else 'No'}")
        print("=" * 70)

    def __repr__(self):
        """Visual representation."""
        fitted = "✓ fitted" if self.is_fitted else "✗ not fitted"

        lines = []
        lines.append("╔" + "═" * 68 + "╗")
        lines.append("║" + " Conditional InvertibleNN - Regression ".center(68) + "║")
        lines.append("╠" + "═" * 68 + "╣")

        lines.append("║ Architecture:".ljust(69) + "║")
        lines.append("║   Input (X):  " + f"{self.n_features_in}D".ljust(54) + "║")
        lines.append("║   │".ljust(69) + "║")

        for i in range(self.n_layers):
            layer_str = f"├─[Conditional Layer {i+1:2d}] (hidden: {self.hidden_dims})"
            lines.append("║   " + layer_str.ljust(65) + "║")
            if i < self.n_layers - 1:
                lines.append("║   │  ↓ (conditioned on X)".ljust(69) + "║")

        lines.append("║   │".ljust(69) + "║")
        lines.append("║   Output (Y): " + f"{self.n_features_out}D".ljust(54) + "║")

        lines.append("╠" + "═" * 68 + "╣")
        lines.append("║ Status: " + fitted.ljust(59) + "║")

        if self.is_fitted:
            lines.append("║   Training iterations: " + f"{self.state_.iter_num}".ljust(44) + "║")
            lines.append("║   Final NLL: " + f"{self.final_nll_:.6f}".ljust(54) + "║")

        lines.append("╚" + "═" * 68 + "╝")

        return "\n".join(lines)

    def __str__(self):
        """Readable description."""
        fitted = "✓ fitted" if self.is_fitted else "✗ not fitted"

        desc = []
        desc.append("=" * 70)
        desc.append(f"Conditional Invertible NN [{fitted}]")
        desc.append("=" * 70)
        desc.append("")
        desc.append("Regression Model: X → Y with uncertainty")
        desc.append("")
        desc.append("Architecture:")
        desc.append(f"  Input (X)         : {self.n_features_in}D")
        desc.append(f"  ↓")
        desc.append(f"  Conditional Flow  : {self.n_layers} coupling layers")
        desc.append(f"                      Hidden: {self.hidden_dims}")
        desc.append(f"  ↓")
        desc.append(f"  Output (Y)        : {self.n_features_out}D")
        desc.append("")

        if self.is_fitted:
            desc.append("Training:")
            desc.append(f"  Iterations        : {self.state_.iter_num}/{self.maxiter}")
            desc.append(f"  Final NLL         : {self.final_nll_:.6f}")
            desc.append("")

        desc.append("Capabilities:")
        desc.append("  • predict(X)              : Mean prediction")
        desc.append("  • predict(X, return_std)  : Mean + uncertainty")
        desc.append("  • sample(X, n_samples)    : Sample from p(Y|X)")
        desc.append("  • score(X, y)             : Log-likelihood")
        desc.append("=" * 70)

        return "\n".join(desc)
