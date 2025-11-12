#!/usr/bin/env python3
"""
Enhanced eduML CLI (Task-aware)
-------------------------------

- Detects classification vs regression datasets.
- Chooses suitable metrics automatically.
- Handles PCA/other transform-only models correctly.
- Builds MLP with correct output_dim for classification.
- When a regression model is used on classification data, provides a
  safe (warned) mapping from continuous predictions -> nearest class label.
"""

import argparse
import sys
import json
import os
import traceback
import numpy as np
from colorama import Fore, Style, init
init(autoreset=True)

# Enable argcomplete if installed
try:
    import argcomplete
except Exception:
    argcomplete = None

# eduML imports
from eduML.core.dataset_loader import load_iris_dataset, generate_linear_data
from eduML.core.preprocessing import preprocess_data, standardize, train_test_split
from eduML.supervised.linear_regression import LinearRegression
from eduML.supervised.logistic_regression import LogisticRegression
from eduML.supervised.svm import LinearSVM
from eduML.supervised.decision_tree import DecisionTree
from eduML.supervised.neural_network import MLP
from eduML.supervised.ridge_regression import RidgeRegression
from eduML.supervised.lda import LDA
from eduML.unsupervised.pca import PCA
from eduML.explainers.explain_utils import explain_model
# near other imports
from eduML.unsupervised.kmeans import KMeans     # <- add your KMeans implementation
from sklearn.metrics import silhouette_score     # used for unsupervised comparison (optional)


