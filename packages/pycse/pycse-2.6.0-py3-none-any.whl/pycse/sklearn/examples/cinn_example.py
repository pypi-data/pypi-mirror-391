"""Example usage of Conditional Invertible Neural Networks for Regression.

This example demonstrates:
1. Simple 1D regression with uncertainty
2. Multi-output regression
3. Heteroscedastic noise (varying uncertainty)
4. Uncertainty visualization
"""

import jax
import jax.numpy as np
import matplotlib.pyplot as plt
from pycse.sklearn.cinn import ConditionalInvertibleNN

# Set random seed for reproducibility
jax.config.update("jax_enable_x64", True)


def example_1_linear_regression():
    """Example 1: Simple linear regression with uncertainty."""
    print("=" * 70)
    print("Example 1: Linear Regression with Uncertainty")
    print("=" * 70)

    # Generate linear data with noise
    key = jax.random.PRNGKey(42)
    X = np.linspace(-3, 3, 200)[:, None]
    y_true = 2 * X + 1
    y = y_true + 0.3 * jax.random.normal(key, X.shape)

    # Create and train conditional flow
    cinn = ConditionalInvertibleNN(
        n_features_in=1,
        n_features_out=1,
        n_layers=8,  # More layers for better modeling
        hidden_dims=[128, 128],  # Larger network
        seed=42
    )

    print("\nTraining model...")
    cinn.fit(X, y, maxiter=2000)  # More training for convergence

    # Print training report
    cinn.report()

    # Predict with uncertainty
    print("\nGenerating predictions with uncertainty...")
    y_pred, y_std = cinn.predict(X, return_std=True, n_samples=2000)  # Many samples for smooth estimates

    # Visualize
    print("\nCreating visualization...")
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(X, y, alpha=0.3, s=10, label='Training data', c='gray')
    ax.plot(X, y_pred, 'r-', label='Prediction', linewidth=2)
    ax.fill_between(
        X.ravel(),
        (y_pred - 2*y_std).ravel(),
        (y_pred + 2*y_std).ravel(),
        alpha=0.3,
        color='red',
        label='95% confidence'
    )
    ax.plot(X, y_true, 'k--', label='True function', linewidth=1)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Linear Regression with Uncertainty')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('cinn_linear_regression.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'cinn_linear_regression.png'")

    return cinn, X, y


