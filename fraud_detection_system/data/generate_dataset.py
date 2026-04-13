"""
Synthetic dataset generator for FraudShield AI.

Creates a balanced credit-card-style dataset with 29 features (V1–V28 + Amount),
applies SMOTE oversampling, and exports to CSV for model training.
"""

import os
import numpy as np  # type: ignore[attr-defined]
import pandas as pd  # type: ignore[attr-defined]
from sklearn.datasets import make_classification  # type: ignore[attr-defined]
from imblearn.over_sampling import SMOTE  # type: ignore[attr-defined]


def generate_data():
    """Generate a SMOTE-balanced synthetic fraud dataset and save to CSV."""
    print("Generating synthetic dataset...")

    # Create 10K samples with 29 features (V1-V28 + Amount), 1% fraud rate
    X, y = make_classification(
        n_samples=10000,
        n_features=29,
        n_informative=24,
        n_redundant=5,
        n_classes=2,
        weights=[0.99, 0.01],
        class_sep=0.8,
        random_state=42,
    )

    cols = [f"V{i}" for i in range(1, 29)] + ["Amount"]
    df = pd.DataFrame(X, columns=cols)
    df["Class"] = y

    # Make Amount values financially realistic
    n_fraud = df[df["Class"] == 1].shape[0]
    n_legit = df[df["Class"] == 0].shape[0]
    df.loc[df["Class"] == 1, "Amount"] = np.random.uniform(100, 5000, n_fraud)
    df.loc[df["Class"] == 0, "Amount"] = np.random.exponential(100, n_legit)

    # Add Time column (0–172800s = 2 days) and sort chronologically
    df["Time"] = np.random.uniform(0, 172800, len(df))
    df = df.sort_values("Time").reset_index(drop=True)

    print(f"Original shape: {df.shape}")
    print(f"Original distribution:\n{df['Class'].value_counts()}")

    # Apply SMOTE to balance fraud vs. legit
    X_res, y_res = SMOTE(random_state=42).fit_resample(
        df.drop("Class", axis=1), df["Class"]
    )

    df_balanced = pd.concat(
        [pd.DataFrame(X_res, columns=cols + ["Time"]).reset_index(drop=True),
         pd.Series(y_res, name="Class").reset_index(drop=True)],
        axis=1,
    )

    print(f"Balanced shape: {df_balanced.shape}")
    print(f"Balanced distribution:\n{df_balanced['Class'].value_counts()}")

    output_path = os.path.join(os.path.dirname(__file__), "creditcard_sample.csv")
    df_balanced.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path}")


if __name__ == "__main__":
    generate_data()
