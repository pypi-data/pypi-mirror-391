"""
visualize.py
-------------
Visualization utilities for eduML to help learners connect algorithm behavior
with visual insights.

Includes:
    - plot_decision_boundary()
    - plot_learning_curve()
    - plot_regression_results()
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_decision_boundary(model, X, y, title="Decision Boundary"):
    """
    Plot the decision boundary for 2D classification problems.

    Args:
        model: Trained model with a predict() method.
        X (ndarray): 2D feature matrix.
        y (ndarray): Labels.
        title (str): Plot title.
    """
    if X.shape[1] != 2:
        print("plot_decision_boundary only supports 2D features.")
        return

    # Define grid
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))

    # Predict on grid
    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict(grid)
    Z = Z.reshape(xx.shape)

    # Plot contour
    plt.contourf(xx, yy, Z, alpha=0.4, cmap='coolwarm')
    plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='coolwarm', edgecolor='k')
    plt.title(title)
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.show()


def plot_learning_curve(losses, title="Learning Curve"):
    """
    Plot loss over epochs for any model trained via gradient descent.

    Args:
        losses (list or ndarray): List of loss values.
        title (str): Plot title.
    """
    plt.figure()
    plt.plot(losses, color='blue', linewidth=2)
    plt.title(title)
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.show()


def plot_regression_results(y_true, y_pred, title="Regression Results"):
    """
    Plot predicted vs actual values for regression.

    Args:
        y_true (ndarray): True target values.
        y_pred (ndarray): Predicted target values.
        title (str): Plot title.
    """
    plt.figure()
    plt.scatter(y_true, y_pred, alpha=0.7)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()],
             color='red', linestyle='--')
    plt.title(title)
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.grid(True)
    plt.show()


# Example usage
if __name__ == "__main__":
    import numpy as np

    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8, 5.1])
    plot_regression_results(y_true, y_pred)
    plot_learning_curve([0.9, 0.6, 0.4, 0.3, 0.25])
