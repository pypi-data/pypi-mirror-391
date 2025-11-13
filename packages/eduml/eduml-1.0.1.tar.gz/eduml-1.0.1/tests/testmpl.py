from sklearn.datasets import load_iris
from eduML.supervised.neural_network import MLP
import numpy as np

X, y = load_iris(return_X_y=True)
mlp = MLP(
        input_dim=X.shape[1],hidden_dim=16,output_dim=len(np.unique(y)),lr=0.05,epochs=300, batch_size=16,early_stop=True,learning_mode=True,
    )
mlp.fit(X, y)
print("Final Accuracy:", mlp.accuracy(X, y))
mlp.visualize_loss()
mlp.explain()