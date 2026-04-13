"""
Synthetic transaction generator for real-time simulation.

Produces realistic credit-card transactions at configurable intervals,
with distinct statistical profiles for legitimate vs. fraudulent activity.
"""

import uuid
import random
import numpy as np  # type: ignore[attr-defined]
from datetime import datetime


class TransactionSimulator:
    """Generates synthetic credit-card transactions with a ~2% fraud rate."""

    CATEGORIES = [
        "grocery", "online", "travel", "gas",
        "restaurant", "electronics", "luxury", "pharmacy",
    ]
    LOCATIONS_NORMAL = [
        "New York/USA", "London/UK", "Toronto/Canada",
        "Sydney/Australia", "Berlin/Germany",
    ]
    LOCATIONS_FRAUD = [
        "Lagos/Nigeria", "Unknown/VPN",
        "Multiple/Locations", "Kiev/Ukraine",
    ]

    def __init__(self):
        self.transaction_count = 0

    def generate_transaction(self) -> dict:
        """Return a single transaction dict with V1–V28 features."""
        self.transaction_count += 1

        # ~2% fraud rate via deterministic + random blend
        is_fraud = (self.transaction_count % 50 == 0) or (random.random() < 0.02)

        if is_fraud:
            amount = random.uniform(800, 8000)
            location = random.choice(self.LOCATIONS_FRAUD)
            v_features = np.random.normal(loc=2.0, scale=4.0, size=28)
        else:
            amount = random.uniform(5, 300)
            location = random.choice(self.LOCATIONS_NORMAL)
            v_features = np.random.normal(loc=0.0, scale=1.0, size=28)

        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "amount": round(amount, 2),  # type: ignore[arg-type]
            "merchant_category": random.choice(self.CATEGORIES),
            "location": location,
        }

        for i, val in enumerate(v_features):
            transaction[f"V{i + 1}"] = val

        return transaction
