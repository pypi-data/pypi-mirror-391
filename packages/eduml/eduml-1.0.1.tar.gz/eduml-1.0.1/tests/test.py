import eduML.supervised.linear_regression as lr 
import numpy as np 
from sklearn.datasets import make_regression  
import eduML.explainers.explain_utils as ex

X, y = make_regression(
        n_samples=100,
        n_features=1,  
        noise=20,      
        random_state=42 
)  

model = lr.LinearRegression(lr=0.005, epochs=10000, early_stopping=True)
model.fit(X, y, verbose=False)
pred = model.predict([[6]])  

print("Prediction for x=6:", pred)
print("R² Score:", model.score(X, y))
print("Training Loss (last):", model.losses[-1])
model.plot_loss()
model.plot_prediction(X, y)

ex.explain_linear_model(model)
