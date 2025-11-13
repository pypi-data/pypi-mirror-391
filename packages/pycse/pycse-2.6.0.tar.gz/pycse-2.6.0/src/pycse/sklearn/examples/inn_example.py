"""Example usage of Invertible Neural Networks (Normalizing Flows).

This example demonstrates:
1. Training an INN on 2D data
2. Generating new samples
3. Computing likelihoods
4. Anomaly detection
5. Visualization
"""

import jax
import jax.numpy as np
from sklearn.datasets import make_moons
import matplotlib.pyplot as plt
from pycse.sklearn.inn import InvertibleNN

# Set random seed for reproducibility
jax.config.update("jax_enable_x64", True)


def example_1_basic_usage():
    """Example 1: Basic density estimation on moons dataset."""
    print("=" * 70)
    print("Example 1: Basic Density Estimation")
    print("=" * 70)

    # Generate 2D moons dataset
    X, _ = make_moons(n_samples=1000, noise=0.05, random_state=42)
    X = np.array(X)

    # Create and train invertible NN
    inn = InvertibleNN(n_features=2, n_layers=8, hidden_dims=[64, 64], seed=42)
    print("\nTraining model...")
    inn.fit(X, maxiter=1000)

    # Print training report
    inn.report()

    # Generate new samples
    print("\nGenerating 500 new samples...")
    samples = inn.sample(500, key=jax.random.PRNGKey(123))

    # Compute likelihoods
    log_probs = inn.log_prob(X[:100])
    print(f"\nMean log-likelihood on training data: {np.mean(log_probs):.3f}")

    # Visualize
    print("\nCreating visualization...")
    fig = inn.plot(X, n_samples=500)
    plt.savefig('inn_moons_example.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'inn_moons_example.png'")

    return inn, X


def example_2_anomaly_detection():
    """Example 2: Anomaly detection using likelihood."""
    print("\n" + "=" * 70)
    print("Example 2: Anomaly Detection")
    print("=" * 70)

    # Generate normal data (2D Gaussian)
    key = jax.random.PRNGKey(42)
    X_train = jax.random.normal(key, (500, 2))

    # Train INN on normal data
    inn = InvertibleNN(n_features=2, n_layers=6, hidden_dims=[64, 64])
    print("\nTraining on normal data...")
    inn.fit(X_train, maxiter=800)

    # Test points: some normal, some outliers
    X_test = np.array([
        [0.0, 0.0],    # Normal (near center)
        [0.5, 0.5],    # Normal
        [1.0, 1.0],    # Normal
        [5.0, 5.0],    # Outlier (far from center)
        [10.0, 10.0],  # Strong outlier
    ])

    # Compute log probabilities
    log_probs = inn.log_prob(X_test)

    print("\nAnomaly Detection Results:")
    print(f"{'Point':<20} {'Log-Prob':<15} {'Anomaly?':<10}")
    print("-" * 45)

    # Use a threshold (e.g., 5th percentile)
    train_lp = inn.log_prob(X_train)
    threshold = np.percentile(train_lp, 5)

    for i, (point, lp) in enumerate(zip(X_test, log_probs)):
        is_anomaly = "YES" if lp < threshold else "NO"
        print(f"{str(point):<20} {lp:<15.3f} {is_anomaly:<10}")

    print(f"\nThreshold (5th percentile): {threshold:.3f}")

    return inn


def example_3_forward_inverse():
    """Example 3: Demonstrate forward and inverse transformations."""
    print("\n" + "=" * 70)
    print("Example 3: Forward and Inverse Transformations")
    print("=" * 70)

    # Generate simple 2D data
    key = jax.random.PRNGKey(42)
    X = jax.random.normal(key, (200, 2))

    # Train INN
    inn = InvertibleNN(n_features=2, n_layers=6, hidden_dims=[32, 32])
    print("\nTraining model...")
    inn.fit(X, maxiter=500)

    # Forward transformation (data → latent)
    print("\nForward transformation (X → Z)...")
    Z, log_det = inn.forward(X[:5])
    print(f"Original data shape: {X[:5].shape}")
    print(f"Latent shape: {Z.shape}")
    print(f"First latent vector: {Z[0]}")

    # Inverse transformation (latent → data)
    print("\nInverse transformation (Z → X)...")
    X_reconstructed = inn.inverse(Z)
    print(f"Reconstructed shape: {X_reconstructed.shape}")

    # Check reconstruction error
    error = np.max(np.abs(X[:5] - X_reconstructed))
    print(f"\nMax reconstruction error: {error:.2e}")
    print(f"Invertibility verified: {error < 1e-5}")

    return inn


def example_4_sampling():
    """Example 4: Generate diverse samples."""
    print("\n" + "=" * 70)
    print("Example 4: Generating Diverse Samples")
    print("=" * 70)

    # Create spiral data
    key = jax.random.PRNGKey(42)
    n_points = 500
    theta = np.linspace(0, 4 * np.pi, n_points)
    r = theta / (4 * np.pi)
    X = np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)
    X = X + 0.05 * jax.random.normal(key, X.shape)

    # Train INN
    inn = InvertibleNN(n_features=2, n_layers=10, hidden_dims=[64, 64])
    print("\nTraining on spiral data...")
    inn.fit(X, maxiter=1500)

    # Generate multiple sample sets with different random keys
    print("\nGenerating samples with different random seeds...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for i, ax in enumerate(axes):
        samples = inn.sample(300, key=jax.random.PRNGKey(i))
        ax.scatter(X[:, 0], X[:, 1], alpha=0.3, s=10, c='gray', label='Training data')
        ax.scatter(samples[:, 0], samples[:, 1], alpha=0.6, s=10, c='red', label='Generated')
        ax.set_title(f'Samples (seed={i})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig('inn_spiral_samples.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'inn_spiral_samples.png'")

    return inn


if __name__ == '__main__':
    # Run all examples
    print("Running Invertible Neural Network Examples\n")

    # Example 1: Basic usage
    inn1, X1 = example_1_basic_usage()

    # Example 2: Anomaly detection
    inn2 = example_2_anomaly_detection()

    # Example 3: Forward/Inverse
    inn3 = example_3_forward_inverse()

    # Example 4: Sampling
    inn4 = example_4_sampling()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
