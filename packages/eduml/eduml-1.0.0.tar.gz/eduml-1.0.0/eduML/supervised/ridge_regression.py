"""
ridge_regression.py
--------------------
Implements Ridge Regression (L2 Regularization).

Key Features:
    - fit(): Train with Normal Equation
    - predict(): Predict output
    - alpha: Regularization strength
"""

import numpy as np


class RidgeRegression:
    def __init__(self, alpha=1.0, fit_intercept=True):
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.theta = None

    def _add_intercept(self, X):
        if not self.fit_intercept:
            return X
        intercept = np.ones((X.shape[0], 1))
        return np.hstack((intercept, X))

    def fit(self, X, y):
        X = self._add_intercept(np.array(X))
        y = np.array(y)

        n_features = X.shape[1]
        I = np.eye(n_features)
        if self.fit_intercept:
            I[0, 0] = 0  # Don't regularize bias term

        # Ridge Normal Equation: θ = (XᵀX + αI)^(-1) Xᵀy
        self.theta = np.linalg.pinv(X.T.dot(X) + self.alpha * I).dot(X.T).dot(y)
        return self

    def predict(self, X):
        X = self._add_intercept(np.array(X))
        return X.dot(self.theta)

    def score(self, X, y):
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot)


# Example usage
if __name__ == "__main__":
    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([2.2, 4.1, 6.0, 8.1, 10.2])

    model = RidgeRegression(alpha=0.5)
    model.fit(X, y)
    print("Prediction for x=6:", model.predict([[6]]))
    print("R² Score:", model.score(X, y))
