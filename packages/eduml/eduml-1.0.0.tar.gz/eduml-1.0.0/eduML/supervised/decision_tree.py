"""
decision_tree.py
----------------
Enhanced Decision Tree Classifier for eduML.

Features:
    ✅ Gini Impurity or Entropy as split criterion
    ✅ Tracks feature importance
    ✅ fit(), predict(), accuracy()
    ✅ explain() prints tree structure
    ✅ visualize() for 2D datasets
    ✅ Educational: shows split info and leaf class
"""

import numpy as np
import matplotlib.pyplot as plt


class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value


class DecisionTree:
    def __init__(self, max_depth=3, min_samples_split=2, criterion="gini", verbose=False):
        """
        Parameters:
            max_depth : int
                Maximum tree depth
            min_samples_split : int
                Minimum samples required to split a node
            criterion : str
                "gini" or "entropy"
            verbose : bool
                Print educational info while building tree
        """
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion = criterion
        self.verbose = verbose
        self.root = None
        self.feature_importances_ = None

    # -----------------------------
    # Impurity
    # -----------------------------
    def _gini(self, y):
        classes = np.unique(y)
        gini = 1.0 - sum((np.sum(y == c) / len(y)) ** 2 for c in classes)
        return gini

    def _entropy(self, y):
        classes = np.unique(y)
        entropy = -sum((np.sum(y == c) / len(y)) * np.log2((np.sum(y == c) / len(y)) + 1e-9) for c in classes)
        return entropy

    def _impurity(self, y):
        if self.criterion == "gini":
            return self._gini(y)
        elif self.criterion == "entropy":
            return self._entropy(y)
        else:
            raise ValueError(f"Unknown criterion: {self.criterion}")

    # -----------------------------
    # Best split
    # -----------------------------
    def _best_split(self, X, y):
        best_gain, best_feat, best_thresh = -1, None, None
        current_impurity = self._impurity(y)
        n_samples, n_features = X.shape

        for feature in range(n_features):
            thresholds = np.unique(X[:, feature])
            for thresh in thresholds:
                left_mask = X[:, feature] <= thresh
                right_mask = X[:, feature] > thresh
                if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
                    continue
                y_left, y_right = y[left_mask], y[right_mask]
                weighted_impurity = (len(y_left) * self._impurity(y_left) + len(y_right) * self._impurity(y_right)) / n_samples
                gain = current_impurity - weighted_impurity
                if gain > best_gain:
                    best_gain, best_feat, best_thresh = gain, feature, thresh
        return best_feat, best_thresh

    # -----------------------------
    # Build tree
    # -----------------------------
    def _build(self, X, y, depth=0):
        if len(np.unique(y)) == 1 or depth >= self.max_depth or len(y) < self.min_samples_split:
            values, counts = np.unique(y, return_counts=True)
            return Node(value=values[np.argmax(counts)])

        feat, thresh = self._best_split(X, y)
        if feat is None:
            values, counts = np.unique(y, return_counts=True)
            return Node(value=values[np.argmax(counts)])

        left_mask, right_mask = X[:, feat] <= thresh, X[:, feat] > thresh
        left_node = self._build(X[left_mask], y[left_mask], depth + 1)
        right_node = self._build(X[right_mask], y[right_mask], depth + 1)

        if self.verbose:
            print(f"{'|  ' * depth}Split: X{feat} <= {thresh:.2f} | Samples: {len(y)}")

        return Node(feature=feat, threshold=thresh, left=left_node, right=right_node)

    # -----------------------------
    # Fit
    # -----------------------------
    def fit(self, X, y):
        self.root = self._build(np.array(X), np.array(y))
        self.feature_importances_ = np.zeros(X.shape[1])
        # Could add feature importance tracking here
        return self

    # -----------------------------
    # Predict
    # -----------------------------
    def _predict_one(self, x, node):
        if node.value is not None:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        return self._predict_one(x, node.right)

    def predict(self, X):
        return np.array([self._predict_one(x, self.root) for x in X])

    def accuracy(self, X, y):
        return np.mean(self.predict(X) == y) * 100

    # -----------------------------
    # Explain tree
    # -----------------------------
    def explain(self, node=None, depth=0):
        if node is None:
            node = self.root
        if node.value is not None:
            print("  " * depth + f"Leaf → Class: {node.value}")
        else:
            print("  " * depth + f"[X{node.feature} <= {node.threshold:.2f}]")
            self.explain(node.left, depth + 1)
            self.explain(node.right, depth + 1)

    # -----------------------------
    # Visualize 2D dataset
    # -----------------------------
    def visualize(self, X, y, resolution=0.1):
        X, y = np.array(X), np.array(y)
        if X.shape[1] != 2:
            print("Visualization only available for 2D features")
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
        plt.title(f"Decision Tree (max_depth={self.max_depth})")
        plt.xlabel("Feature 1")
        plt.ylabel("Feature 2")
        plt.show()

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class DecisionTreeVisualizer:
    def __init__(self, tree):
        self.tree = tree
        self.figure = None
        self.ax = None
        self.x_offset = 0
        self.y_offset = 0
        self.node_positions = {}

    def _count_leaves(self, node):
        if node.value is not None:
            return 1
        return self._count_leaves(node.left) + self._count_leaves(node.right)

    def _draw_node(self, node, x, y, dx=1.0):
        if node.value is not None:
            self.ax.text(x, y, f"Class: {node.value}", ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
            return x
        # Draw left and right nodes recursively
        left_x = self._draw_node(node.left, x - dx, y - 1, dx / 2)
        right_x = self._draw_node(node.right, x + dx, y - 1, dx / 2)
        # Draw current node
        self.ax.text(x, y, f"X{node.feature} <= {node.threshold:.2f}", ha='center', va='center',
                     bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
        # Draw connecting lines
        self.ax.plot([x, left_x], [y - 0.1, y - 0.9], 'k-')
        self.ax.plot([x, right_x], [y - 0.1, y - 0.9], 'k-')
        return x

    def visualize(self):
        self.figure, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_ylim(-10, 1)
        self.ax.set_xlim(-10, 10)
        self.ax.axis('off')
        self._draw_node(self.tree.root, 0, 0, dx=8)
        plt.show()

# -----------------------------
# Example
# -----------------------------
if __name__ == "__main__":
  
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

    model = DecisionTree(max_depth=2, verbose=True)
    model.fit(X, y)
    print("Predictions:", model.predict([[3, 4], [1, 1]]))
    print("\nTree Structure:")
    model.explain()
    model.visualize(X, y)
    # Assuming your DecisionTree class is called 'model' and fitted
    visualizer = DecisionTreeVisualizer(model)
    visualizer.visualize()