# ============================================================
# Config Storage (~/.eduml/config.json)
# ============================================================
CONFIG_PATH = os.path.expanduser("~/.eduml/config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(model, dataset):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"model": model, "dataset": dataset}, f, indent=4)
    except Exception:
        pass

# ============================================================
# ASCII Banner
# ============================================================
def banner():
    

    print(Fore.CYAN + Style.BRIGHT + r"""
                                ███████╗██████╗  ██╗   ██╗ ███╗   ███╗██╗     
                                ██╔════╝██╔══██  ██║   ██║ ████╗ ████║██║     
                                █████╗  ██   ██  ██║   ██║ ██╔████╔██║██║     
                                ██╔══╝  ██╔══██  ██║   ██║ ██║╚██╔╝██║██║     
                                ███████╗██████   ██║█████ ╔██║ ╚═╝ ██║███████╗
                                ╚══════╝╚═╝      ╚═════╝  ╚═╝     ╚═╝╚══════╝

                                                eduML
    """ + Style.RESET_ALL)


# ============================================================
# Model aliases -> canonical keys
# ============================================================
MODEL_ALIASES = {
    "linear": "linear",
    "lin": "linear",
    "ridge": "ridge",
    "logistic": "logistic",
    "logreg": "logistic",
    "svm": "svm",
    "linear_svm": "svm",
    "tree": "tree",
    "decision_tree": "tree",
    "dt": "tree",
    "mlp": "mlp",
    "neural": "mlp",
    "neural_network": "mlp",
    "pca": "pca",
    "lda": "lda",
    # optional extras
    "kmeans": "kmeans",
    "knn": "knn",
    "nb": "nb",
    "naive_bayes": "nb",
}

def canonical_model_name(name):
    if name is None:
        return None
    key = name.strip().lower()
    return MODEL_ALIASES.get(key, None)

# ============================================================
# Model factory (build after dataset known when needed)
# ============================================================
def get_model(canonical_name, input_dim=None, n_classes=None):
    if canonical_name is None:
        raise ValueError("Missing model name (could not canonicalize).")

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
            raise ValueError("MLP requires input_dim (number of features).")
        output_dim = int(n_classes) if n_classes is not None else 1
        return MLP(input_dim=input_dim, hidden_dim=8, output_dim=output_dim, lr=0.01, epochs=1000)
    if canonical_name == "kmeans":
        # default n_clusters: if classification dataset, use number of classes, else 3
        n_clusters = int(n_classes) if n_classes is not None else 3
        return KMeans(n_clusters=n_clusters, learning_mode=False)
    # add other unsupervised models here...
    raise ValueError(f"Unknown canonical model '{canonical_name}'")


# ============================================================
# Dataset loader (unified)
# ============================================================
def load_dataset_by_name(name):
    """
    Return X, y for the requested dataset name.
    Currently supports: 'iris', 'linear'
    """
    if name is None:
        raise ValueError("Dataset name is required.")
    n = name.strip().lower()
    if n in ("iris", "iris_dataset"):
        return load_iris_dataset()
    if n in ("linear", "synthetic", "regression"):
        return generate_linear_data()
    # add more loaders later (digits, salary, kmeans demo...)
    raise ValueError(f"Unknown dataset '{name}'. Available: iris, linear")

# ============================================================
# Helpers: train/split/preprocess + task detection
# ============================================================
def prepare_data_for_model(dataset_name, unsupervised=False):
    """
    Prepares data for supervised or unsupervised models.
    If unsupervised=True -> returns X_train, X_test, None, None, True
    Else returns X_train, X_test, y_train, y_test, False
    """
    X, y = load_dataset_by_name(dataset_name)

    # If user selected an unsupervised model but dataset loader returned y,
    # just ignore y for fitting but keep it for optional evaluation/visualization.
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # Standardize numeric features for X
    X_train_std, mean, std = standardize(X_train)
    X_test_std = (X_test - mean) / std

    if unsupervised:
        # Do not return labels as training target; keep them for optional visualization
        return X_train_std, X_test_std, None, None, True
    else:
        return X_train_std, X_test_std, y_train, y_test, False


def is_classification(y):
    """
    Decide whether the task is classification.
    Heuristic: if y contains integers and the number of unique labels is small (<= 20),
    treat as classification. Otherwise treat as regression.
    """
    y = np.asarray(y)
    unique = np.unique(y)
    # If non-numeric (strings), it's classification
    if y.dtype.type is np.str_ or y.dtype.type is np.object_:
        return True
    # If values are integers (close to int) and few unique labels => classification
    if np.allclose(unique, unique.astype(int)):
        if len(unique) <= 20:
            return True
    return False

def map_continuous_to_labels(preds, labels):
    """
    Map continuous predictions to nearest label in labels array.
    labels should be 1D array of unique class labels (numeric).
    Returns integer/label array.
    """
    labels = np.asarray(sorted(labels))
    preds = np.asarray(preds).ravel()
    mapped = []
    for p in preds:
        # find index with minimal absolute distance
        idx = np.argmin(np.abs(labels - p))
        mapped.append(labels[idx])
    return np.array(mapped)

# ============================================================
# CLI core commands (task-aware)
# ============================================================
def run_train(model_name, dataset):
    try:
        canon = canonical_model_name(model_name) or model_name
        if canon is None:
            print(Fore.RED + "❌ Unknown model name. Please provide a valid model (e.g. svm, linear, mlp).")
            return

        print(Fore.YELLOW + f"\n🚀 Training model: {canon} on dataset: {dataset}")

        # decide unsupervised models
        unsupervised_models = {"pca", "kmeans"}
        is_unsupervised = canon in unsupervised_models

        # prepare data accordingly
        X_train, X_test, y_train, y_test, _ = prepare_data_for_model(dataset, unsupervised=is_unsupervised)

        # determine task
        classification = False
        labels = None
        n_classes = None
        if not is_unsupervised and y_train is not None:
            classification = is_classification(y_train)
            labels = np.unique(y_train)
            n_classes = len(labels) if classification else None

        # Warn on mismatch (unchanged behavior)
        if canon in ("logistic", "svm", "tree", "mlp", "lda") and not classification and not is_unsupervised:
            print(Fore.YELLOW + f"⚠️ Selected classification model ({canon}) but dataset appears regression.")
        if canon in ("linear", "ridge") and classification:
            print(Fore.YELLOW + f"⚠️ Selected regression model ({canon}) for classification dataset. Predictions will be continuous and may be mapped when evaluating.")

        # create model
        model = get_model(canon, input_dim=(X_train.shape[1] if X_train is not None else None), n_classes=n_classes)

        print(Fore.CYAN + "📚 Fitting model...")

        # handle fitting per type
        if canon == "pca" or canon == "kmeans":
            # unsupervised: fit on X only
            model.fit(X_train)
        elif canon == "lda":
            # LDA is classification-only
            if not classification:
                print(Fore.RED + "❌ LDA requires classification labels. Aborting.")
                return
            model.fit(X_train, y_train)
        else:
            # supervised
            try:
                model.fit(X_train, y_train)
            except TypeError:
                # fallback if model.fit expects only X
                model.fit(X_train)

        # Post-fit evaluation / messages
        if canon == "kmeans":
            print(Fore.CYAN + "✅ KMeans fitted.")
            try:
                inertia = getattr(model, "inertia_", None)
                if inertia is not None:
                    print(Fore.CYAN + f"   Inertia (within-cluster variance): {inertia:.4f}")
                # if true labels exist, compute simple purity or silhouette
                if y_test is not None:
                    try:
                        labels_pred = model.predict(X_test)
                        # silhouette requires >1 cluster and >1 sample per cluster
                        if len(np.unique(labels_pred)) > 1 and len(X_test) > len(np.unique(labels_pred)):
                            sil = silhouette_score(X_test, labels_pred)
                            print(Fore.CYAN + f"   Silhouette Score: {sil:.4f}")
                    except Exception:
                        pass
            except Exception:
                pass

            print(Fore.BLUE + "✅ KMeans Training complete!\n")
            save_config(model_name, dataset)
            return

        if canon == "pca":
            print(Fore.CYAN + "✅ PCA fitted. Showing summary:")
            explain_model("pca", model, X_train, y_train)
            save_config(model_name, dataset)
            return

        # standard supervised predict/evaluate
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            print(Fore.YELLOW + f"⚠️ Prediction unavailable for this model: {e}")
            save_config(model_name, dataset)
            return

        # handle regression-on-classification mapping
        if not is_unsupervised and classification:
            if canon in ("linear", "ridge"):
                print(Fore.YELLOW + "⚠️ Mapping continuous regression predictions to nearest class labels.")
                y_pred = map_continuous_to_labels(y_pred, labels)
            try:
                acc = (y_pred == y_test).mean() * 100
                print(Fore.GREEN + f"✅ Accuracy: {acc:.2f}%")
            except Exception:
                print(Fore.GREEN + "✅ Predictions generated (accuracy unavailable).")
        else:
            # regression metrics
            from sklearn.metrics import mean_squared_error
            try:
                rmse = mean_squared_error(y_test, y_pred, squared=False)
                print(Fore.GREEN + f"✅ RMSE: {rmse:.4f}")
            except Exception:
                print(Fore.GREEN + "✅ Predictions generated (RMSE unavailable).")

        save_config(model_name, dataset)
        print(Fore.BLUE + "✅ Training complete!\n")

    except Exception as e:
        print(Fore.RED + "❌ Error during training:")
        print(Fore.RED + str(e))
        traceback.print_exc()

def run_compare(model_name, dataset):
    try:
        canon = canonical_model_name(model_name) or model_name
        if canon is None:
            print(Fore.RED + "❌ Unknown model name.")
            return

        print(Fore.MAGENTA + f"\n⚖️ Comparing {canon} vs Scikit-learn on {dataset}")

        # sklearn mapping
        from sklearn import (
            linear_model, svm, tree, neural_network, decomposition, discriminant_analysis, cluster
        )
        from sklearn.metrics import silhouette_score

        skl_map = {
            "linear": linear_model.LinearRegression(),
            "ridge": linear_model.Ridge(),
            "logistic": linear_model.LogisticRegression(max_iter=1000),
            "svm": svm.SVC(),
            "tree": tree.DecisionTreeClassifier(),
            "mlp": neural_network.MLPClassifier(hidden_layer_sizes=(8,), max_iter=500),
            "pca": decomposition.PCA(n_components=2),
            "lda": discriminant_analysis.LinearDiscriminantAnalysis(),
            "kmeans": cluster.KMeans(n_clusters=3, random_state=0),
        }

        # Determine if unsupervised
        unsupervised_models = {"pca", "kmeans"}
        is_unsupervised = canon in unsupervised_models

        # Prepare data (unsupervised flag)
        X_train, X_test, y_train, y_test, _ = prepare_data_for_model(dataset, unsupervised=is_unsupervised)
        input_dim = X_train.shape[1]
        classification = False
        n_classes = None
        if y_train is not None:
            classification = is_classification(y_train)
            n_classes = len(np.unique(y_train))

        # Special: PCA compare by explained variance
        if canon == "pca":
            edu_model = get_model("pca")
            edu_model.fit(X_train)
            edu_var = float(np.sum(getattr(edu_model, "explained_variance_ratio_", 0)))

            skl = skl_map["pca"]
            skl.fit(X_train)
            skl_var = float(np.sum(getattr(skl, "explained_variance_ratio_", 0)))

            print(Fore.CYAN + f"\neduML Explained Variance : {edu_var * 100:.2f}%")
            print(Fore.CYAN + f"Sklearn Explained Var.   : {skl_var * 100:.2f}%\n")
            save_config(model_name, dataset)
            return

        # Special: KMeans compare by inertia / silhouette
        if canon == "kmeans":
            # choose n_clusters from dataset if classification
            n_clusters = n_classes if (classification and n_classes is not None and n_classes > 1) else 3
            edu_model = KMeans(n_clusters=n_clusters)
            edu_model.fit(X_train)
            edu_inertia = getattr(edu_model, "inertia_", None)

            skl = skl_map.get("kmeans")
            skl.set_params(n_clusters=n_clusters)
            skl.fit(X_train)
            skl_inertia = getattr(skl, "inertia_", None)

            print(Fore.CYAN + f"\neduML Inertia : {edu_inertia:.4f}" if edu_inertia is not None else "eduML Inertia: N/A")
            print(Fore.CYAN + f"Sklearn Inertia: {skl_inertia:.4f}" if skl_inertia is not None else "Sklearn Inertia: N/A")

            # optional silhouette if labels available
            try:
                edu_labels = edu_model.predict(X_test)
                skl_labels = skl.predict(X_test)
                if len(np.unique(edu_labels)) > 1:
                    edu_sil = silhouette_score(X_test, edu_labels)
                    print(Fore.CYAN + f"eduML Silhouette: {edu_sil:.4f}")
                if len(np.unique(skl_labels)) > 1:
                    skl_sil = silhouette_score(X_test, skl_labels)
                    print(Fore.CYAN + f"Sklearn Silhouette: {skl_sil:.4f}")
            except Exception:
                pass

            save_config(model_name, dataset)
            return

        # Normal supervised comparison (unchanged)
        model = get_model(canon, input_dim=input_dim, n_classes=n_classes)
        model.fit(X_train, y_train)
        try:
            edu_pred = model.predict(X_test)
        except Exception:
            edu_pred = None

        skl = skl_map.get(canon)
        skl_display = "(no sklearn baseline)"
        if skl is not None:
            try:
                skl.fit(X_train, y_train)
                skl_pred = skl.predict(X_test) if hasattr(skl, "predict") else None
                if skl_pred is not None:
                    if classification:
                        skl_metric = (skl_pred == y_test).mean()
                        skl_display = f"{skl_metric * 100:.2f}%"
                    else:
                        from sklearn.metrics import mean_squared_error
                        skl_rmse = mean_squared_error(y_test, skl_pred, squared=False)
                        skl_display = f"RMSE = {skl_rmse:.4f}"
            except Exception:
                skl_display = "(sklearn baseline failed)"

        if edu_pred is not None:
            if classification:
                edu_metric = (edu_pred == y_test).mean()
                edu_display = f"{edu_metric * 100:.2f}%"
            else:
                from sklearn.metrics import mean_squared_error
                edu_rmse = mean_squared_error(y_test, edu_pred, squared=False)
                edu_display = f"RMSE = {edu_rmse:.4f}"
        else:
            edu_display = "(no prediction available)"

        print(Fore.CYAN + f"\neduML result     : {edu_display}")
        print(Fore.CYAN + f"Scikit-learn     : {skl_display}\n")

        save_config(model_name, dataset)

    except Exception as e:
        print(Fore.RED + "❌ Error during comparison:")
        print(Fore.RED + str(e))
        traceback.print_exc()
def run_explain(model_name, dataset):
    try:
        canon = canonical_model_name(model_name) or model_name
        if canon is None:
            print(Fore.RED + "❌ Unknown model name.")
            return

        print(Fore.BLUE + f"\n🔍 Explaining model: {canon} on dataset: {dataset}")

        # Determine if unsupervised -> for fitting we only need X
        unsupervised_models = {"pca", "kmeans"}
        is_unsupervised = canon in unsupervised_models

        X_train, X_test, y_train, y_test, _ = prepare_data_for_model(dataset, unsupervised=is_unsupervised)
        input_dim = X_train.shape[1]
        classification = False
        n_classes = None
        if y_train is not None:
            classification = is_classification(y_train)
            n_classes = len(np.unique(y_train))

        model = get_model(canon, input_dim=input_dim, n_classes=n_classes)

        print(Fore.YELLOW + "📌 Training model for explanation...\n")
        if canon in ("pca", "kmeans"):
            model.fit(X_train)
        elif canon == "lda":
            if not classification:
                print(Fore.RED + "❌ LDA requires classification labels; cannot explain.")
                return
            model.fit(X_train, y_train)
        else:
            model.fit(X_train, y_train)

        print(Fore.GREEN + "✅ Model trained successfully.\n")
        print(Fore.CYAN + "📘 Generating explanation...\n")

        # explain_model prints descriptions (text) — call first
        explain_model(canon, model, X_train, y_train)

        # Visual help for unsupervised
        if canon == "kmeans":
            print(Fore.CYAN + "📊 KMeans visual (2D only):")
            if X_train.shape[1] == 2:
                model.visualize(X_train, show_history=True)
            else:
                print("   (decision: projection required; use PCA to reduce to 2D first)")
        elif canon == "pca":
            print(Fore.CYAN + "📊 PCA 2D projection (first two components):")
            try:
                X_proj = model.transform(X_train)
                if X_proj.shape[1] >= 2:
                    # simple ascii info or plotting if environment supports
                    print("   First two component variance ratio:", getattr(model, "explained_variance_ratio_", None))
                else:
                    print("   PCA reduced to 1D.")
            except Exception:
                pass

        save_config(model_name, dataset)
        print(Fore.GREEN + "\n✅ Explanation completed!\n")

    except Exception as e:
        print(Fore.RED + "\n❌ Error during explanation:")
        print(Fore.RED + str(e))
        traceback.print_exc()


# ============================================================
# Interactive Menu
# ============================================================
def interactive_menu():
    #banner()
    cfg = load_config()
    last_model = cfg.get("model", "svm")
    last_dataset = cfg.get("dataset", "iris")

    print(Fore.GREEN + "✅ Interactive Mode Enabled")
    print(Fore.WHITE + f"Last used → Model: {last_model}, Dataset: {last_dataset}\n")

    print(Fore.CYAN + "1) Train a model")
    print("2) Compare with Scikit-learn")
    print("3) Explain a model")
    print("4) Exit\n")

    choice = input("Enter choice (1–4): ").strip()
    if choice == "4":
        print(Fore.YELLOW + "\n👋 Exiting…")
        sys.exit(0)

    # Ask inputs with defaults
    model = input(f"Model [{last_model}]: ").strip() or last_model
    dataset = input(f"Dataset [{last_dataset}]: ").strip() or last_dataset

    if choice == "1":
        run_train(model, dataset)
    elif choice == "2":
        run_compare(model, dataset)
    elif choice == "3":
        run_explain(model, dataset)
    else:
        print(Fore.RED + "❌ Invalid selection!")

# ============================================================
# Main CLI Parser
# ============================================================
def main():
    banner()

    parser = argparse.ArgumentParser(description="eduML CLI")
    sub = parser.add_subparsers(dest="command")

    # train
    train = sub.add_parser("train")
    train.add_argument("--model", required=False)
    train.add_argument("--dataset", required=False)

    # compare
    compare = sub.add_parser("compare")
    compare.add_argument("--model", required=False)
    compare.add_argument("--dataset", required=False)

    # explain
    explain = sub.add_parser("explain")
    explain.add_argument("--model", required=False)
    explain.add_argument("--dataset", required=False)

    if argcomplete:
        argcomplete.autocomplete(parser)

    # No arguments → interactive mode
    if len(sys.argv) == 1:
        interactive_menu()
        return

    args = parser.parse_args()

    # Use provided args or fallback to config/defaults
    cfg = load_config()
    default_model = cfg.get("model", "svm")
    default_dataset = cfg.get("dataset", "iris")

    if args.command == "train":
        run_train(args.model or default_model, args.dataset or default_dataset)
    elif args.command == "compare":
        run_compare(args.model or default_model, args.dataset or default_dataset)
    elif args.command == "explain":
        run_explain(args.model or default_model, args.dataset or default_dataset)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
