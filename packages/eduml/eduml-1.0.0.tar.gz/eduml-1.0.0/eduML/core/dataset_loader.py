"""
dataset_loader.py
-----------------
Provides dataset loading and synthetic data generation utilities for eduML.

Includes:
    - load_iris_dataset(): Load Iris classification dataset.
    - load_wine_dataset(): Load Wine classification dataset.
    - load_digits_dataset(): Load Digits classification dataset.
    - generate_linear_data(): Create synthetic regression data for experiments.
"""

from sklearn.datasets import load_iris, load_wine, load_digits, make_regression
import numpy as np

# -----------------------------
# Classic Datasets
# -----------------------------

def load_iris_dataset():
    """
    Load the classic Iris dataset for classification tasks.

    Returns:
        X (ndarray): Feature matrix (shape: [150, 4])
        y (ndarray): Labels (shape: [150])
    """
    data = load_iris()
    X = data.data
    y = data.target
    return X, y


def load_wine_dataset():
    """
    Load the Wine dataset for classification tasks.

    Returns:
        X (ndarray): Feature matrix (shape: [178, 13])
        y (ndarray): Labels (shape: [178])
    """
    data = load_wine()
    X = data.data
    y = data.target
    return X, y


def load_digits_dataset():
    """
    Load the Digits dataset for classification tasks (8x8 images).

    Returns:
        X (ndarray): Feature matrix (shape: [1797, 64])
        y (ndarray): Labels (shape: [1797])
    """
    data = load_digits()
    X = data.data
    y = data.target
    return X, y


# -----------------------------
# Synthetic / Regression Data
# -----------------------------

def generate_linear_data(n_samples=100, n_features=1, noise=5.0, random_state=42):
    """
    Generate a synthetic linear regression dataset.

    Args:
        n_samples (int): Number of samples.
        n_features (int): Number of input features.
        noise (float): Random noise added to target values.
        random_state (int): Seed for reproducibility.

    Returns:
        X (ndarray): Feature matrix.
        y (ndarray): Target vector.
    """
    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        noise=noise,
        random_state=random_state
    )
    return X, y


# -----------------------------
# Example / Test
# -----------------------------
if __name__ == "__main__":
    X, y = load_iris_dataset()
    print("Iris dataset:", X.shape, y.shape)

    X, y = load_wine_dataset()
    print("Wine dataset:", X.shape, y.shape)

    X, y = load_digits_dataset()
    print("Digits dataset:", X.shape, y.shape)

    X, y = generate_linear_data()
    print("Synthetic linear data:", X.shape, y.shape)
