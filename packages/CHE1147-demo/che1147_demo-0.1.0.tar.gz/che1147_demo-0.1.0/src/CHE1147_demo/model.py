# src/mypackage/model.py

import numpy as np

class LinearRegressionGD:
    """A simple Linear Regression model trained with Gradient Descent."""

    def __init__(self, learning_rate=0.01, n_iters=1000):
        self.learning_rate = learning_rate
        self.n_iters = n_iters
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        """
        Train the model using gradient descent.

        X: shape (n_samples, n_features)
        y: shape (n_samples,)
        """
        n_samples, n_features = X.shape

        # initialize parameters
        self.weights = np.zeros(n_features)
        self.bias = 0.0

        # gradient descent loop
        for _ in range(self.n_iters):
            y_pred = np.dot(X, self.weights) + self.bias

            # compute gradients
            dw = (1 / n_samples) * np.dot(X.T, (y_pred - y))
            db = (1 / n_samples) * np.sum(y_pred - y)

            # update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict(self, X):
        return np.dot(X, self.weights) + self.bias
