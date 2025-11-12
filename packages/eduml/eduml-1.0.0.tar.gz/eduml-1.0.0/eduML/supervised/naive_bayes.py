"""
naive_bayes.py
--------------
Enhanced Gaussian Naive Bayes Classifier for eduML.

Educational Features:
    - Logs class-wise mean & variance
    - Shows posterior probabilities
    - Visualizes feature distributions
"""

import numpy as np
import matplotlib.pyplot as plt


class GaussianNB:
    def __init__(self):
        self.classes = None
        self.means = {}
        self.vars = {}
        self.priors = {}
        self.log_likelihoods = []

    # -------------------------
    # Fit
    # -------------------------
    def fit(self, X, y):
        X, y = np.array(X), np.array(y)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self.classes = np.unique(y)
        for c in self.classes:
            X_c = X[y == c]
            self.means[c] = np.mean(X_c, axis=0)
            self.vars[c] = np.var(X_c, axis=0) + 1e-6  # avoid zero variance
            self.priors[c] = len(X_c) / len(X)
        return self

    # -------------------------
    # Gaussian PDF
    # -------------------------
    def _pdf(self, x, mean, var):
        return (1.0 / np.sqrt(2 * np.pi * var)) * np.exp(- ((x - mean) ** 2) / (2 * var))

    # -------------------------
    # Predict
    # -------------------------
    def predict(self, X, return_proba=False):
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        predictions = []
        all_posteriors = []

        for x in X:
            posteriors = []
            for c in self.classes:
                prior = np.log(self.priors[c])
                cond_likelihood = np.sum(np.log(self._pdf(x, self.means[c], self.vars[c])))
                posterior = prior + cond_likelihood
                posteriors.append(posterior)
            all_posteriors.append(posteriors)
            predictions.append(self.classes[np.argmax(posteriors)])

        self.log_likelihoods = all_posteriors
        return np.array(predictions) if not return_proba else np.array(all_posteriors)

    # -------------------------
    # Accuracy
    # -------------------------
    def accuracy(self, X, y):
        preds = self.predict(X)
        return np.mean(preds == y) * 100

    # -------------------------
    # Explain
    # -------------------------
    def explain(self):
        print("Gaussian Naive Bayes Explanation:")
        for c in self.classes:
            print(f"Class '{c}':")
            print(f"  Prior: {self.priors[c]:.3f}")
            print(f"  Mean: {self.means[c]}")
            print(f"  Variance: {self.vars[c]}")
        print("\nPosterior probabilities (log-likelihoods) are tracked in 'log_likelihoods'.")

    # -------------------------
    # Visualization
    # -------------------------
    def visualize_features(self, feature_names=None):
        """
        Plots class-wise Gaussian distributions for each feature.
        """
        n_features = len(next(iter(self.means.values())))
        feature_names = feature_names or [f"Feature {i}" for i in range(n_features)]

        x_min = {i: float("inf") for i in range(n_features)}
        x_max = {i: float("-inf") for i in range(n_features)}

        # Determine ranges
        for i in range(n_features):
            for c in self.classes:
                mean, var = self.means[c][i], self.vars[c][i]
                x_min[i] = min(x_min[i], mean - 3 * np.sqrt(var))
                x_max[i] = max(x_max[i], mean + 3 * np.sqrt(var))

        for i in range(n_features):
            xs = np.linspace(x_min[i], x_max[i], 200)
            plt.figure(figsize=(6, 4))
            for c in self.classes:
                mean, var = self.means[c][i], self.vars[c][i]
                pdf = self._pdf(xs, mean, var)
                plt.plot(xs, pdf, label=f"Class {c}")
            plt.title(f"Feature '{feature_names[i]}' Gaussian Distribution")
            plt.xlabel(feature_names[i])
            plt.ylabel("Probability Density")
            plt.legend()
            plt.show()


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    # Synthetic dataset (height, weight)
    X = np.array([
        [1.7, 56], [1.8, 65], [1.6, 54], [1.9, 72], [1.5, 50],
        [1.55, 48], [1.85, 70], [1.65, 60], [1.78, 68], [1.62, 52]
    ])
    y = np.array(["M", "M", "F", "M", "F", "F", "M", "F", "M", "F"])

    model = GaussianNB()
    model.fit(X, y)

    preds = model.predict([[1.7, 60], [1.6, 52]])
    print("Predictions:", preds)
    print("Accuracy:", model.accuracy(X, y))

    model.explain()
    model.visualize_features(feature_names=["Height (m)", "Weight (kg)"])
