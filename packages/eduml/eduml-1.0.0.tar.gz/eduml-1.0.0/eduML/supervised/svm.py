"""
svm.py — Improved & Educational SVM for eduML
---------------------------------------------

Features:
  - Stable hinge-loss gradient (SGD / mini-batch)
  - One-vs-Rest (OvR) multi-class support
  - Per-class loss history, support vector indices (margin / violators)
  - Learning rate schedule, optional shuffling
  - 2D decision-boundary visualization for demos
  - explain() and a runnable main() demo (no sklearn)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Dict, Any


class LinearSVM:
    def __init__(
        self,
        lr: float = 0.01,
        epochs: int = 1000,
        C: float = 1.0,
        batch_size: Optional[int] = None,
        shuffle: bool = True,
        decay: float = 0.0,
        learning_mode: bool = False,
    ):
        """
        Parameters
        ----------
        lr : float
            Initial learning rate (SGD step).
        epochs : int
            Number of epochs (passes over the data).
        C : float
            Regularization / hinge-loss weight.
        batch_size : Optional[int]
            None or >= n_samples -> full-batch. 1 -> SGD. >1 -> mini-batch.
        shuffle : bool
            Whether to shuffle at each epoch.
        decay : float
            Learning rate decay factor. lr_t = lr / (1 + decay * t)
        learning_mode : bool
            If True prints training progress occasionally.
        """
        self.lr = float(lr)
        self.epochs = int(epochs)
        self.C = float(C)
        self.batch_size = None if batch_size is None else int(batch_size)
        self.shuffle = bool(shuffle)
        self.decay = float(decay)
        self.learning_mode = bool(learning_mode)

       
        self.classes_: Optional[np.ndarray] = None
        self.W: Optional[np.ndarray] = None         
        self.b: Optional[np.ndarray] = None        
        self.loss_history: Dict[Any, list] = {}   
       
        self.support_vectors_: Dict[Any, Dict[str, np.ndarray]] = {}


    def _hinge_loss_and_grad(self, X_b: np.ndarray, y_b: np.ndarray, w: np.ndarray, b: float
                            ) -> Tuple[float, np.ndarray, float, np.ndarray]:
        """
        Compute hinge loss and gradients for a batch (X_b, y_b).
        y_b should be in {-1, +1}.
        Returns: (loss, dw, db, miss_mask)
        dw and db are scaled by batch size outside (we divide by n later).
        """
        n = X_b.shape[0]
        scores = X_b @ w + b                      # (n,)
        margins = y_b * scores                    # (n,)

        miss_mask = margins < 1.0                 # boolean array
        if miss_mask.any():
           
            dw_hinge = - (X_b[miss_mask].T @ y_b[miss_mask])  
            db_hinge = - np.sum(y_b[miss_mask])               
            hinge_loss = np.sum(np.maximum(0.0, 1.0 - margins))
        else:
            dw_hinge = np.zeros_like(w)
            db_hinge = 0.0
            hinge_loss = 0.0

        
        loss = 0.5 * float(w @ w) + self.C * float(hinge_loss)
        dw = w + (self.C * dw_hinge)   # full gradient
        db = self.C * db_hinge

      
        return loss, dw, db, miss_mask

    def _iter_batches(self, X: np.ndarray, y: np.ndarray):
        n = X.shape[0]
        if self.batch_size is None or self.batch_size >= n:
            yield X, y
            return

        indices = np.arange(n)
        for start in range(0, n, self.batch_size):
            batch_idx = indices[start:start + self.batch_size]
            yield X[batch_idx], y[batch_idx]

    # -------------------------
    # Binary trainer
    # -------------------------
    def _fit_binary(self, X: np.ndarray, y_bin: np.ndarray, verbose_prefix: str = "") -> Tuple[np.ndarray, float, list, np.ndarray, np.ndarray, np.ndarray]:
        """
        Train binary SVM for labels in {-1, +1}.
        Returns: (w, b, losses, support_idx, margin_idx, violator_idx)
        """
        n_samples, n_features = X.shape
        w = np.zeros(n_features, dtype=float)
        b = 0.0
        losses = []

        base_lr = self.lr

        # ensure batch ops operate on local copies for shuffle safety
        X_work = X.copy()
        y_work = y_bin.copy()

        for epoch in range(self.epochs):
            lr_t = base_lr / (1.0 + self.decay * epoch)

            if self.shuffle:
                perm = np.random.permutation(n_samples)
                X_work = X_work[perm]
                y_work = y_work[perm]

            # iterate batches
            for X_batch, y_batch in self._iter_batches(X_work, y_work):
                loss_batch, dw, db, _ = self._hinge_loss_and_grad(X_batch, y_batch, w, b)
                # scale gradient by batch size
                scale = float(max(1, X_batch.shape[0]))
                w -= (lr_t * (dw / scale))
                b -= (lr_t * (db / scale))

            # compute full-batch loss and store
            loss_full, _, _, miss_mask_full = self._hinge_loss_and_grad(X, y_bin, w, b)
            losses.append(float(loss_full))

            if self.learning_mode and (epoch % max(1, (self.epochs // 10)) == 0):
                print(f"{verbose_prefix}Epoch {epoch:4d} | loss={loss_full:.6f} | violations={miss_mask_full.sum()} | lr={lr_t:.6g}")

        # final margins and support-like selection
        final_margins = y_bin * (X @ w + b)   # shape (n_samples,)
        # scale-aware epsilon: small fraction of mean absolute margin (handles feature scaling)
        mean_margin_abs = float(np.mean(np.abs(final_margins))) if final_margins.size > 0 else 0.0
        eps = max(1e-6, 1e-3 * (mean_margin_abs if mean_margin_abs > 0 else 1.0))

        # margin points (approximately on margin)
        margin_idx = np.where(np.isclose(final_margins, 1.0, atol=eps))[0]
        # violators (strictly inside margin)
        violator_idx = np.where(final_margins < 1.0 - 1e-12)[0]
        # support = union of the two
        support_idx = np.union1d(margin_idx, violator_idx)

        return w, b, losses, support_idx, margin_idx, violator_idx

    # -------------------------
    # Public API
    # -------------------------
    def fit(self, X, y):
        """
        Fit SVM. Supports multiclass via One-vs-Rest (OvR).

        After fit:
            - self.classes_ contains ordered unique labels
            - self.W and self.b store per-class classifiers
            - self.loss_history[class] = [...]
            - self.support_vectors_[class] = {"support": idxs, "margin": idxs, "violators": idxs}
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)

        if X.ndim != 2:
            raise ValueError("X must be 2D array (n_samples, n_features).")

        self.classes_, inv = np.unique(y, return_inverse=True)
        n_classes = len(self.classes_)
        n_samples, n_features = X.shape

        # allocate storage (keeps indices consistent with older code that used index 1 for binary)
        self.W = np.zeros((max(2, n_classes), n_features), dtype=float)
        self.b = np.zeros(max(2, n_classes), dtype=float)
        self.loss_history = {}
        self.support_vectors_ = {}

        # binary special-case (store result at index 1)
        if n_classes == 2:
            # map first unique class to -1, second to +1
            y_bin = np.where(y == self.classes_[0], -1, 1)
            w, b, losses, support_idx, margin_idx, violator_idx = self._fit_binary(X, y_bin, verbose_prefix="[binary] ")
            # place at index 1 to maintain parity with previous code expectations
            self.W[1, :] = w
            self.b[1] = b
            self.loss_history[self.classes_[1]] = losses
            self.support_vectors_[self.classes_[1]] = {
                "support": support_idx,
                "margin": margin_idx,
                "violators": violator_idx
            }
            return self

        # multiclass OvR
        for idx, cls in enumerate(self.classes_):
            if self.learning_mode:
                print(f"\n>>> OvR training for class {cls} ({idx+1}/{n_classes})")
            y_bin = np.where(y == cls, 1, -1)
            w, b, losses, support_idx, margin_idx, violator_idx = self._fit_binary(X, y_bin, verbose_prefix=f"[OvR:{cls}] ")
            self.W[idx, :] = w
            self.b[idx] = b
            self.loss_history[cls] = losses
            self.support_vectors_[cls] = {
                "support": support_idx,
                "margin": margin_idx,
                "violators": violator_idx
            }

        return self

    def decision_function(self, X):
        """
        Return raw decision scores.
        Binary: returns shape (n_samples,) from index 1 classifier.
        Multiclass: returns (n_samples, n_classes).
        """
        X = np.asarray(X, dtype=float)
        if self.classes_ is None:
            raise ValueError("Call fit() before decision_function().")

        if len(self.classes_) == 2:
            return X @ self.W[1, :] + self.b[1]
        return X @ self.W.T + self.b

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        if self.classes_ is None:
            raise ValueError("Call fit() before predict().")

        if len(self.classes_) == 2:
            scores = self.decision_function(X)
            return np.where(scores >= 0.0, self.classes_[1], self.classes_[0])
        scores = self.decision_function(X)   # (n_samples, n_classes)
        idx = np.argmax(scores, axis=1)
        return self.classes_[idx]

    def accuracy(self, X, y):
        preds = self.predict(X)
        return float(np.mean(preds == y) * 100.0)

    # -------------------------
    # Visualization (2D only)
    # -------------------------
    def visualize(self, X, y, show_support=True):
        """
        Visualize 2D data and decision boundary (binary) or class scatter (multiclass).
        show_support: if True, plot support/violators with distinct markers.
        """
        X = np.asarray(X)
        y = np.asarray(y)
        if X.shape[1] != 2:
            print("[visualize] Visualization available only for 2D features.")
            return

        plt.figure(figsize=(7, 6))
        for cls in self.classes_:
            pts = X[y == cls]
            plt.scatter(pts[:, 0], pts[:, 1], label=str(cls), alpha=0.7, edgecolor="k")

        
        if len(self.classes_) == 2:
            w = self.W[1]
            b = self.b[1]
            if np.allclose(w, 0.0):
                plt.title("SVM: trivial/zero weights (didn't converge)")
            else:
                x0 = np.linspace(np.min(X[:, 0]) - 0.5, np.max(X[:, 0]) + 0.5, 300)
                x1 = -(w[0] * x0 + b) / (w[1] + 1e-12)
                plt.plot(x0, x1, "k-", lw=2, label="Decision boundary")

                # approximate margin lines
                norm_w = np.linalg.norm(w) + 1e-12
                margin = 1.0 / norm_w
                plt.plot(x0, x1 + margin, "k--", lw=1, alpha=0.6)
                plt.plot(x0, x1 - margin, "k--", lw=1, alpha=0.6)

            if show_support:
                sv_idx = self.support_vectors_.get(self.classes_[1], {}).get("support", np.array([], dtype=int))
                viol_idx = self.support_vectors_.get(self.classes_[1], {}).get("violators", np.array([], dtype=int))
                margin_idx = self.support_vectors_.get(self.classes_[1], {}).get("margin", np.array([], dtype=int))

                if len(sv_idx) > 0:
                    sv = X[sv_idx]
                    plt.scatter(sv[:, 0], sv[:, 1], facecolors="none", edgecolors="r", s=110, label="Support-like")
                if len(viol_idx) > 0:
                    vv = X[viol_idx]
                    plt.scatter(vv[:, 0], vv[:, 1], marker="x", color="orange", s=60, label="Violators")
                if len(margin_idx) > 0:
                    mm = X[margin_idx]
                    plt.scatter(mm[:, 0], mm[:, 1], marker="o", facecolors="none", edgecolors="purple", s=80, label="Margin approx")

        plt.legend()
        plt.title("eduML Linear SVM (2D visualization)")
        plt.grid(alpha=0.3)
        plt.show()

    
    def explain(self):
        print("\n📘 Support Vector Machine Explanation")
        print("-------------------------------------")
        print(f"Learning rate (init): {self.lr}")
        print(f"Epochs: {self.epochs}")
        print(f"Regularization (C): {self.C}")
        print(f"Classes: {self.classes_}")

        if len(self.classes_) == 2:
            cls = self.classes_[1]
            print("\nBinary SVM (stored at index 1):")
            print(f"  w: {np.round(self.W[1], 6)}")
            print(f"  b: {np.round(self.b[1], 6)}")
            losses = self.loss_history.get(cls, [])
            if losses:
                print(f"  Final loss: {losses[-1]:.6f}")
                print(f"  Loss history (last 5): {np.round(losses[-5:], 6)}")
            sv = self.support_vectors_.get(cls, {})
            print(f"  Support-like count: {len(sv.get('support', []))}")
            print(f"  Margin approx count: {len(sv.get('margin', []))}")
            print(f"  Violators count: {len(sv.get('violators', []))}")
        else:
            for idx, cls in enumerate(self.classes_):
                print(f"\nOvR classifier for class {cls}:")
                print(f"  w: {np.round(self.W[idx], 6)}")
                print(f"  b: {np.round(self.b[idx], 6)}")
                losses = self.loss_history.get(cls, [])
                if losses:
                    print(f"  Final loss: {losses[-1]:.6f} (last 5: {np.round(losses[-5:],6)})")
                sv = self.support_vectors_.get(cls, {})
                print(f"  Support-like count: {len(sv.get('support', []))}")
                print(f"  Margin approx count: {len(sv.get('margin', []))}")
                print(f"  Violators count: {len(sv.get('violators', []))}")

        print("\nNotes:")
        print(" - 'Support-like' are samples on or inside the margin (approx).")
        print(" - 'Violators' are samples inside the margin (may be misclassified).")
        print(" - This SVM uses SGD/mini-batch; exact support vectors as in QP SVM may differ slightly.")


