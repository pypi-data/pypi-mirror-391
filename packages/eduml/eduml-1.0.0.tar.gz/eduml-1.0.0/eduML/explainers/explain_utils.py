"""
eduML.explainers.explain_utils
===============================

Unified explainability interface for eduML.

Author: eduML Team (adjusted for your project)
Version: 1.1
"""

import numpy as np
import matplotlib.pyplot as plt
import textwrap
import json
import datetime
from matplotlib.colors import ListedColormap


# ---------------------------
# Helper printing utilities
# ---------------------------

def print_header(title: str):
    """Prints a formatted section header."""
    print("\n" + "=" * 70)
    print(f"🔍 {title.upper()}")
    print("=" * 70)


def explain_step(description: str, value=None, precision: int = 4):
    """Prints an explanation line with optional numeric value."""
    if value is not None:
        # Format numpy arrays nicely
        if isinstance(value, np.ndarray):
            # show small arrays inline, large arrays by shape
            if value.size <= 8:
                val = np.array2string(value, precision=precision, separator=", ")
            else:
                val = f"array shape={value.shape}"
        elif isinstance(value, (list, tuple)):
            val = value
        elif isinstance(value, (float, np.floating)):
            val = round(float(value), precision)
        else:
            val = value
        print(f"• {description}: {val}")
    else:
        print(f"• {description}")


def show_equation(name: str, formula: str):
    """Displays a labeled mathematical formula in readable format."""
    print(f"📘 {name}: {formula}")


# ---------------------------
# Core explainers
# ---------------------------

def explain_linear_model(weights, bias, metrics=None):
    """Explain Linear or Ridge Regression models."""
    print_header("Linear / Ridge Regression Summary")
    explain_step("Weights (coefficients)", np.asarray(weights))
    explain_step("Bias term", bias)

    if metrics:
        print_header("Performance Metrics")
        for key, val in metrics.items():
            explain_step(key, val)

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ Each weight represents the contribution of a feature to the output. "
        "Large magnitude indicates stronger influence; sign indicates direction."
    ))


def explain_logistic_model(weights, bias, metrics=None):
    """Explain Logistic Regression results."""
    print_header("Logistic Regression Summary")
    explain_step("Weights (coefficients)", np.asarray(weights))
    explain_step("Bias term", bias)

    if metrics:
        print_header("Performance Metrics")
        for key, val in metrics.items():
            explain_step(key, val)

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ Logistic regression estimates class probabilities with sigmoid/softmax. "
        "Positive weights increase probability of class 1."
    ))


def explain_svm(summary):
    """Explain Support Vector Machine (linear) results."""
    print_header("Support Vector Machine Summary")
    explain_step("Support Vectors (count)", len(summary.get("support_vectors", [])))
    explain_step("C (Regularization Parameter)", summary.get("C"))
    explain_step("Training Accuracy", summary.get("accuracy"))

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ SVM constructs a margin-maximizing hyperplane. Support vectors are the "
        "critical points that define the margin."
    ))


def explain_decision_tree(tree_summary):
    """Explain Decision Tree behavior and splits."""
    print_header("Decision Tree Summary")
    explain_step("Total Nodes", tree_summary.get("total_nodes"))
    explain_step("Max Depth", tree_summary.get("depth"))
    explain_step("Criterion", tree_summary.get("criterion"))

    print("\nTop Feature Importances:")
    fi = tree_summary.get("feature_importance", {})
    # Show up to top 8 features
    for i, (feature, imp) in enumerate(sorted(fi.items(), key=lambda x: -x[1])[:8]):
        explain_step(f"{feature}", f"{imp * 100:.2f}%")

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ Decision trees split features to increase purity. Feature importance "
        "shows which features were most useful for splitting."
    ))


def explain_knn(summary):
    """Explain k-NN behaviour."""
    print_header("k-Nearest Neighbors Summary")
    explain_step("k (neighbors)", summary.get("k"))
    explain_step("Distance metric", summary.get("metric"))
    explain_step("Example neighbors shown", summary.get("example_neighbors"))

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ k-NN predicts based on nearest labeled neighbors. Its behavior depends "
        "on k and the distance metric chosen."
    ))


