"""
Real-time fraud detection engine.

Loads the trained PyCaret model and scores incoming transactions,
returning fraud probability, prediction label, and risk level.
"""

import time
import pandas as pd  # type: ignore[attr-defined]
from pycaret.classification import load_model, predict_model  # type: ignore[attr-defined]
from config import MODEL_SAVE_PATH, HIGH_RISK_THRESHOLD  # type: ignore[attr-defined,no-redef]


class FraudDetector:
    """Loads a trained PyCaret model and predicts fraud on transaction dicts."""

    def __init__(self):
        self.model = None

    def load(self):
        """Load the saved PyCaret model from disk."""
        print(f"Loading model from {MODEL_SAVE_PATH}...")
        try:
            self.model = load_model(MODEL_SAVE_PATH)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def predict(self, transaction_dict: dict) -> dict:
        """
        Score a single transaction and return enriched result dict.

        Adds: fraud_probability, prediction, risk_level, processing_time_ms.
        """
        start_time = time.time()

        df = pd.DataFrame([transaction_dict])

        # Align column names to match training schema
        if "amount" in df.columns and "Amount" not in df.columns:
            df["Amount"] = df["amount"]
        if "Time" not in df.columns:
            df["Time"] = 0.0

        # Drop non-feature columns that weren't in training data
        extra_cols = ["transaction_id", "timestamp", "amount", "merchant_category", "location"]
        df_model = df.drop(columns=[c for c in extra_cols if c in df.columns], errors="ignore")

        predictions = predict_model(self.model, data=df_model, verbose=False)

        pred_label = predictions["prediction_label"].iloc[0]
        pred_score = predictions["prediction_score"].iloc[0]
        processing_time_ms = round((time.time() - start_time) * 1000, 2)  # type: ignore[arg-type]

        # Convert PyCaret score to fraud probability
        fraud_prob = pred_score if pred_label == 1 else (1 - pred_score)

        if fraud_prob > HIGH_RISK_THRESHOLD:
            risk_level = "HIGH"
        elif fraud_prob > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        result = transaction_dict.copy()
        result["fraud_probability"] = round(fraud_prob, 4)
        result["prediction"] = int(pred_label)
        result["risk_level"] = risk_level
        result["processing_time_ms"] = processing_time_ms
        result["model_used"] = "AutoML"
        return result