class SimpleScaler:
    def fit(self, X: np.ndarray):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0) + 1e-9
        return self

    def transform(self, X: np.ndarray):
        return (X - self.mean_) / self.std_

    def fit_transform(self, X: np.ndarray):
        self.fit(X)
        return self.transform(X)

def make_synthetic_classification(n_samples=300, n_features=2, class_sep=1.5, random_state=1):
    """
    Simple two-class gaussian blobs generator (no sklearn).
    """
    np.random.seed(random_state)
    half = n_samples // 2
    mean0 = np.zeros(n_features)
    mean1 = np.ones(n_features) * class_sep
    cov = np.eye(n_features)
    X0 = np.random.multivariate_normal(mean0, cov, half)
    X1 = np.random.multivariate_normal(mean1, cov, n_samples - half)
    X = np.vstack([X0, X1])
    y = np.array([0] * half + [1] * (n_samples - half))
    return X, y

def load_tiny_iris():
    """
    Tiny iris-like dataset (2D projection) used for demo/walkthrough.
    """
    X = np.array([
        [5.1, 3.5], [4.9, 3.0], [4.7, 3.2], [4.6, 3.1], [5.0, 3.6],
        [7.0, 3.2], [6.4, 3.2], [6.9, 3.1], [5.5, 2.3], [6.5, 2.8],
        [6.3, 3.3], [5.8, 2.7], [7.1, 3.0], [6.3, 2.9], [6.5, 3.0]
    ])
    y = np.array([
        0, 0, 0, 0, 0,
        1, 1, 1, 1, 1,
        2, 2, 2, 2, 2
    ])
    return X, y


