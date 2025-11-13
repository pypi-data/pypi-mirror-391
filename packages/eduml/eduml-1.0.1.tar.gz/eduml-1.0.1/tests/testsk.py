# ==============================
# 🔸 Linear Regression in Scikit-learn
# ==============================
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression

X, y = make_regression(n_samples=100, n_features=1, noise=20, random_state=42)
# Train sklearn model
sk_model = LinearRegression()
sk_model.fit(X, y)

# Predictions and evaluation
sk_pred = sk_model.predict([[6]])
print("\n🔸 Scikit-learn Results")
print("-----------------------")
print("Prediction for x=6:", sk_pred)
print("R² Score:", sk_model.score(X, y))

# Visualization
plt.scatter(X, y, color="blue", label="Actual Data")
plt.plot(X, sk_model.predict(X), color="red", label="Predicted Line")
plt.title("Scikit-learn Linear Regression")
plt.xlabel("X")
plt.ylabel("y")
plt.legend()
plt.show()