def explain_naive_bayes(summary):
    """Explain Gaussian Naive Bayes summary."""
    print_header("Gaussian Naive Bayes Summary")
    explain_step("Classes", summary.get("classes"))
    explain_step("Per-class means (sample)", summary.get("means_sample"))
    explain_step("Per-class variances (sample)", summary.get("vars_sample"))

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ Naive Bayes assumes conditional independence of features and models "
        "each feature with a simple distribution (e.g., Gaussian)."
    ))


def explain_neural_network(summary):
    """Explain Multi-Layer Perceptron behavior."""
    print_header("Neural Network (MLP) Summary")
    explain_step("Layers", summary.get("n_layers"))
    explain_step("Total Parameters", summary.get("n_params"))
    explain_step("Activation Functions", summary.get("activations"))

    print("\nTraining Overview:")
    explain_step("Final Loss", summary.get("final_loss"))
    explain_step("Accuracy", summary.get("accuracy"))

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ The network learns by adjusting weights to minimize loss. Observing "
        "loss progression and weight distributions helps understand learning dynamics."
    ))


def explain_dim_reduction(summary):
    """Explain PCA / LDA dimensionality reduction results safely and clearly."""
    print_header("Dimensionality Reduction Summary")

    # -------------------------
    # Safe fetch helpers
    # -------------------------
    def safe_var_explained(value):
        """Convert variance_explained into a single float percentage."""
        if value is None:
            return 0.0
        if isinstance(value, (list, tuple, np.ndarray)):
            return float(np.sum(value))   # sum list of components
        return float(value)

    # Fetch
    original_dim = summary.get("original_dim", "?")
    reduced_dim = summary.get("reduced_dim", "?")
    variance = safe_var_explained(summary.get("variance_explained", 0))

    # -------------------------
    # Display
    #---------------------------
    explain_step("Original Dimensions", original_dim)
    explain_step("Reduced Dimensions", reduced_dim)
    explain_step("Variance Explained", f"{variance * 100:.2f}%")

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ Dimensionality reduction compresses data into fewer features while "
        "preserving the structure of the dataset. PCA focuses on maximizing variance, "
        "while LDA maximizes class separability. Larger explained variance means the "
        "reduced features still retain most of the important information."
    ))

def explain_kmeans(summary):
    """Explain K-Means clustering."""
    print_header("K-Means Clustering Summary")
    explain_step("n_clusters", summary.get("n_clusters"))
    explain_step("Iterations", summary.get("n_iter"))
    explain_step("Inertia (final)", summary.get("inertia"))
    explain_step("Cluster centers (sample)", summary.get("centers_sample"))

    print("\nInterpretation:")
    print(textwrap.fill(
        "→ K-Means groups points around centroids iteratively. The inertia measures "
        "within-cluster variance (lower is better)."
    ))


# ---------------------------
# Visualization helpers
# ---------------------------

def plot_loss_curve(losses, title="Loss Curve"):
    """Plot training loss progression."""
    plt.figure(figsize=(6, 4))
    plt.plot(losses, linewidth=2)
    plt.title(title)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.show()


def plot_decision_boundary(model, X, y, resolution=0.02):
    """Plot 2D decision boundary for classifiers (2 features only)."""
    if X.shape[1] < 2:
        print("Decision boundary requires at least 2 features.")
        return
    cmap_light = ListedColormap(["#FFBBBB", "#BBFFBB", "#BBBBFF"])
    cmap_bold = ["#FF0000", "#00AA00", "#0000FF"]

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, resolution),
                         np.arange(y_min, y_max, resolution))

    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict(grid)
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(6, 5))
    plt.contourf(xx, yy, Z, alpha=0.4, cmap=cmap_light)
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolor="k", cmap=ListedColormap(cmap_bold))
    plt.title("Decision Boundary Visualization")
    plt.show()


