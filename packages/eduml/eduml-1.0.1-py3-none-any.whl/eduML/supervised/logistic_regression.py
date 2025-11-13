import numpy as np
import matplotlib.pyplot as plt

class LogisticRegression:
    def __init__(self, lr=0.1, epochs=1000, fit_intercept=True, tol=1e-6, early_stopping=False):
        """
        Parameters
        ----------
        lr : float
            Learning rate
        epochs : int
            Maximum number of iterations
        fit_intercept : bool
            Whether to include bias term
        tol : float
            Minimum improvement for early stopping
        early_stopping : bool
            Enable early stopping
        """
        self.lr = lr
        self.epochs = epochs
        self.fit_intercept = fit_intercept
        self.tol = tol
        self.early_stopping = early_stopping

        self.theta = None
        self.losses = []

    # -----------------------------
    # Utilities
    # -----------------------------
    def _add_intercept(self, X):
        if self.fit_intercept:
            return np.hstack((np.ones((X.shape[0], 1)), X))
        return X

    def _check_input(self, X, y=None):
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

    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    # -----------------------------
    # Fit model
    # -----------------------------
    def fit(self, X, y, verbose=False):
        X, y = self._check_input(X, y)
        X_b = self._add_intercept(X)
        n_samples, n_features = X_b.shape

        self.theta = np.zeros(n_features)
        prev_loss = float("inf")
        self.losses = []

        for epoch in range(self.epochs):
            linear_output = X_b @ self.theta
            y_pred = self._sigmoid(linear_output)

            # Gradient descent update
            grad = (1 / n_samples) * X_b.T @ (y_pred - y)
            self.theta -= self.lr * grad

            # Binary cross-entropy loss
            loss = -np.mean(y * np.log(y_pred + 1e-8) + (1 - y) * np.log(1 - y_pred + 1e-8))
            self.losses.append(loss)

            # Verbose logging
            if verbose and epoch % (self.epochs // 10) == 0:
                print(f"Epoch {epoch}: Loss = {loss:.6f}")

            # Early stopping
            if self.early_stopping and abs(prev_loss - loss) < self.tol:
                if verbose:
                    print(f"Early stopping at epoch {epoch}: improvement < {self.tol}")
                break
            prev_loss = loss

        return self

    # -----------------------------
    # Predict probabilities
    # -----------------------------
    def predict_proba(self, X):
        X, _ = self._check_input(X)
        X_b = self._add_intercept(X)
        return self._sigmoid(X_b @ self.theta)

    # -----------------------------
    # Predict classes
    # -----------------------------
    def predict(self, X, threshold=0.5):
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)

    # -----------------------------
    # Accuracy
    # -----------------------------
    def accuracy(self, X, y):
        preds = self.predict(X)
        y, _ = self._check_input(y)
        return np.mean(preds == y) * 100

    # -----------------------------
    # Explanation (NEW FUNCTION)
    # -----------------------------
    def explain(self):
        """
        Explains the model's coefficients and decision boundary.
        """
        if self.theta is None:
            print("Model has not been trained yet. Call .fit() first.")
            return

        print("## 🧠 Model Explanation\n---")
        
        # 1. Explain Coefficients (Theta)
        print("### 📊 Trained Coefficients ($\\theta$)")
        if self.fit_intercept:
            bias = self.theta[0]
            weights = self.theta[1:]
            print(f"* **Bias/Intercept ($\\theta_0$): {bias:.4f}**")
            print("    * This is the baseline log-odds when all features are zero.")
            for i, w in enumerate(weights):
                print(f"* **Weight for Feature {i+1} ($\\theta_{i+1}$): {w:.4f}**")
                
                # Simple interpretation for weight
                if w > 0:
                    print("    * A positive weight means this feature **increases** the log-odds of the outcome being 1.")
                elif w < 0:
                    print("    * A negative weight means this feature **decreases** the log-odds of the outcome being 1.")
                else:
                    print("    * A zero weight means this feature has no impact on the log-odds.")
            print("\n")

        else:
            weights = self.theta
            for i, w in enumerate(weights):
                print(f"* **Weight for Feature {i+1} ($\\theta_{i}$): {w:.4f}**")
            print("\n")

        # 2. Decision Boundary
        print("### 📐 Decision Boundary (Linear Separator)")
        
        # The decision boundary is defined where the predicted probability is 0.5,
        # which means the linear combination of inputs is 0 (i.e., theta @ X_b = 0).
        
        theta_str = []
        if self.fit_intercept:
            theta_str.append(f"{self.theta[0]:.4f}")
            for i, w in enumerate(self.theta[1:]):
                sign = '+' if w >= 0 else ''
                theta_str.append(f"{sign}{w:.4f} \cdot x_{i+1}")
        else:
             for i, w in enumerate(self.theta):
                sign = '+' if w >= 0 and i > 0 else ''
                theta_str.append(f"{sign}{w:.4f} \cdot x_{i+1}")
        
        boundary_equation = " + ".join(theta_str).replace("+ -", "- ")

        print("The linear equation $\\theta^T X = 0$ defines the boundary where P(Y=1) = 0.5.")
        print(f"> **Boundary Equation:** ${boundary_equation} = 0$")
        print("\n")
        
        print("### 💡 Core Concept")
        print("Logistic Regression models the **log-odds** (log-probability of $Y=1$ vs $Y=0$) as a linear function of the input features.")


    # -----------------------------
    # Visualization
    # -----------------------------
    def plot_loss(self):
        """Plot training binary cross-entropy loss curve"""
        plt.figure(figsize=(6,4))
        plt.plot(self.losses, color='blue', linewidth=2)
        plt.title("Binary Cross-Entropy Loss Curve")
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.grid(True)
        plt.show()

    def plot_decision_boundary(self, X, y):
        """
        Plot decision boundary (for 2D features only)
        """
        X, y = self._check_input(X, y)
        if X.shape[1] != 2:
            print("Decision boundary plot only available for 2D data")
            return

        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                             np.linspace(y_min, y_max, 300))
        grid = np.c_[xx.ravel(), yy.ravel()]
        Z = self.predict(grid)
        Z = Z.reshape(xx.shape)

        plt.figure(figsize=(6,5))
        plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.Paired)
        plt.scatter(X[:, 0], X[:, 1], c=y, edgecolor='k', cmap=plt.cm.Paired)
        plt.title("Logistic Regression Decision Boundary")
        plt.xlabel("Feature 1")
        plt.ylabel("Feature 2")
        plt.show()


# -----------------------------
# Example usage with NEW explain()
# -----------------------------
if __name__ == "__main__":
    # Simple 2D binary classification
    X = np.array([[0, 1], [1, 1], [2, 0], [3, 1], [4, 0]])
    y = np.array([0, 0, 0, 1, 1])

    model = LogisticRegression(lr=0.1, epochs=1000, early_stopping=True, tol=1e-6)
    model.fit(X, y, verbose=False) # Changed to False for cleaner output here

    print("--- Example Usage Results ---")
    print(f"Final Theta: {model.theta}")
    print(f"Predictions for [[1.5, 0.5], [3, 1]]: {model.predict([[1.5, 0.5], [3, 1]])}")
    print(f"Accuracy: {model.accuracy(X, y):.2f}%")
    
    print("\n" + "="*40 + "\n")
    model.explain()
    print("\n" + "="*40 + "\n")

    # Visualization
    model.plot_loss()
    model.plot_decision_boundary(X, y)