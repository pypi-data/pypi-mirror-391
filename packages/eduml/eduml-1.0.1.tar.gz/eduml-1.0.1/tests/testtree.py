import numpy as np
import eduML.supervised.decision_tree as dt
X = np.array([
        [2, 3], [1, 2], [3, 6], [4, 5], [6, 8],
        [5, 2], [7, 3], [8, 4], [9, 6], [10, 7],
        [3, 1], [4, 2], [5, 5], [6, 6], [7, 7],
        [8, 8], [9, 9], [10, 10], [1, 6], [2, 5]
    ])

    
y = np.array([
        0, 0, 1, 1, 1,
        0, 0, 1, 1, 1,
        0, 0, 1, 1, 1,
        1, 1, 1, 0, 0
    ])

model = dt.DecisionTree(max_depth=2, verbose=True)
model.fit(X, y)
print("Predictions:", model.predict([[3, 4], [1, 1]]))
print("\nTree Structure:")
model.explain()
model.visualize(X, y)
    
visualizer = dt.DecisionTreeVisualizer(model)
visualizer.visualize()