def plot_explained_variance(ratios):
    """Plot cumulative variance explained for PCA."""
    plt.figure(figsize=(6, 4))
    plt.plot(np.cumsum(ratios) * 100, marker='o')
    plt.title("Cumulative Explained Variance")
    plt.xlabel("Number of Components")
    plt.ylabel("Variance Explained (%)")
    plt.grid(True)
    plt.show()


# ---------------------------
# Utilities
# ---------------------------

def save_explanation_log(summary_dict, filename="explanation_log.json"):
    """Save explanation summary as JSON for reproducibility."""
    summary_dict["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "w") as f:
        json.dump(summary_dict, f, indent=4)
    print(f"\n📝 Explanation log saved to {filename}")


def get_attr_safe(obj, *names, default=None):
    """
    Try multiple possible attribute names and return the first that exists.
    Example:
        get_attr_safe(model, "weights", "coef_", default=None)
    """
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


# ---------------------------
# Unified dispatcher
# ---------------------------

def explain_model(mode: str, model, X=None, y=None):
    """
    Unified explain_model dispatcher.

    mode : one of:
        linear, ridge, logistic, svm, tree, knn, nb, lda, mlp, pca, kmeans

    model : the trained model object (eduML model instance)

    X, y : optional data used for computing accuracy or examples
    """
    mode = (mode or "").strip().lower()

    # --- linear / ridge ---
    if mode in ("linear", "ridge"):
        weights = get_attr_safe(model, "weights", "coef_", "coef", "w", default=None)
        bias = get_attr_safe(model, "bias", "intercept_", "intercept", "b", default=None)

        metrics = {}
        # compute accuracy / rmse only if X,y provided
        if X is not None and y is not None:
            try:
                preds = model.predict(X)
                if preds.ndim == 1 and y.ndim == 1:
                    # classification vs regression detection: treat numeric vs discrete
                    # For regression compute RMSE
                    from sklearn.metrics import mean_squared_error
                    rmse = mean_squared_error(y, preds, squared=False)
                    metrics["RMSE"] = rmse
                # else leave metrics empty
            except Exception:
                pass

        explain_linear_model(weights=weights, bias=bias, metrics=metrics or None)
        return

    # --- logistic ---
    if mode == "logistic":
        weights = get_attr_safe(model, "weights", "coef_", "coef", default=None)
        bias = get_attr_safe(model, "bias", "intercept_", "intercept", default=None)
        metrics = {}
        if X is not None and y is not None:
            try:
                preds = model.predict(X)
                from sklearn.metrics import accuracy_score
                metrics["accuracy"] = accuracy_score(y, preds)
            except Exception:
                pass
        explain_logistic_model(weights=weights, bias=bias, metrics=metrics or None)
        return

    # --- svm ---
    if mode == "svm":
        sv = get_attr_safe(model, "support_vectors", "support_vectors_", default=[])
        C = get_attr_safe(model, "C", default=None)
        acc = None
        if X is not None and y is not None:
            try:
                acc = (model.predict(X) == y).mean()
            except Exception:
                pass
        summary = {"support_vectors": sv, "C": C, "accuracy": acc}
        explain_svm(summary)
        return

    # --- decision tree ---
    if mode in ("tree", "decision_tree"):
        total_nodes = get_attr_safe(model, "total_nodes", "node_count", default=None)
        depth = get_attr_safe(model, "depth", "max_depth", default=None)
        criterion = get_attr_safe(model, "criterion", default=None)
        feature_importance = get_attr_safe(model, "feature_importance", "feature_importances_", default={})
        # if sklearn-style feature_importances_ convert to dict with indices
        if isinstance(feature_importance, np.ndarray):
            feature_importance = {f"f{i}": float(v) for i, v in enumerate(feature_importance)}
        summary = {
            "total_nodes": total_nodes,
            "depth": depth,
            "criterion": criterion,
            "feature_importance": feature_importance
        }
        explain_decision_tree(summary)
        return

    # --- k-NN ---
    if mode in ("knn",):
        k = get_attr_safe(model, "k", "n_neighbors", default=None)
        metric = get_attr_safe(model, "metric", default="euclidean")
        example_neighbors = None
        # try to show neighbors for first test point if X provided
        if X is not None:
            try:
                if hasattr(model, "kneighbors"):
                    neigh = model.kneighbors(X[:1], return_distance=True)
                    example_neighbors = neigh[1].tolist() if len(neigh) > 1 else None
            except Exception:
                example_neighbors = None
        summary = {"k": k, "metric": metric, "example_neighbors": example_neighbors}
        explain_knn(summary)
        return

    # --- Naive Bayes ---
    if mode in ("nb", "naive_bayes"):
        classes = get_attr_safe(model, "classes_", "classes", default=None)
        means = get_attr_safe(model, "class_means_", "theta_", "means", default=None)
        vars_ = get_attr_safe(model, "class_vars_", "sigma_", "vars", default=None)
        # sample small prints
        means_sample = None
        vars_sample = None
        if means is not None:
            try:
                means_arr = np.asarray(means)
                means_sample = means_arr if means_arr.size <= 20 else means_arr[:5].tolist()
            except Exception:
                means_sample = None
        if vars_ is not None:
            try:
                vars_arr = np.asarray(vars_)
                vars_sample = vars_arr if vars_arr.size <= 20 else vars_arr[:5].tolist()
            except Exception:
                vars_sample = None
        summary = {"classes": classes, "means_sample": means_sample, "vars_sample": vars_sample}
        explain_naive_bayes(summary)
        return

    # --- LDA ---
    if mode == "lda":
        original_dim = get_attr_safe(model, "original_dim", "n_features_in_", default=None)
        n_components = get_attr_safe(model, "n_components", default=get_attr_safe(model, "n_components_", default=None))
        explained_variance = get_attr_safe(model, "explained_variance_ratio_", "explained_variance", default=None)
        summary = {"original_dim": original_dim, "reduced_dim": n_components, "variance_explained": explained_variance}
        explain_dim_reduction(summary)
        return

    # --- MLP / Neural ---
    if mode in ("mlp", "neural"):
        acc = None
        if X is not None and y is not None:
            try:
                preds = model.predict(X)
                acc = (preds == y).mean()
            except Exception:
                acc = None

        n_layers = get_attr_safe(model, "n_layers", default=None)
        total_params = get_attr_safe(model, "total_params", "n_params", default=None)
        activations = get_attr_safe(model, "activations", default=None)
        final_loss = None
        if hasattr(model, "loss_history") and model.loss_history:
            final_loss = model.loss_history[-1]
        summary = {
            "n_layers": n_layers,
            "n_params": total_params,
            "activations": activations,
            "final_loss": final_loss,
            "accuracy": acc
        }
        explain_neural_network(summary)
        return

    # --- PCA ---
    if mode == "pca":
        original_dim = get_attr_safe(model, "original_dim", "n_features_in_", default=None)
        n_components = get_attr_safe(model, "n_components", "n_components_", default=None)
        explained_variance = get_attr_safe(model, "explained_variance_ratio_", "explained_variance", default=None)
        summary = {"original_dim": original_dim, "reduced_dim": n_components, "variance_explained": explained_variance}
        explain_dim_reduction(summary)
        return

    # --- KMeans ---
    if mode == "kmeans":
        n_clusters = get_attr_safe(model, "n_clusters", "k", "n_clusters_", default=None)
        n_iter = get_attr_safe(model, "n_iter", "n_iter_", default=None)
        inertia = get_attr_safe(model, "inertia_", "inertia", default=None)
        centers = get_attr_safe(model, "cluster_centers_", "centroids", default=None)
        centers_sample = None
        if centers is not None:
            try:
                centers_arr = np.asarray(centers)
                centers_sample = centers_arr if centers_arr.size <= 20 else centers_arr[:5].tolist()
            except Exception:
                centers_sample = None
        summary = {"n_clusters": n_clusters, "n_iter": n_iter, "inertia": inertia, "centers_sample": centers_sample}
        explain_kmeans(summary)
        return

    # --- Unknown ---
    print_header("ERROR")
    print(f"❌ Unknown explain mode: '{mode}'")
    print("Available modes:")
    print("  • linear, ridge, logistic, svm, tree, knn, nb, lda, mlp, pca, kmeans")
