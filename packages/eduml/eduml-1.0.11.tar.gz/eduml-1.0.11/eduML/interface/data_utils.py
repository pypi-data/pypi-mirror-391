# data_utils.py
import numpy as np
from eduML.core.dataset_loader import (
    load_iris_dataset,
    load_wine_dataset,
    load_digits_dataset,
    generate_linear_data
)
from eduML.core.preprocessing import train_test_split, standardize

def prepare_data(dataset_name):
    """
    Unified helper: loads dataset, splits into train/test, and standardizes features.
    Returns:
        X_train, X_test, y_train, y_test
    """
    # Load dataset
    name = dataset_name.strip().lower()
    if name in ("iris", "iris_dataset"):
        X, y = load_iris_dataset()
    elif name in ("wine", "wine_dataset"):
        X, y = load_wine_dataset()
    elif name in ("digits", "digits_dataset"):
        X, y = load_digits_dataset()
    elif name in ("linear", "synthetic", "regression"):
        X, y = generate_linear_data()
    else:
        raise ValueError(f"Unknown dataset '{dataset_name}'")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # Standardize numeric features
    X_train_std, mean, std = standardize(X_train)
    X_test_std = (X_test - mean) / std

    return X_train_std, X_test_std, y_train, y_test
