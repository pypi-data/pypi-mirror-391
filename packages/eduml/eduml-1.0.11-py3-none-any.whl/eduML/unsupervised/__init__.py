"""
eduML.unsupervised
------------------

Contains unsupervised learning algorithms for clustering
and dimensionality reduction.

Includes:
- K-Means Clustering
- Principal Component Analysis (PCA)
"""

from .kmeans import KMeans
from .pca import PCA

__all__ = ["KMeans", "PCA"]
