"""
mlp.py — Deeply Improved MLP for eduML
---------------------------------------
Features:
1. Fully vectorized forward/backward pass (fast & clean)
2. He initialization for better convergence
3. Supports binary & multi-class classification
4. Mini-batch gradient descent
5. Early stopping
6. Numerical stability (sigmoid/softmax clipping)
7. Tracks loss and accuracy per epoch
8. Explains architecture, parameters, and final results
9. Visualizations for loss & decision boundaries
10. Modular, easy-to-read, educational
"""

import numpy as np
import matplotlib.pyplot as plt


class MLP:
    def __init__(
        self,
        input_dim,
        hidden_dim=8,
        output_dim=1,
        lr=0.01,
        epochs=1000,
        batch_size=32,
        early_stop=False,
        patience=20,
        learning_mode=False,
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.early_stop = early_stop
        self.patience = patience
        self.learning_mode = learning_mode

        # -------------------------------
        # He Initialization for hidden
        # -------------------------------
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2 / input_dim)
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2 / hidden_dim)
        self.b2 = np.zeros((1, output_dim))

        # Track history
        self.loss_history = []
        self.accuracy_history = []

        # Explainable info
        self.n_layers = 3
        self.activations = ["sigmoid", "sigmoid" if output_dim == 1 else "softmax"]
        self.total_params = self.W1.size + self.b1.size + self.W2.size + self.b2.size

    # -------------------------------
    # Activation Functions
    # -------------------------------
    def _sigmoid(self, z):
        z = np.clip(z, -40, 40)
        return 1 / (1 + np.exp(-z))

    def _sigmoid_deriv(self, a):
        return a * (1 - a)

    def _softmax(self, z):
        z = z - np.max(z, axis=1, keepdims=True)
        exp_z = np.exp(z)
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)

    # -------------------------------
    # Forward Pass
    # -------------------------------
    def _forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self._sigmoid(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self._softmax(self.z2) if self.output_dim > 1 else self._sigmoid(self.z2)
        return self.a2

    # -------------------------------
    # Backward Pass (Vectorized)
    # -------------------------------
    def _backward(self, X, y, a2):
        m = X.shape[0]
        # Output layer gradient
        if self.output_dim > 1:
            y_onehot = np.zeros_like(a2)
            y_onehot[np.arange(m), y.astype(int)] = 1
            dz2 = a2 - y_onehot
        else:
            dz2 = a2 - y.reshape(-1, 1)

        dW2 = (self.a1.T @ dz2) / m
        db2 = np.sum(dz2, axis=0, keepdims=True) / m

        dz1 = (dz2 @ self.W2.T) * self._sigmoid_deriv(self.a1)
        dW1 = (X.T @ dz1) / m
        db1 = np.sum(dz1, axis=0, keepdims=True) / m

        # Gradient update
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2

    # -------------------------------
    # Loss Function (Cross-Entropy)
    # -------------------------------
    def _compute_loss(self, y, a2):
        m = y.shape[0]
        if self.output_dim > 1:
            y_onehot = np.zeros_like(a2)
            y_onehot[np.arange(m), y.astype(int)] = 1
            return -np.sum(y_onehot * np.log(a2 + 1e-9)) / m
        return -np.mean(
            y * np.log(a2 + 1e-9) + (1 - y) * np.log(1 - a2 + 1e-9)
        )

    # -------------------------------
    # Fit Method with Mini-Batches & Early Stop
    # -------------------------------
    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        m = X.shape[0]

        best_loss = float("inf")
        patience_counter = 0

        for epoch in range(self.epochs):
            # Shuffle for mini-batch
            shuffle_idx = np.random.permutation(m)
            X, y = X[shuffle_idx], y[shuffle_idx]

            for i in range(0, m, self.batch_size):
                Xb = X[i:i + self.batch_size]
                yb = y[i:i + self.batch_size]
                a2b = self._forward(Xb)
                self._backward(Xb, yb, a2b)

            # Epoch loss & accuracy
            a2_full = self._forward(X)
            loss = self._compute_loss(y, a2_full)
            self.loss_history.append(loss)
            acc = self.accuracy(X, y)
            self.accuracy_history.append(acc)

            if self.learning_mode:
                print(f"Epoch {epoch+1:03d}/{self.epochs}  Loss={loss:.4f}  Accuracy={acc:.2f}%")

            # Early stopping
            if self.early_stop:
                if loss < best_loss:
                    best_loss = loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.patience:
                        if self.learning_mode:
                            print("Early stopping triggered.")
                        break

        return self

    # -------------------------------
    # Prediction & Accuracy
    # -------------------------------
    def predict(self, X):
        a2 = self._forward(np.array(X))
        if self.output_dim > 1:
            return np.argmax(a2, axis=1)
        return (a2 > 0.5).astype(int).flatten()

    def accuracy(self, X, y):
        preds = self.predict(X)
        return np.mean(preds == y) * 100

    # -------------------------------
    # Visualization
    # -------------------------------
    def visualize_loss(self):
       
        # Figure 1: Loss
        plt.figure(figsize=(6, 4))
        plt.plot(self.loss_history, label="Loss", color='tab:blue')
        plt.title("MLP Training Loss Curve")
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.grid(True)
        plt.legend()
        plt.show()

        # Figure 2: Accuracy
        plt.figure(figsize=(6, 4))
        plt.plot(self.accuracy_history, label="Accuracy (%)", color='tab:orange')
        plt.title("MLP Training Accuracy Curve")
        plt.xlabel("Epochs")
        plt.ylabel("Accuracy (%)")
        plt.grid(True)
        plt.legend()
        plt.show()
    # -------------------------------
    # Explain Architecture
    # -------------------------------
    def explain(self):
        print("\n=== Multi-Layer Perceptron (MLP) Explanation ===")
        print(f"Input Layer: {self.input_dim} neurons")
        print(f"Hidden Layer: {self.hidden_dim} neurons")
        print(f"Output Layer: {self.output_dim} neurons")
        print(f"Activations: {self.activations}")
        print(f"Total parameters: {self.total_params}")
        if self.loss_history:
            print(f"Final Loss: {self.loss_history[-1]:.4f}")
            print(f"Final Accuracy: {self.accuracy_history[-1]:.2f}%")
        print("Forward pass produces probabilities (sigmoid or softmax).")
        print("Backpropagation updates weights using gradient descent.")


# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    from sklearn.datasets import load_iris

    X, y = load_iris(return_X_y=True)
    mlp = MLP(
        input_dim=X.shape[1],
        hidden_dim=16,
        output_dim=len(np.unique(y)),
        lr=0.05,
        epochs=300,
        batch_size=16,
        early_stop=True,
        learning_mode=True,
    )
    mlp.fit(X, y)
    print("Final Accuracy:", mlp.accuracy(X, y))
    mlp.visualize_loss()
    mlp.explain()
