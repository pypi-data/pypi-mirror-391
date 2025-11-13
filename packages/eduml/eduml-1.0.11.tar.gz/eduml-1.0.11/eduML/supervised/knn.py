"""
knn.py
------
Enhanced K-Nearest Neighbors (KNN) Classifier for eduML.

Features:
    ✅ Supports different distance metrics (Euclidean, Manhattan)
    ✅ fit(): stores training data
    ✅ predict(): classifies by majority voting
    ✅ accuracy(): computes classification accuracy
    ✅ plot_decision_boundary(): visualizes 2D decision regions
    ✅ Educational: prints neighbor information for examples
"""

import numpy as np
from collections import Counter
import matplotlib.pyplot as plt


class KNN:
    def __init__(self, k=3, distance_metric="euclidean", verbose=False):
        """
        Parameters:
            k : int
                Number of neighbors
            distance_metric : str
                "euclidean" or "manhattan"
            verbose : bool
                Print educational info during prediction
        """
        self.k = k
        self.distance_metric = distance_metric
        self.verbose = verbose
        self.X_train = None
        self.y_train = None

    # -----------------------------
    # Fit
    # -----------------------------
    def fit(self, X, y):
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        return self

    # -----------------------------
    # Distance calculation
    # -----------------------------
    def _distance(self, x1, x2):
        if self.distance_metric == "euclidean":
            return np.sqrt(np.sum((x1 - x2) ** 2))
        elif self.distance_metric == "manhattan":
            return np.sum(np.abs(x1 - x2))
        else:
            raise ValueError(f"Unsupported distance metric: {self.distance_metric}")

    # -----------------------------
    # Predict
    # -----------------------------
    def predict(self, X):
        X = np.array(X)
        preds = []

        for i, x in enumerate(X):
            distances = [self._distance(x, x_train) for x_train in self.X_train]
            k_indices = np.argsort(distances)[:self.k]
            k_labels = self.y_train[k_indices]

            majority = Counter(k_labels).most_common(1)[0][0]
            preds.append(majority)

            if self.verbose:
                print(f"Sample {i}:")
                print(f"  Distances: {distances}")
                print(f"  Nearest {self.k} labels: {k_labels}")
                print(f"  Predicted class: {majority}\n")

        return np.array(preds)

    # -----------------------------
    # Accuracy
    # -----------------------------
    def accuracy(self, X, y):
        preds = self.predict(X)
        return np.mean(preds == y) * 100

    # -----------------------------
    # Decision boundary visualization
    # -----------------------------
    def plot_decision_boundary(self, X, y, resolution=0.1):
        X, y = np.array(X), np.array(y)
        if X.shape[1] != 2:
            print("Decision boundary plotting only works for 2D features")
            return

        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, resolution),
                             np.arange(y_min, y_max, resolution))
        grid = np.c_[xx.ravel(), yy.ravel()]
        Z = self.predict(grid)
        Z = Z.reshape(xx.shape)

        plt.figure(figsize=(7, 5))
        plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.Paired)
        plt.scatter(X[:, 0], X[:, 1], c=y, edgecolor="k", cmap=plt.cm.Paired)
        plt.title(f"KNN Decision Boundary (k={self.k})")
        plt.xlabel("Feature 1")
        plt.ylabel("Feature 2")
        plt.show()


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Simple 2D dataset
    import numpy as np

# Larger, more diverse 2D dataset
    X = np.array([
        [2, 3], [1, 2], [3, 6], [4, 5], [6, 8],
        [5, 2], [7, 3], [8, 4], [9, 6], [10, 7],
        [3, 1], [4, 2], [5, 5], [6, 6], [7, 7],
        [8, 8], [9, 9], [10, 10], [1, 6], [2, 5]
    ])

# Corresponding labels (0 or 1)
    y = np.array([
    0, 0, 1, 1, 1,
    0, 0, 1, 1, 1,
    0, 0, 1, 1, 1,
    1, 1, 1, 0, 0
])


    model = KNN(k=3, distance_metric="euclidean", verbose=True)
    model.fit(X, y)

    preds = model.predict([[3, 3], [7, 8]])
    print("Predictions:", preds)
    print("Accuracy:", model.accuracy(X, y))

    # Visualization
    model.plot_decision_boundary(X, y)
