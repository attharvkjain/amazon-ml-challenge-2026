"""
LightGBM binary classifier for entity matching.

Trains on candidate pair features + ground truth labels.
Uses scale_pos_weight for class imbalance (precision bias for F₀.₅).
"""
from __future__ import annotations

import numpy as np
import lightgbm as lgb
import pickle
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LGBM_PARAMS, OUTPUT_DIR


class EntityMatcher:
    """LightGBM-based entity matcher."""

    def __init__(self, params: dict | None = None):
        self.params = dict(LGBM_PARAMS)
        if params:
            self.params.update(params)
        self.model = None

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray | None = None,
        y_val: np.ndarray | None = None,
        feature_names: list[str] | None = None,
    ) -> None:
        """
        Train the LightGBM classifier.

        Auto-computes scale_pos_weight = n_neg / n_pos for precision bias.
        Uses early stopping on validation set if provided.
        """
        # Auto-compute scale_pos_weight
        n_pos = int(y_train.sum())
        n_neg = len(y_train) - n_pos
        if n_pos > 0:
            self.params['scale_pos_weight'] = n_neg / n_pos
        print(f"[matcher] Training LightGBM: {len(X_train):,} samples, "
              f"{n_pos:,} pos, {n_neg:,} neg, "
              f"scale_pos_weight={self.params['scale_pos_weight']:.2f}")

        callbacks = [lgb.log_evaluation(period=50)]

        # Set up model
        self.model = lgb.LGBMClassifier(**self.params)

        # Train with or without early stopping
        fit_params = {}
        if feature_names:
            fit_params['feature_name'] = feature_names

        if X_val is not None and y_val is not None:
            callbacks.append(lgb.early_stopping(stopping_rounds=30, verbose=True))
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                eval_metric='binary_logloss',
                callbacks=callbacks,
                **fit_params,
            )
        else:
            self.model.fit(
                X_train, y_train,
                callbacks=callbacks,
                **fit_params,
            )

        print(f"[matcher] Training complete. Best iteration: {self.model.best_iteration_}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return probability of positive class (match)."""
        assert self.model is not None, "Model not trained yet"
        return self.model.predict_proba(X)[:, 1]

    def feature_importance(self, feature_names: list[str] | None = None) -> dict[str, float]:
        """Return feature importance dict."""
        assert self.model is not None, "Model not trained yet"
        importances = self.model.feature_importances_
        if feature_names is not None:
            return dict(zip(feature_names, importances))
        return dict(enumerate(importances))

    def save(self, path: str | os.PathLike | None = None) -> None:
        """Save model to disk."""
        if path is None:
            path = OUTPUT_DIR / "model.pkl"
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"[matcher] Model saved to {path}")

    def load(self, path: str | os.PathLike | None = None) -> None:
        """Load model from disk."""
        if path is None:
            path = OUTPUT_DIR / "model.pkl"
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"[matcher] Model loaded from {path}")
