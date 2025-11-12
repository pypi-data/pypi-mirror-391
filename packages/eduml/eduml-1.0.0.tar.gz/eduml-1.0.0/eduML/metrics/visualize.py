# eduML/metrics/visualize.py

import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, Optional
from matplotlib.colors import ListedColormap


def plot_decision_boundary(
    model: Callable,
    X: np.ndarray,
    y: np.ndarray,
    title: str = "Decision Boundary",
    resolution: int = 300,
    alpha: float = 0.3,
    cmap: Optional[ListedColormap] = None
):
    """
    Plots the decision boundary for 2D datasets.

    Parameters:
        model: classifier with .predict() method
        X: feature matrix of shape (n_samples, 2)
        y: target labels
        title: plot title
        resolution: number of points per axis for meshgrid
        alpha: transparency of the decision surface
        cmap: optional matplotlib colormap
    """
    assert X.shape[1] == 2, "Decision boundary plot requires 2D features."

    # Set default colormap if not provided
    if cmap is None:
        cmap = ListedColormap(["#FFAAAA", "#AAAAFF", "#AAFFAA", "#FFD700", "#FF69B4"])

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, resolution),
        np.linspace(y_min, y_max, resolution)
    )

    grid = np.c_[xx.ravel(), yy.ravel()]

    # Predict classes
    try:
        Z = model.predict(grid)
    except Exception:
        # If model outputs probabilities, take argmax
        Z = np.argmax(model.predict(grid), axis=1)
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(8, 6))
    plt.contourf(xx, yy, Z, alpha=alpha, cmap=cmap)
    
    # Plot data points
    for idx, cls in enumerate(np.unique(y)):
        plt.scatter(
            X[y == cls, 0],
            X[y == cls, 1],
            edgecolor="k",
            label=f"Class {cls}",
            s=60
        )

    plt.title(title)
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_loss_curve(
    loss_history: list,
    title: str = "Loss Curve",
    linewidth: float = 2,
    marker: Optional[str] = None,
    smooth: bool = False
):
    """
    Plots training loss vs epochs.

    Parameters:
        loss_history: list of loss values
        title: plot title
        linewidth: line thickness
        marker: optional marker style for points
        smooth: if True, applies simple moving average smoothing
    """
    loss_array = np.array(loss_history)
    if smooth and len(loss_array) > 5:
        window = max(3, len(loss_array) // 50)
        smoothed = np.convolve(loss_array, np.ones(window)/window, mode='valid')
        plt.plot(smoothed, linewidth=linewidth, label="Smoothed Loss")
    
    plt.plot(loss_array, linewidth=linewidth, marker=marker, label="Raw Loss")
    plt.title(title)
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.legend()
    plt.show()
