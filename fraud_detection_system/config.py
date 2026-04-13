"""
Global configuration for FraudShield AI.
Centralizes all tunable parameters: paths, thresholds, and server settings.
"""

DATABASE_PATH = "database/fraud_detection.db"
MODEL_SAVE_PATH = "models/saved_model/best_fraud_model"
FRAUD_THRESHOLD = 0.5
HIGH_RISK_THRESHOLD = 0.7
TRANSACTION_INTERVAL_SECONDS = 2
HOST = "0.0.0.0"
PORT = 8000
