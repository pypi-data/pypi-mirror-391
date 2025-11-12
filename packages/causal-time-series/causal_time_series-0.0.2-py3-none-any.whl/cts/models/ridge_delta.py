from __future__ import annotations
import numpy as np

try:
    from sklearn.linear_model import Ridge
except ImportError:
    raise ImportError("scikit-learn must be installed to use RidgeDelta.")

class RidgeDelta:
    """Baseline model: Ridge regression on ΔX."""
    def __init__(self, alpha: float = 1.0):
        self.model = Ridge(alpha=alpha)

    def fit(self, X: np.ndarray, dy: np.ndarray):
        self.model.fit(X, dy.ravel())
        return self

    def predict_delta(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X).reshape(-1, 1)