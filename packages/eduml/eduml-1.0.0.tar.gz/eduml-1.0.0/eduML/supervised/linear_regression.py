"""
linear_regression.py
--------------------
Enhanced Linear Regression for eduML.

Features:
    ✅ Input validation and reshaping
    ✅ Gradient Descent + Normal Equation
    ✅ Early stopping
    ✅ Tracks training loss
    ✅ Visualization of loss and predictions
    ✅ Bridges theory and code for learning
"""

import numpy as np
import matplotlib.pyplot as plt

class LinearRegression:
    def __init__(self, lr=0.01, epochs=1000, fit_intercept=True,
                 tol=1e-6, early_stopping=False):
        """
        Parameters
        ----------
        lr : float
            Learning rate for gradient descent.
        epochs : int
            Maximum number of iterations.
        fit_intercept : bool
            Whether to add bias term (θ0).
        tol : float
            Tolerance for early stopping.
        early_stopping : bool
            Stop GD if improvement < tol.
        """
        self.lr = lr
        self.epochs = epochs
        self.fit_intercept = fit_intercept
        self.tol = tol
        self.early_stopping = early_stopping

        self.theta = None
        self.losses = []

    # -----------------------------
    # Internal utilities
    # -----------------------------
    def _add_intercept(self, X):
        """Add column of ones for intercept term θ0"""
        if self.fit_intercept:
            return np.hstack((np.ones((X.shape[0], 1)), X))
        return X

    def _check_input(self, X, y=None):
        """Validate and reshape input"""
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if y is not None:
            y = np.array(y)
            if y.ndim != 1:
                y = y.ravel()
            if X.shape[0] != y.shape[0]:
                raise ValueError("X and y must have the same number of samples")
        return X, y

    # -----------------------------
    # Fit model
    # -----------------------------
    def fit(self, X, y, method="gradient_descent", verbose=False):
        """
        Train model.

        Parameters
        ----------
        method : str
            'gradient_descent' or 'normal'
        verbose : bool
            Print loss progress
        """
        X, y = self._check_input(X, y)
        X_b = self._add_intercept(X)

        if method == "normal":
            # Normal Equation (closed form solution)
            self.theta = np.linalg.pinv(X_b.T @ X_b) @ X_b.T @ y
            return self

        # Gradient Descent
        n_samples, n_features = X_b.shape
        self.theta = np.zeros(n_features)
        prev_loss = float("inf")
        self.losses = []

        for epoch in range(self.epochs):
            y_pred = X_b @ self.theta
            error = y_pred - y
            grad = (1 / n_samples) * (X_b.T @ error)
            self.theta -= self.lr * grad

            # Compute mean squared error
            loss = np.mean(error ** 2)
            self.losses.append(loss)

            if verbose and epoch % (self.epochs // 10) == 0:
                print(f"Epoch {epoch}: Loss = {loss:.6f}")

            # Early stopping
            if self.early_stopping and abs(prev_loss - loss) < self.tol:
                if verbose:
                    print(f"Early stopping at epoch {epoch}: loss improvement < {self.tol}")
                break
            prev_loss = loss

        return self

    # -----------------------------
    # Predict
    # -----------------------------
    def predict(self, X):
        X, _ = self._check_input(X)
        X_b = self._add_intercept(X)
        return X_b @ self.theta

    # -----------------------------
    # Score (R²)
    # -----------------------------
    def score(self, X, y):
        X, y = self._check_input(X, y)
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot)

    # -----------------------------
    # Visualization utilities
    # -----------------------------
    def plot_loss(self):
        """Plot training loss over epochs"""
        plt.figure(figsize=(6,4))
        plt.plot(self.losses, color='blue', linewidth=2)
        plt.title("Training Loss (MSE) Curve")
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.grid(True)
        plt.show()

    def plot_prediction(self, X, y):
        """
        Plot predictions vs actual data
        Works for 1D feature data
        """
        X, y = self._check_input(X, y)
        if X.shape[1] != 1:
            print("Prediction plot only available for 1D feature data")
            return

        y_pred = self.predict(X)

        plt.figure(figsize=(6,4))
        plt.scatter(X, y, color='red', label='Actual')
        plt.plot(X, y_pred, color='blue', linewidth=2, label='Predicted')
        plt.title("Linear Regression Predictions")
        plt.xlabel("Feature")
        plt.ylabel("Target")
        plt.legend()
        plt.grid(True)
        plt.show()


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Example: simple linear data
    X = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 6, 8, 10])

    model = LinearRegression(lr=0.05, epochs=500, early_stopping=True)
    model.fit(X, y, verbose=True)

    print("Theta:", model.theta)
    print("Prediction for x=6:", model.predict([[6]]))
    print("R² Score:", model.score(X, y))
    print("Last Training Loss:", model.losses[-1])

    # Visualization
    model.plot_loss()
    model.plot_prediction(X, y)
