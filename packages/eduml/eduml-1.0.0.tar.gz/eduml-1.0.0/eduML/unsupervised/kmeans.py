"""
kmeans.py — eduML Implementation
--------------------------------
Unsupervised learning algorithm for grouping unlabeled data into K clusters.

✨ Improvements over base version:
    ✅ Added multiple centroid initialization strategies (random / k-means++)
    ✅ Added simple scaling option (for stability)
    ✅ Added optional history visualization (centroid movement)
    ✅ Added clearer explanations & progress info
    ✅ Added a built-in demo (no sklearn)

Educational Goal:
    Understand iterative optimization, convergence, and cluster compactness.
"""

import numpy as np
import matplotlib.pyplot as plt


class KMeans:
    def __init__(self, n_clusters=3, max_iter=100, tol=1e-4,
                 random_state=None, init="k-means++", learning_mode=False):
        """
        Parameters
        ----------
        n_clusters : int
            Number of clusters to form.
        max_iter : int
            Maximum number of iterations.
        tol : float
            Convergence threshold for centroid movement.
        random_state : int, optional
            Random seed for reproducibility.
        init : str, 'random' or 'k-means++'
            Centroid initialization method.
        learning_mode : bool
            If True, prints step-by-step progress.
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.init = init
        self.learning_mode = learning_mode

        self.centroids_ = None
        self.labels_ = None
        self.inertia_ = None
        self.history_ = []  # For learning visualization

    # --------------------------------------------------------
    # Fit
    # --------------------------------------------------------
    def fit(self, X):
        np.random.seed(self.random_state)

        # Scale data (auto-normalization)
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)

        # Step 1: Initialize centroids
        self.centroids_ = self._init_centroids(X)

        if self.learning_mode:
            print("=== K-Means Learning Mode ===")
            print(f"Initialization method: {self.init}")
            print(f"Initial centroids:\n{np.round(self.centroids_, 4)}\n")

        for i in range(self.max_iter):
            # Step 2: Assign samples to nearest centroid
            distances = self._compute_distances(X)
            labels = np.argmin(distances, axis=1)

            # Step 3: Update centroids
            new_centroids = np.array([
                X[labels == k].mean(axis=0) if np.any(labels == k)
                else self.centroids_[k]  # handle empty cluster
                for k in range(self.n_clusters)
            ])

            # Step 4: Convergence check
            shift = np.linalg.norm(new_centroids - self.centroids_)
            self.history_.append(new_centroids.copy())

            if self.learning_mode:
                print(f"Iteration {i+1}/{self.max_iter} | Shift: {shift:.6f}")

            if shift < self.tol:
                if self.learning_mode:
                    print(f"✅ Converged after {i+1} iterations.\n")
                break

            self.centroids_ = new_centroids

        # Final assignments & inertia
        self.labels_ = np.argmin(self._compute_distances(X), axis=1)
        self.inertia_ = np.sum(np.min(self._compute_distances(X), axis=1))

        if self.learning_mode:
            print("Final centroids:\n", np.round(self.centroids_, 4))
            print("Final inertia (within-cluster variance):", round(self.inertia_, 4))

        return self

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------
    def predict(self, X):
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
        distances = self._compute_distances(X)
        return np.argmin(distances, axis=1)

    # --------------------------------------------------------
    # Distance Computation
    # --------------------------------------------------------
    def _compute_distances(self, X):
        return np.sqrt(((X[:, np.newaxis, :] - self.centroids_) ** 2).sum(axis=2))

    # --------------------------------------------------------
    # Centroid Initialization
    # --------------------------------------------------------
    def _init_centroids(self, X):
        if self.init == "random":
            idx = np.random.choice(X.shape[0], self.n_clusters, replace=False)
            return X[idx, :]

        # k-means++ initialization
        centroids = [X[np.random.randint(X.shape[0])]]
        for _ in range(1, self.n_clusters):
            dist_sq = np.min(((X[:, np.newaxis, :] - centroids) ** 2).sum(axis=2), axis=1)
            probs = dist_sq / np.sum(dist_sq)
            next_idx = np.random.choice(X.shape[0], p=probs)
            centroids.append(X[next_idx])
        return np.array(centroids)

    # --------------------------------------------------------
    # Explain
    # --------------------------------------------------------
    def explain(self):
        print("\n📘 === K-Means Explanation ===")
        print(f"Number of clusters (K): {self.n_clusters}")
        print(f"Initialization: {self.init}")
        print(f"Max iterations: {self.max_iter}")
        print(f"Converged centroids:\n{np.round(self.centroids_, 4)}")
        print(f"Final inertia (compactness): {round(self.inertia_, 4)}")
        print("\nConcept:")
        print("K-Means groups data into K clusters by minimizing within-cluster variance.")
        print("It alternates between assigning points to nearest centroids and recomputing centroids until stable.")

    # --------------------------------------------------------
    # Visualization (2D only)
    # --------------------------------------------------------
    def visualize(self, X, show_history=False):
        if X.shape[1] != 2:
            print("Visualization available only for 2D data.")
            return

        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
        plt.figure(figsize=(6, 5))
        colors = plt.cm.tab10(np.arange(self.n_clusters))

        # Plot points by cluster
        for k in range(self.n_clusters):
            cluster_points = X[self.labels_ == k]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1],
                        s=40, color=colors[k], alpha=0.6, label=f"Cluster {k+1}")

        # Centroids
        plt.scatter(self.centroids_[:, 0], self.centroids_[:, 1],
                    s=200, color='black', marker='X', label='Centroids')

        # Optional centroid movement path
        if show_history and len(self.history_) > 1:
            for k in range(self.n_clusters):
                trail = np.array([h[k] for h in self.history_])
                plt.plot(trail[:, 0], trail[:, 1], '--', color=colors[k], alpha=0.4)

        plt.title("eduML K-Means Clustering")
        plt.xlabel("Feature 1")
        plt.ylabel("Feature 2")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()


# --------------------------------------------------------
# ✅ Built-in Demo (No sklearn)
# --------------------------------------------------------
def main():
    print("=== eduML K-Means Demo ===")

    np.random.seed(42)

    # --- Create simple 2D clusters manually ---
    cluster1 = np.random.randn(100, 2) + np.array([0, 0])
    cluster2 = np.random.randn(100, 2) + np.array([5, 5])
    cluster3 = np.random.randn(100, 2) + np.array([-5, 5])
    X = np.vstack((cluster1, cluster2, cluster3))

    # --- Run KMeans ---
    model = KMeans(n_clusters=3, learning_mode=True, random_state=1)
    model.fit(X)

    # --- Explain & visualize ---
    model.explain()
    model.visualize(X, show_history=True)

    print("Demo finished.")


if __name__ == "__main__":
    main()