def example_2_nonlinear_regression():
    """Example 2: Nonlinear regression (sine wave)."""
    print("\n" + "=" * 70)
    print("Example 2: Nonlinear Regression (Sine Wave)")
    print("=" * 70)

    # Generate sine wave data
    key = jax.random.PRNGKey(123)
    X = np.linspace(-2*np.pi, 2*np.pi, 300)[:, None]
    y_true = np.sin(X)
    y = y_true + 0.15 * jax.random.normal(key, X.shape)

    # Train conditional flow
    cinn = ConditionalInvertibleNN(
        n_features_in=1,
        n_features_out=1,
        n_layers=10,
        hidden_dims=[128, 128],
        seed=42
    )

    print("\nTraining on sine wave data...")
    cinn.fit(X, y, maxiter=2000)

    # Predict with uncertainty and samples
    print("\nGenerating predictions...")
    y_pred, y_std, y_samples = cinn.predict(
        X,
        return_std=True,
        return_samples=True,
        n_samples=500
    )

    # Visualize
    print("\nCreating visualization...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left plot: Mean and confidence interval
    ax = axes[0]
    ax.scatter(X, y, alpha=0.3, s=10, label='Training data', c='gray')
    ax.plot(X, y_pred, 'r-', label='Mean prediction', linewidth=2)
    ax.fill_between(
        X.ravel(),
        (y_pred - 2*y_std).ravel(),
        (y_pred + 2*y_std).ravel(),
        alpha=0.3,
        color='red',
        label='95% confidence'
    )
    ax.plot(X, y_true, 'k--', label='True function', linewidth=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Mean Prediction with Uncertainty')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right plot: Sample predictions
    ax = axes[1]
    for i in range(min(20, y_samples.shape[0])):
        ax.plot(X, y_samples[i], 'r-', alpha=0.1, linewidth=0.5)
    ax.scatter(X[::10], y[::10], alpha=0.5, s=20, label='Training data', c='gray')
    ax.plot(X, y_true, 'k--', label='True function', linewidth=2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Sampled Predictions from p(Y|X)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('cinn_sine_regression.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'cinn_sine_regression.png'")

    return cinn


def example_3_heteroscedastic():
    """Example 3: Heteroscedastic regression (varying noise)."""
    print("\n" + "=" * 70)
    print("Example 3: Heteroscedastic Regression")
    print("=" * 70)

    # Generate data with varying noise levels
    key = jax.random.PRNGKey(99)
    X = np.linspace(-3, 3, 250)[:, None]
    y_true = X**2

    # Noise increases with |X|
    noise_std = 0.1 + 0.3 * np.abs(X)
    noise = noise_std * jax.random.normal(key, X.shape)
    y = y_true + noise

    # Train conditional flow
    cinn = ConditionalInvertibleNN(
        n_features_in=1,
        n_features_out=1,
        n_layers=10,  # More layers to capture input-dependent uncertainty
        hidden_dims=[128, 128, 128],  # Deeper network
        seed=42
    )

    print("\nTraining on heteroscedastic data...")
    print("(Noise level varies with X)")
    cinn.fit(X, y, maxiter=2500)  # More training iterations

    # Predict with uncertainty - use many samples for smooth estimate
    y_pred, y_std = cinn.predict(X, return_std=True, n_samples=5000)

    # Apply smoothing to uncertainty for visualization
    from scipy.ndimage import gaussian_filter1d
    y_std_smooth = gaussian_filter1d(y_std.ravel(), sigma=5)

    # Visualize
    print("\nCreating visualization...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left: Data and predictions
    ax = axes[0]
    ax.scatter(X, y, alpha=0.3, s=10, label='Training data', c='gray')
    ax.plot(X, y_pred, 'r-', label='Mean prediction', linewidth=2)
    ax.fill_between(
        X.ravel(),
        (y_pred.ravel() - 2*y_std_smooth),
        (y_pred.ravel() + 2*y_std_smooth),
        alpha=0.3,
        color='red',
        label='95% confidence'
    )
    ax.plot(X, y_true, 'k--', label='True function', linewidth=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Heteroscedastic Regression')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right: Predicted vs actual uncertainty
    ax = axes[1]
    ax.plot(X, noise_std * 2, 'k--', label='True noise (2σ)', linewidth=2)
    ax.plot(X, y_std_smooth * 2, 'r-', label='Learned uncertainty (2σ, smoothed)', linewidth=2, alpha=0.8)
    ax.set_xlabel('X')
    ax.set_ylabel('Uncertainty (2σ)')
    ax.set_title('Model Learns Input-Dependent Uncertainty!')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('cinn_heteroscedastic.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'cinn_heteroscedastic.png'")
    print("\nNote: The model learns input-dependent uncertainty!")

    return cinn


def example_4_multioutput():
    """Example 4: Multi-output regression."""
    print("\n" + "=" * 70)
    print("Example 4: Multi-Output Regression")
    print("=" * 70)

    # Generate 2D output from 1D input (parametric curve)
    key = jax.random.PRNGKey(77)
    t = np.linspace(0, 2*np.pi, 200)[:, None]

    # Lissajous curve with noise
    x_true = np.sin(3*t)
    y_true = np.cos(2*t)

    x = x_true + 0.1 * jax.random.normal(key, x_true.shape)
    y = y_true + 0.1 * jax.random.normal(key, y_true.shape)

    Y = np.concatenate([x, y], axis=1)  # Shape: (200, 2)

    # Train multi-output model
    cinn = ConditionalInvertibleNN(
        n_features_in=1,   # Input: t
        n_features_out=2,  # Output: (x, y)
        n_layers=8,
        hidden_dims=[128, 128],
        seed=42
    )

    print("\nTraining multi-output model...")
    print("Input: t (time)")
    print("Output: (x, y) coordinates")
    cinn.fit(t, Y, maxiter=1200)

    # Predict
    Y_pred, Y_std = cinn.predict(t, return_std=True, n_samples=100)

    # Visualize
    print("\nCreating visualization...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Left: X output
    ax = axes[0]
    ax.scatter(t, x, alpha=0.3, s=10, label='Training data (x)', c='gray')
    ax.plot(t, Y_pred[:, 0], 'r-', label='Prediction (x)', linewidth=2)
    ax.fill_between(
        t.ravel(),
        (Y_pred[:, 0] - 2*Y_std[:, 0]).ravel(),
        (Y_pred[:, 0] + 2*Y_std[:, 0]).ravel(),
        alpha=0.3,
        color='red'
    )
    ax.plot(t, x_true, 'k--', label='True x', linewidth=1)
    ax.set_xlabel('t')
    ax.set_ylabel('x')
    ax.set_title('X Component')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Middle: Y output
    ax = axes[1]
    ax.scatter(t, y, alpha=0.3, s=10, label='Training data (y)', c='gray')
    ax.plot(t, Y_pred[:, 1], 'r-', label='Prediction (y)', linewidth=2)
    ax.fill_between(
        t.ravel(),
        (Y_pred[:, 1] - 2*Y_std[:, 1]).ravel(),
        (Y_pred[:, 1] + 2*Y_std[:, 1]).ravel(),
        alpha=0.3,
        color='red'
    )
    ax.plot(t, y_true, 'k--', label='True y', linewidth=1)
    ax.set_xlabel('t')
    ax.set_ylabel('y')
    ax.set_title('Y Component')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right: Parametric curve
    ax = axes[2]
    ax.scatter(x, y, alpha=0.3, s=10, label='Training data', c='gray')
    ax.plot(Y_pred[:, 0], Y_pred[:, 1], 'r-', label='Prediction', linewidth=2)
    ax.plot(x_true, y_true, 'k--', label='True curve', linewidth=1)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Parametric Curve (x,y)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig('cinn_multioutput.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'cinn_multioutput.png'")

    return cinn


def example_5_extrapolation():
    """Example 5: Uncertainty in extrapolation."""
    print("\n" + "=" * 70)
    print("Example 5: Uncertainty in Extrapolation")
    print("=" * 70)

    # Train on limited range
    key = jax.random.PRNGKey(55)
    X_train = np.linspace(-2, 2, 150)[:, None]
    y_train = X_train**2 + 0.2 * jax.random.normal(key, X_train.shape)

    # Test on wider range (including extrapolation)
    X_test = np.linspace(-4, 4, 300)[:, None]

    # Train model
    cinn = ConditionalInvertibleNN(
        n_features_in=1,
        n_features_out=1,
        n_layers=8,
        hidden_dims=[64, 64],
        seed=42
    )

    print("\nTraining on X ∈ [-2, 2]...")
    cinn.fit(X_train, y_train, maxiter=1000)

    # Predict on full range
    print("Predicting on X ∈ [-4, 4] (includes extrapolation)...")
    y_pred, y_std = cinn.predict(X_test, return_std=True, n_samples=150)

    # Visualize
    print("\nCreating visualization...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left: Predictions with uncertainty
    ax = axes[0]
    ax.scatter(X_train, y_train, alpha=0.5, s=20, label='Training data', c='blue')
    ax.plot(X_test, y_pred, 'r-', label='Prediction', linewidth=2)
    ax.fill_between(
        X_test.ravel(),
        (y_pred - 2*y_std).ravel(),
        (y_pred + 2*y_std).ravel(),
        alpha=0.3,
        color='red',
        label='95% confidence'
    )

    # Mark training region
    ax.axvline(-2, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(2, color='gray', linestyle='--', alpha=0.5)
    ax.text(-2.5, ax.get_ylim()[1] * 0.9, 'Extrapolation', fontsize=10)
    ax.text(0, ax.get_ylim()[1] * 0.9, 'Interpolation', fontsize=10, ha='center')
    ax.text(2.5, ax.get_ylim()[1] * 0.9, 'Extrapolation', fontsize=10)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Predictions with Uncertainty')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right: Uncertainty vs X
    ax = axes[1]
    ax.plot(X_test, y_std, 'r-', linewidth=2)
    ax.axvline(-2, color='gray', linestyle='--', alpha=0.5, label='Training bounds')
    ax.axvline(2, color='gray', linestyle='--', alpha=0.5)
    ax.fill_between([-4, -2], 0, ax.get_ylim()[1], alpha=0.1, color='orange', label='Extrapolation region')
    ax.fill_between([2, 4], 0, ax.get_ylim()[1], alpha=0.1, color='orange')
    ax.set_xlabel('X')
    ax.set_ylabel('Predictive Uncertainty (σ)')
    ax.set_title('Uncertainty Increases in Extrapolation')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('cinn_extrapolation.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'cinn_extrapolation.png'")
    print("\nNote: Uncertainty increases outside the training range!")

    return cinn


if __name__ == '__main__':
    print("Running Conditional Invertible NN Regression Examples\n")

    # Example 1: Linear regression
    cinn1, X1, y1 = example_1_linear_regression()

    # Example 2: Nonlinear regression
    cinn2 = example_2_nonlinear_regression()

    # Example 3: Heteroscedastic regression
    cinn3 = example_3_heteroscedastic()

    # Example 4: Multi-output regression
    cinn4 = example_4_multioutput()

    # Example 5: Extrapolation uncertainty
    cinn5 = example_5_extrapolation()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Regression with uncertainty quantification")
    print("  ✓ Heteroscedastic (input-dependent) uncertainty")
    print("  ✓ Multi-output predictions")
    print("  ✓ Extrapolation uncertainty")
    print("  ✓ Full predictive distribution via sampling")
    print("\nGenerated visualizations:")
    print("  - cinn_linear_regression.png")
    print("  - cinn_sine_regression.png")
    print("  - cinn_heteroscedastic.png")
    print("  - cinn_multioutput.png")
    print("  - cinn_extrapolation.png")
    print("=" * 70)
