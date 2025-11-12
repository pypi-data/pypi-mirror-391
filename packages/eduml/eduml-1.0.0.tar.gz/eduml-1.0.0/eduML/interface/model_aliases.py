# model_aliases.py
"""
Model Aliases for eduML
-----------------------

Maps user-friendly names to canonical model keys.
Used by CLI and Streamlit UI.
"""

MODEL_ALIASES = {
    # Linear regression
    "linear": "linear",
    "lin": "linear",
    "lr": "linear",

    # Ridge regression
    "ridge": "ridge",

    # Logistic regression
    "logistic": "logistic",
    "logreg": "logistic",
    "lg": "logistic",

    # SVM
    "svm": "svm",
    "linear_svm": "svm",

    # Decision tree
    "tree": "tree",
    "decision_tree": "tree",
    "dt": "tree",

    # MLP / Neural network
    "mlp": "mlp",
    "neural": "mlp",
    "neural_network": "mlp",

    # LDA
    "lda": "lda",

    # PCA
    "pca": "pca"
}


def canonical_model_name(name: str):
    """
    Return canonical model key from alias.
    """
    if not name:
        return None

    key = name.strip().lower()
    return MODEL_ALIASES.get(key, None)
