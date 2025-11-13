"""
metrics.py
-----------
Evaluation metrics for regression and classification algorithms in eduML.

Includes:
    - mean_squared_error (MSE)
    - root_mean_squared_error (RMSE)
    - accuracy_score
    - f1_score
    - confusion_matrix
"""

import numpy as np


# ---------------------------
# Regression Metrics
# ---------------------------

def mean_squared_error(y_true, y_pred):
    """
    Compute Mean Squared Error (MSE).

    Args:
        y_true (ndarray): Actual target values.
        y_pred (ndarray): Predicted target values.

    Returns:
        float: Mean squared error.
    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean((y_true - y_pred) ** 2)


def root_mean_squared_error(y_true, y_pred):
    """
    Compute Root Mean Squared Error (RMSE).

    Args:
        y_true (ndarray): Actual target values.
        y_pred (ndarray): Predicted target values.

    Returns:
        float: Root mean squared error.
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


# ---------------------------
# Classification Metrics
# ---------------------------

def accuracy_score(y_true, y_pred):
    """
    Compute classification accuracy.

    Args:
        y_true (ndarray): Actual class labels.
        y_pred (ndarray): Predicted class labels.

    Returns:
        float: Accuracy in percentage.
    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(y_true == y_pred) * 100


def confusion_matrix(y_true, y_pred):
    """
    Compute confusion matrix for multi-class classification.

    Args:
        y_true (ndarray): True class labels.
        y_pred (ndarray): Predicted class labels.

    Returns:
        ndarray: Confusion matrix of shape (n_classes, n_classes)
    """
    labels = np.unique(np.concatenate((y_true, y_pred)))
    n_classes = len(labels)
    matrix = np.zeros((n_classes, n_classes), dtype=int)

    for i, label_true in enumerate(labels):
        for j, label_pred in enumerate(labels):
            matrix[i, j] = np.sum((y_true == label_true) & (y_pred == label_pred))
    return matrix


def f1_score(y_true, y_pred):
    """
    Compute F1-score for binary classification.

    Args:
        y_true (ndarray): True labels.
        y_pred (ndarray): Predicted labels.

    Returns:
        float: F1-score.
    """
    cm = confusion_matrix(y_true, y_pred)
    tp = np.diag(cm)
    fp = np.sum(cm, axis=0) - tp
    fn = np.sum(cm, axis=1) - tp
    precision = np.divide(tp, tp + fp + 1e-8)
    recall = np.divide(tp, tp + fn + 1e-8)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-8)
    return np.mean(f1)


# Example usage
if __name__ == "__main__":
    y_true = np.array([1, 0, 1, 1, 0])
    y_pred = np.array([1, 0, 1, 0, 0])

    print("MSE:", mean_squared_error(y_true, y_pred))
    print("RMSE:", root_mean_squared_error(y_true, y_pred))
    print("Accuracy:", accuracy_score(y_true, y_pred), "%")
    print("Confusion Matrix:\n", confusion_matrix(y_true, y_pred))
    print("F1 Score:", f1_score(y_true, y_pred))
