# model_builder.py
"""
Model Builder for eduML
-----------------------

Central factory to return model instances
based on canonical names.
"""

from eduML.supervised.linear_regression import LinearRegression
from eduML.supervised.ridge_regression import RidgeRegression
from eduML.supervised.logistic_regression import LogisticRegression
from eduML.supervised.svm import LinearSVM
from eduML.supervised.decision_tree import DecisionTree
from eduML.supervised.neural_network import MLP
from eduML.supervised.lda import LDA
from eduML.unsupervised.pca import PCA


def get_model(canonical_name: str, input_dim=None):
    """
    Create and return a model instance.
    """

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
        return MLP(
            input_dim=input_dim,
            hidden_dim=8,
            output_dim=1,
            lr=0.01,
            epochs=1000
        )

    raise ValueError(f"Unknown model key '{canonical_name}'")
