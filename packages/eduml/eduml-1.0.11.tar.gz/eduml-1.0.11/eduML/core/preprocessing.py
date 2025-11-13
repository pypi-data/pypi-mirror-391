"""
preprocessing.py
----------------
Provides basic preprocessing utilities for eduML.

Includes:
    - train_test_split(): Split data into training and testing sets.
    - standardize(): Perform z-score normalization on features.
"""

import numpy as np


def train_test_split(X, y, test_size=0.2, random_state=42):
    """
    Split dataset into training and testing sets.

    Args:
        X (ndarray): Feature matrix.
        y (ndarray): Target vector.
        test_size (float): Fraction of data to use for testing.
        random_state (int): Seed for reproducibility.

    Returns:
        X_train, X_test, y_train, y_test (ndarray)
    """
    np.random.seed(random_state)
    n_samples = X.shape[0]
    indices = np.arange(n_samples)
    np.random.shuffle(indices)

    split_idx = int(n_samples * (1 - test_size))
    train_idx, test_idx = indices[:split_idx], indices[split_idx:]

    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def standardize(X):
    """
    Standardize features by removing the mean and scaling to unit variance.

    Args:
        X (ndarray): Feature matrix.

    Returns:
        X_std (ndarray): Standardized feature matrix.
        mean (ndarray): Feature means.
        std (ndarray): Feature standard deviations.
    """
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std[std == 0] = 1e-8  # Avoid division by zero
    X_std = (X - mean) / std
    return X_std, mean, std

"""
preprocessing.py
----------------
Provides basic preprocessing utilities for eduML.

Includes:
    - train_test_split(): Split data into training and testing sets.
    - standardize(): Perform z-score normalization on features.
    - Preprocessor: Unified preprocessing model with fit/transform API.
"""

import numpy as np


def train_test_split(X, y, test_size=0.2, random_state=42):
    """
    Split dataset into training and testing sets.

    Args:
        X (ndarray): Feature matrix.
        y (ndarray): Target vector.
        test_size (float): Fraction of data to use for testing.
        random_state (int): Seed for reproducibility.

    Returns:
        X_train, X_test, y_train, y_test (ndarray)
    """
    np.random.seed(random_state)
    n_samples = X.shape[0]
    indices = np.arange(n_samples)
    np.random.shuffle(indices)

    split_idx = int(n_samples * (1 - test_size))
    train_idx, test_idx = indices[:split_idx], indices[split_idx:]

    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def standardize(X):
    """
    Standardize features by removing the mean and scaling to unit variance.

    Args:
        X (ndarray): Feature matrix.

    Returns:
        X_std (ndarray): Standardized feature matrix.
        mean (ndarray): Feature means.
        std (ndarray): Feature standard deviations.
    """
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std[std == 0] = 1e-8  # Avoid division by zero
    X_std = (X - mean) / std
    return X_std, mean, std


# ============================================================
# ✅ Preprocessing Model (fit/transform API)
# ============================================================

class preprocess_data:
    """
    A simple preprocessing model similar to sklearn.preprocessing.StandardScaler.
    Provides:
        - fit(): Learn statistics from training data
        - transform(): Apply preprocessing
        - fit_transform(): Combined step
        - inverse_transform(): Revert to original scale
    """

    def __init__(self):
        self.mean_ = None
        self.std_ = None
        self.is_fitted = False

    def fit(self, X):
        """Compute mean & std of the dataset."""
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0)
        self.std_[self.std_ == 0] = 1e-8  # Avoid division by zero
        self.is_fitted = True
        return self

    def transform(self, X):
        """Apply standardization to features."""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before calling transform().")
        return (X - self.mean_) / self.std_

    def fit_transform(self, X):
        """Fit preprocessing statistics and transform the data."""
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X_scaled):
        """Revert standardized data back to original scale."""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before calling inverse_transform().")
        return (X_scaled * self.std_) + self.mean_


# ============================================================
# Example usage (for testing / demonstration)
# ============================================================

if __name__ == "__main__":
    from dataset_loader import generate_linear_data

    X, y = generate_linear_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    print("Train/Test split:", X_train.shape, X_test.shape)

    X_std, mean, std = standardize(X_train)
    print("Standardized features (function):", X_std[:5])

    prep = preprocess_data()
    X_scaled = prep.fit_transform(X_train)
    print("Standardized features (model):", X_scaled[:5])


    X, y = generate_linear_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    print("Train/Test split:", X_train.shape, X_test.shape)

    X_std, mean, std = standardize(X_train)
    print("Standardized features:", X_std[:5])
