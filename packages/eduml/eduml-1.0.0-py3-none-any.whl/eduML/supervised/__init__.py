"""
eduML.supervised
----------------

Implements key supervised learning algorithms from scratch, including:
- Linear Regression, Ridge Regression
- Logistic Regression
- KNN, Naive Bayes, LDA
- SVM, Decision Tree, and a simple Neural Network (MLP)

All algorithms follow a consistent API: fit(), predict(), explain(), visualize().
"""

from .linear_regression import LinearRegression
from .ridge_regression import RidgeRegression
from .logistic_regression import LogisticRegression
from .knn import KNN
from .naive_bayes import GaussianNB
from .lda import LDA
from .svm import LinearSVM
from .decision_tree import DecisionTree
from .neural_network import MLP

__all__ = [
    "LinearRegression",
    "RidgeRegression",
    "LogisticRegression",
    "KNN",
    "GaussianNB",
    "LDA",
    "LinearSVM",
    "DecisionTree",
    "MLP"
]
