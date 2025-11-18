# src/mypackage/train.py

import numpy as np
#from model import LinearRegressionGD  # Local package import
from CHE1147_demo.model import LinearRegressionGD  # Local package import

def load_dummy_data():
    """Generate simple linear data with noise."""
    X = np.linspace(0, 10, 50).reshape(-1, 1)
    y = 3.5 * X.flatten() + 2 + np.random.randn(50) * 2
    return X, y

def main():
    # Load data
    X, y = load_dummy_data()

    # Initialize model
    model = LinearRegressionGD(learning_rate=0.01, n_iters=2000)

    # Train model
    model.fit(X, y)

    # Print learned parameters
    print("Learned weights:", model.weights)
    print("Learned bias:", model.bias)

    # Make some predictions
    preds = model.predict(X[:5])
    print("Predictions on first 5 samples:", preds)

if __name__ == "__main__":
    main()