def main():
    print("=== eduML LinearSVM demo (no sklearn) ===")

    # ---------- Synthetic binary classification ----------
    Xb, yb = make_synthetic_classification(n_samples=300, class_sep=1.5, random_state=2)
    scaler = SimpleScaler()
    Xb = scaler.fit_transform(Xb)

    model = LinearSVM(
        lr=0.05,
        epochs=180,
        C=1.0,
        batch_size=32,
        shuffle=True,
        decay=1e-3,
        learning_mode=True
    )

    print("\n-- Training synthetic binary dataset --")
    model.fit(Xb, yb)
    acc = model.accuracy(Xb, yb)
    print(f"[Synthetic binary] Training accuracy: {acc:.2f}%")
    model.explain()
    model.visualize(Xb, yb)

    X_iris, y_iris = load_tiny_iris()
    scaler2 = SimpleScaler()
    X2 = scaler2.fit_transform(X_iris)

    svm_iris = LinearSVM(
        lr=0.02,
        epochs=260,
        C=0.6,
        batch_size=16,
        learning_mode=True
    )

    print("\n-- Training tiny iris-like multiclass dataset --")
    svm_iris.fit(X2, y_iris)
    acc2 = svm_iris.accuracy(X2, y_iris)
    print(f"[Tiny Iris-like] Training accuracy: {acc2:.2f}%")
    svm_iris.explain()
    svm_iris.visualize(X2, y_iris)

    print("\nDemo finished.")

if __name__ == "__main__":
    main()
