#!/usr/bin/env python3
"""
eduML Streamlit App
------------------
Educational Machine Learning UI for interactive experiments.

Features:
- Train, Compare, Explain models (Linear, Logistic, SVM, MLP, Decision Tree, Ridge, LDA, PCA)
- Handles regression, classification, unsupervised
- Robust input handling, safe metrics, safe visualization
- Uses eduML core implementations
"""

import os
import json
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# ------------------------
# eduML imports
# ------------------------
from eduML.interface.data_utils import prepare_data
from eduML.supervised.linear_regression import LinearRegression
from eduML.supervised.ridge_regression import RidgeRegression
from eduML.supervised.logistic_regression import LogisticRegression
from eduML.supervised.svm import LinearSVM
from eduML.supervised.decision_tree import DecisionTree
from eduML.supervised.neural_network import MLP
from eduML.supervised.lda import LDA
from eduML.unsupervised.pca import PCA
from eduML.explainers.explain_utils import explain_model

# ------------------------
# Config
# ------------------------
CONFIG_PATH = os.path.expanduser("~/.eduml/app_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(model, dataset):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"model": model, "dataset": dataset}, f, indent=4)
    except Exception:
        pass

# ------------------------
# Model Aliases
# ------------------------
MODEL_ALIASES = {
    "linear": "linear",
    "ridge": "ridge",
    "logistic": "logistic",
    "linear_svm": "svm",
    "svm": "svm",
    "tree": "tree",
    "decision_tree": "tree",
    "neural_network": "mlp",
    "mlp": "mlp",
    "pca": "pca",
    "lda": "lda",
}

def canonical_model_name(name):
    if not name:
        return None
    return MODEL_ALIASES.get(name.strip().lower(), None)

# ------------------------
# Model Factory
# ------------------------
def get_model(canonical_name, input_dim=None):
    """Factory function to create eduML models."""
    if canonical_name == "linear":
        return LinearRegression()
    if canonical_name == "ridge":
        return RidgeRegression()
    if canonical_name == "logistic":
        return LogisticRegression()
    if canonical_name == "svm":
        return LinearSVM()
    if canonical_name == "tree":
        return DecisionTree()
    if canonical_name == "lda":
        return LDA()
    if canonical_name == "pca":
        return PCA(n_components=2)
    if canonical_name == "mlp":
        if input_dim is None:
            raise ValueError("MLP requires input_dim.")
        return MLP(input_dim=input_dim, hidden_dim=16, output_dim=1, lr=0.01, epochs=500, learning_mode=True)
    raise ValueError(f"Unknown canonical model '{canonical_name}'")

# ------------------------
# Utilities
# ------------------------
def safe_predict(model, X):
    """Ensure X is 2D and compatible with model predictions."""
    X = np.array(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    try:
        return model.predict(X)
    except Exception as e:
        st.warning(f"Prediction failed: {e}")
        return None

def plot_regression_line(model, X_train, y_train):
    """Plot 1D or 2D regression fits."""
    plt.figure(figsize=(6,4))
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    if X_train.shape[1] == 1:
        plt.scatter(X_train[:,0], y_train, label="Train")
        y_pred = safe_predict(model, X_train)
        if y_pred is not None:
            plt.plot(X_train[:,0], y_pred, color="r", label="Prediction")
        plt.xlabel("Feature 1")
        plt.ylabel("Target")
        plt.title("Regression Fit")
        plt.legend()
        st.pyplot(plt)
    elif X_train.shape[1] == 2:
        try:
            from eduML.metrics.visualize import plot_decision_boundary
            plot_decision_boundary(model, X_train, y_train, title="Regression Decision Boundary")
            st.pyplot(plt)
        except Exception:
            st.info("2D regression visualization unavailable.")
    else:
        st.info("Regression visualization only available for 1D or 2D features.")

# ------------------------
# Streamlit UI
# ------------------------
def main():
    st.set_page_config(page_title="eduML Interactive App", layout="wide")
    st.title("🚀 eduML Interactive App")
    st.write("Educational Machine Learning Toolkit")

    # Load config
    cfg = load_config()
    default_model = cfg.get("model", "svm")
    default_dataset = cfg.get("dataset", "iris")

    # Sidebar
    st.sidebar.header("Configuration")
    model_name = st.sidebar.selectbox(
        "Select Model",
        options=list(MODEL_ALIASES.keys()),
        index=list(MODEL_ALIASES.keys()).index(default_model) if default_model in MODEL_ALIASES else 0
    )
    dataset_name = st.sidebar.selectbox(
        "Select Dataset",
        options=["iris", "linear", "wine", "digits"],
        index=["iris", "linear", "wine", "digits"].index(default_dataset) if default_dataset in ["iris", "linear", "wine", "digits"] else 0
    )
    action = st.sidebar.radio("Action", ["Train", "Compare", "Explain"])
    st.sidebar.markdown("---")

    # Prepare data
    try:
        X_train, X_test, y_train, y_test = prepare_data(dataset_name)
        input_dim = X_train.shape[1]
    except Exception as e:
        st.error(f"Failed to load dataset '{dataset_name}': {e}")
        return

    canon = canonical_model_name(model_name)
    if canon is None:
        st.error(f"Unknown model selection: {model_name}")
        return

    # ------------------------
    # TRAIN
    # ------------------------
    if action == "Train":
        st.header(f"Training {canon} on {dataset_name}")
        model = get_model(canon, input_dim=input_dim)
        try:
            model.fit(X_train, y_train)
        except Exception as e:
            st.error(f"Training failed: {e}")
            return

        y_pred = safe_predict(model, X_test)

        # Regression
        if canon in ("linear", "ridge"):
            from sklearn.metrics import mean_squared_error, r2_score
            if y_pred is not None:
                y_test_reshaped = np.array(y_test).reshape(-1,)
                y_pred_reshaped = np.array(y_pred).reshape(-1,)
                try:
                    rmse = mean_squared_error(y_test_reshaped, y_pred_reshaped, squared=False)
                    r2 = r2_score(y_test_reshaped, y_pred_reshaped)
                    st.success(f"✅ Regression Metrics:\n- RMSE: {rmse:.4f}\n- R² Score: {r2:.4f}")
                    plot_regression_line(model, X_train, y_train)
                except Exception as e:
                    st.warning(f"Metric calculation failed: {e}")
            else:
                st.warning("Prediction failed; metrics unavailable.")
        # Classification
        else:
            if y_pred is not None:
                try:
                    preds = np.array(y_pred).ravel()
                    y_true = np.array(y_test).ravel()
                    if len(preds) != len(y_true):
                        raise ValueError("Prediction length mismatch.")
                    acc = np.mean(preds == y_true) * 100
                    st.success(f"✅ Classification Accuracy: {acc:.2f}%")
                except Exception as e:
                    st.warning(f"Metric calculation failed: {e}")
            else:
                st.warning("Prediction failed; metrics unavailable.")

    # ------------------------
    # COMPARE
    # ------------------------
    elif action == "Compare":
        st.header(f"Comparing eduML {canon} with Scikit-learn")
        from sklearn import (
            linear_model, svm, tree, neural_network, decomposition, discriminant_analysis
        )

        skl_map = {
            "linear": linear_model.LinearRegression(),
            "ridge": linear_model.Ridge(),
            "logistic": linear_model.LogisticRegression(max_iter=1000),
            "svm": svm.SVC(),
            "tree": tree.DecisionTreeClassifier(),
            "mlp": neural_network.MLPClassifier(hidden_layer_sizes=(16,), max_iter=500),
            "pca": decomposition.PCA(n_components=2),
            "lda": discriminant_analysis.LinearDiscriminantAnalysis(),
        }

        # eduML
        edu_model = get_model(canon, input_dim=input_dim)
        try:
            edu_model.fit(X_train, y_train)
            y_pred = safe_predict(edu_model, X_test)
            if canon in ("linear", "ridge"):
                from sklearn.metrics import mean_squared_error
                edu_val = mean_squared_error(y_test, y_pred, squared=False)
                edu_metric = "RMSE"
            else:
                edu_val = np.mean(y_pred == y_test) * 100
                edu_metric = "Accuracy"
        except Exception:
            edu_val, edu_metric = None, None

        # sklearn
        skl_model = skl_map.get(canon)
        try:
            skl_model.fit(X_train, y_train)
            skl_pred = skl_model.predict(X_test)
            if canon in ("linear", "ridge"):
                from sklearn.metrics import mean_squared_error
                skl_val = mean_squared_error(y_test, skl_pred, squared=False)
                skl_metric = "RMSE"
            else:
                skl_val = np.mean(skl_pred == y_test) * 100
                skl_metric = "Accuracy"
        except Exception:
            skl_val, skl_metric = None, None

        st.subheader("Comparison Results")
        if edu_val is not None:
            st.success(f"eduML {edu_metric}: {edu_val:.4f}")
        else:
            st.warning("eduML result not available")

        if skl_val is not None:
            st.success(f"Scikit-learn {edu_metric}: {skl_val:.4f}")
        else:
            st.warning("Scikit-learn result not available")

    # ------------------------
    # EXPLAIN
    # ------------------------
    elif action == "Explain":
        st.header(f"Explaining {canon}")
        model = get_model(canon, input_dim=input_dim)
        try:
            model.fit(X_train, y_train)

            # Text explanation
            st.subheader("📄 Model Explanation")
            explain_model(canon, model, X_train, y_train)

            # Visual explanation
            st.subheader("🖼 Visual Explanation")
            if canon in ("linear", "ridge"):
                plot_regression_line(model, X_train, y_train)
            elif canon in ("logistic", "svm"):
                if X_train.shape[1] == 2:
                    from eduML.metrics.visualize import plot_decision_boundary
                    plot_decision_boundary(model, X_train, y_train, title=f"{canon} Decision Boundary")
                    st.pyplot(plt)
                else:
                    st.info("Decision boundary only available for 2D features.")
            elif canon == "mlp" and hasattr(model, "visualize"):
                model.visualize()
            elif canon == "tree":
                st.text("Decision Tree Structure:")
                model.explain()
            elif canon == "pca":
                X_proj = model.fit(X_train).transform(X_train)
                plt.figure(figsize=(6,4))
                plt.scatter(X_proj[:,0], X_proj[:,1], c=y_train, cmap="viridis", edgecolor="k")
                plt.xlabel("PC1"); plt.ylabel("PC2"); plt.title("PCA Projection")
                st.pyplot(plt)
            else:
                st.info("No visualization available for this model.")

        except Exception as e:
            st.error(f"Explanation failed: {e}")

    # Save config
    save_config(model_name, dataset_name)

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    main()
