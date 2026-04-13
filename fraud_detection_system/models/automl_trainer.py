"""
AutoML training pipeline using PyCaret.

Compares 8 classification algorithms, selects the best by F1 score,
tunes hyperparameters, and persists the final model + comparison metrics.
"""

import json
import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pycaret.classification import (
    setup, compare_models, save_model, pull, tune_model, finalize_model,
)
from config import MODEL_SAVE_PATH


def train_model():
    """Train, compare, and tune models. Returns a dict of best-model metrics."""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data/creditcard_sample.csv",
    )
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    print("Loading dataset for training...")
    df = pd.read_csv(data_path)

    print("Initializing PyCaret Setup...")
    setup(
        data=df,
        target="Class",
        normalize=True,
        fix_imbalance=True,
        session_id=42,
        verbose=False,
        html=False,
    )

    print("Comparing models (this may take a moment)...")
    best_model = compare_models(
        include=["rf", "et", "gbc", "lr", "dt", "knn", "nb", "ada"],
        n_select=1,
        sort="F1",
        verbose=False,
    )
    print(f"Best model selected: {best_model}")

    print("Tuning model...")
    tuned_model = tune_model(best_model, optimize="F1", verbose=False)

    # Save comparison results
    results_df = pull()
    results_dict = results_df.to_dict(orient="records")
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/model_comparison.json")
    with open(json_path, "w") as f:
        json.dump(str(results_dict), f)

    best_metrics = results_df.iloc[0].to_dict()

    print(f"Saving model to {MODEL_SAVE_PATH}...")
    save_model(tuned_model, MODEL_SAVE_PATH)

    return {
        "model_name": str(tuned_model),
        "f1": best_metrics.get("F1", 0),
        "auc": best_metrics.get("AUC", 0),
        "precision": best_metrics.get("Prec.", 0),
        "recall": best_metrics.get("Recall", 0),
        "accuracy": best_metrics.get("Accuracy", 0),
    }


if __name__ == "__main__":
    metrics = train_model()
    print("Training complete:", metrics)
