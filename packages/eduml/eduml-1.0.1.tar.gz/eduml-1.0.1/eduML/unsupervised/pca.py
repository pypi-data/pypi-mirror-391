import numpy as np
import matplotlib.pyplot as plt


class PCA:
    """
    Principal Component Analysis (PCA) implementation for eduML.
    Designed to be simple, educational, and mathematically transparent.
    """

    def __init__(self, n_components=None, learning_mode=False):
        self.n_components = n_components
        self.learning_mode = learning_mode

        self.mean_ = None
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None

    # ----------------------------------------------------
    # FIT (now accepts y=None for sklearn-compatible API)
    # ----------------------------------------------------
    def fit(self, X, y=None):
        X = np.asarray(X)

        if X.ndim != 2:
            raise ValueError("PCA.fit expects a 2D array (n_samples, n_features).")

        # Step 1: Center the data
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_

        # Step 2: Compute covariance matrix using SVD (more stable)
        # X = U * S * Vt
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        # Eigenvalues = variance along each direction
        eigvals = (S ** 2) / (X.shape[0] - 1)
        eigvecs = Vt.T  # columns = principal directions

        # Step 3: Select components
        if self.n_components is None:
            self.n_components = X.shape[1]

        self.components_ = eigvecs[:, :self.n_components]
        self.explained_variance_ = eigvals[:self.n_components]
        total_var = np.sum(eigvals)
        self.explained_variance_ratio_ = self.explained_variance_ / total_var

        # Learning / Educational Output
        if self.learning_mode:
            print("\n=== PCA Learning Mode (eduML) ===")
            print("1) Mean vector:")
            print(np.round(self.mean_, 4))
            print("\n2) Top eigenvalues (variance per PC):")
            print(np.round(self.explained_variance_, 4))
            print("\n3) Explained variance ratio (%):")
            print(np.round(100 * self.explained_variance_ratio_, 2))
            print("\n4) Principal Components (directions of max variance):")
            print(np.round(self.components_, 4))
            print("\nInterpretation:")
            print("- Each PC is a direction that captures maximum variance.")
            print("- PC1 captures the most variability, PC2 the next most, and so on.")
            print("- Components are orthogonal (no overlap in information).")

        return self

    # ----------------------------------------------------
    # TRANSFORM
    # ----------------------------------------------------
    def transform(self, X):
        if self.components_ is None:
            raise ValueError("PCA not fitted yet. Call fit(X) first.")
        X_centered = X - self.mean_
        return np.dot(X_centered, self.components_)

    # ----------------------------------------------------
    # INVERSE TRANSFORM
    # ----------------------------------------------------
    def inverse_transform(self, X_transformed):
        if self.components_ is None:
            raise ValueError("PCA not fitted yet.")
        return np.dot(X_transformed, self.components_.T) + self.mean_

    # ----------------------------------------------------
    # EXPLAIN
    # ----------------------------------------------------
    def explain(self):
        print("\n=== PCA Explanation ===")
        print(f"Number of selected components: {self.n_components}")
        print("Explained variance ratio per component (%):")
        print(np.round(100 * self.explained_variance_ratio_, 2))

        print("\nEducational Interpretation:")
        print("- PCA finds new axes that maximize variance.")
        print("- PC1 captures the strongest trend in data.")
        print("- PC2 captures the next strongest trend, independent of PC1.")
        print("- Useful for compression, noise reduction, visualization, and feature learning.")

    # ----------------------------------------------------
    # VISUALIZE
    # ----------------------------------------------------
    def visualize(self, X, y=None):
        X_pca = self.transform(X)

        plt.figure(figsize=(7, 5))

        if X_pca.shape[1] >= 2:
            # 2D scatter
            if y is not None:
                classes = np.unique(y)
                for c in classes:
                    plt.scatter(X_pca[y == c, 0], X_pca[y == c, 1], alpha=0.7, label=f"Class {c}")
            else:
                plt.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.7)

            plt.xlabel("Principal Component 1")
            plt.ylabel("Principal Component 2")
            plt.title("2D PCA Projection")
            plt.legend()
        else:
            # 1D Projection
            plt.scatter(range(len(X_pca)), X_pca[:, 0])
            plt.xlabel("Samples")
            plt.ylabel("PC1 Value")
            plt.title("1D PCA Projection")

        plt.grid(alpha=0.3)
        plt.show()
