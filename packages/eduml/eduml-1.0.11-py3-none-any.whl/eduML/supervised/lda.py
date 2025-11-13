import numpy as np
import matplotlib.pyplot as plt


class LDA:
    """
    Linear Discriminant Analysis (LDA)
    ----------------------------------
    Supervised dimensionality reduction and classification.

    Features:
    - Handles binary & multi-class LDA
    - Automatic fallback to SVD if Sw is singular
    - Works for both classification + visualization
    - scikit-learn–style API
    """

    def __init__(self, n_components=None, learning_mode=False):
        self.n_components = n_components
        self.learning_mode = learning_mode

        self.classes_ = None
        self.W_ = None
        self.eigvals_ = None
        self.means_ = {}
        self.centroids_ = {}

    # ------------------------------------------------------
    # Fit
    # ------------------------------------------------------
    def fit(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y)

        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")
        if y.ndim != 1:
            raise ValueError("y must be a 1D array.")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples.")

        self.classes_ = np.unique(y)
        n_features = X.shape[1]

        # Overall mean
        mean_overall = np.mean(X, axis=0)

        # Scatter matrices
        Sw = np.zeros((n_features, n_features))
        Sb = np.zeros((n_features, n_features))

        for c in self.classes_:
            X_c = X[y == c]
            mean_c = np.mean(X_c, axis=0)
            self.means_[c] = mean_c

            # Within-class scatter
            X_centered = X_c - mean_c
            Sw += X_centered.T @ X_centered

            # Between-class scatter
            n_c = len(X_c)
            mean_diff = (mean_c - mean_overall).reshape(-1, 1)
            Sb += n_c * (mean_diff @ mean_diff.T)

        # Eigen decomposition of Sw⁻¹ Sb
        try:
            eigvals, eigvecs = np.linalg.eig(np.linalg.pinv(Sw) @ Sb)
        except np.linalg.LinAlgError:
            # Backup: SVD for numerical stability
            U, S, Vt = np.linalg.svd(Sw)
            Sw_inv = (Vt.T * (1 / (S + 1e-12))) @ U.T
            eigvals, eigvecs = np.linalg.eig(Sw_inv @ Sb)

        # Sort by importance
        sorted_idx = np.argsort(np.real(eigvals))[::-1]
        eigvals = np.real(eigvals[sorted_idx])
        eigvecs = np.real(eigvecs[:, sorted_idx])

        # Determine number of components
        if self.n_components is None:
            self.n_components = min(len(self.classes_) - 1, X.shape[1])

        self.eigvals_ = eigvals
        self.W_ = eigvecs[:, :self.n_components]

        # Precompute class centroids for prediction
        X_proj = self.transform(X)
        for c in self.classes_:
            self.centroids_[c] = np.mean(X_proj[y == c], axis=0)

        if self.learning_mode:
            print("\n=== LDA Learning Mode ===")
            print("Classes:", self.classes_)
            print("Eigenvalues:", np.round(self.eigvals_[:self.n_components], 4))
            print("Projection matrix W shape:", self.W_.shape)

        return self

    # ------------------------------------------------------
    # Transform
    # ------------------------------------------------------
    def transform(self, X):
        if self.W_ is None:
            raise ValueError("Model must be fitted before calling transform().")
        return np.dot(X, self.W_)

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)

    # ------------------------------------------------------
    # Predict
    # ------------------------------------------------------
    def predict(self, X):
        if self.W_ is None or not self.centroids_:
            raise ValueError("Model must be fitted before prediction.")

        X_proj = self.transform(X)
        preds = []

        for x in X_proj:
            distances = {c: np.linalg.norm(x - centroid) 
                         for c, centroid in self.centroids_.items()}
            preds.append(min(distances, key=distances.get))

        return np.array(preds)

    # ------------------------------------------------------
    # Explain
    # ------------------------------------------------------
    def explain(self):
        if self.W_ is None:
            raise ValueError("Fit model before calling explain().")

        print("\n=== LDA Model Explanation ===")
        print(f"Classes detected: {self.classes_}")
        print(f"Number of components selected: {self.n_components}")
        print("\nTop Eigenvalues (discrimination power):")
        print(np.round(self.eigvals_[:self.n_components], 5))

        print("\nInterpretation:")
        print("- Each LDA component is a direction maximizing class separability.")
        print("- Higher eigenvalues ⇒ better discrimination between classes.")
        print("- W_ contains the projection directions.")

    # ------------------------------------------------------
    # Visualize (2D or 1D)
    # ------------------------------------------------------
    def visualize(self, X, y):
        if self.W_ is None:
            raise ValueError("Model must be fitted before visualization.")

        X_lda = self.transform(X)

        plt.figure(figsize=(7, 5))

        if X_lda.shape[1] == 1:
            # Use a single axis projection
            for label in self.classes_:
                plt.scatter(X_lda[y == label, 0],
                            np.zeros_like(X_lda[y == label, 0]),
                            label=str(label))
            plt.xlabel("LD1")
            plt.yticks([])
            plt.title("LDA Projection (1D)")

        elif X_lda.shape[1] >= 2:
            for label in self.classes_:
                plt.scatter(X_lda[y == label, 0],
                            X_lda[y == label, 1],
                            label=str(label))
            plt.xlabel("LD1")
            plt.ylabel("LD2")
            plt.title("LDA Projection (2D)")

        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()
# ------------------------------------------------------
# Standalone demo runner
# ------------------------------------------------------
def main():
    """
    Quick test for LDA module.
    Run:
        python -m eduML.supervised.lda
    """

    import numpy as np
    from sklearn.datasets import load_iris

    print("=== Running LDA Demo ===\n")

    data = load_iris()
    X, y = data.data, data.target

    lda = LDA(n_components=2, learning_mode=True)
    lda.fit(X, y)

    print("\nExplanation:")
    lda.explain()

    try:
        lda.visualize(X, y)
    except Exception as e:
        print("Visualization error:", e)

    preds = lda.predict(X)
    acc = np.mean(preds == y) * 100
    print(f"\nTraining accuracy: {acc:.2f}%")
    print("Demo complete.")


if __name__ == "__main__":
    main()
