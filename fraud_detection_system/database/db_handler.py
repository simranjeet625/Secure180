"""
SQLite database handler for FraudShield AI.

Manages all CRUD operations for transactions and model performance metrics.
"""

import sqlite3
from datetime import datetime
from config import DATABASE_PATH  # type: ignore[attr-defined,no-redef]


def get_db_connection():
    """Open a connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the transactions and model_performance tables if they don't exist."""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            timestamp TEXT,
            amount REAL,
            merchant_category TEXT,
            location TEXT,
            fraud_probability REAL,
            prediction INTEGER,
            risk_level TEXT,
            processing_time_ms REAL,
            model_used TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS model_performance (
            model_name TEXT,
            auc REAL,
            f1 REAL,
            precision_score REAL,
            recall REAL,
            accuracy REAL,
            trained_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_transaction(data_dict: dict):
    """Insert a scored transaction record into the database."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (
            transaction_id, timestamp, amount, merchant_category, location,
            fraud_probability, prediction, risk_level, processing_time_ms, model_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data_dict.get("transaction_id"),
            data_dict.get("timestamp"),
            data_dict.get("amount"),
            data_dict.get("merchant_category"),
            data_dict.get("location"),
            data_dict.get("fraud_probability"),
            data_dict.get("prediction"),
            data_dict.get("risk_level"),
            data_dict.get("processing_time_ms"),
            data_dict.get("model_used"),
        ),
    )
    conn.commit()
    conn.close()


def get_recent_transactions(limit: int = 100) -> list[dict]:
    """Return the most recent transactions, newest first."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_fraud_transactions(limit: int = 50) -> list[dict]:
    """Return the most recent fraud-flagged transactions."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE prediction = 1 ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_fraud_stats() -> dict:
    """Aggregate fraud statistics across all stored transactions."""
    conn = get_db_connection()
    c = conn.cursor()

    total = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    fraud_count = c.execute("SELECT COUNT(*) FROM transactions WHERE prediction = 1").fetchone()[0]
    legit_count = c.execute("SELECT COUNT(*) FROM transactions WHERE prediction = 0").fetchone()[0]
    total_amount = c.execute("SELECT SUM(amount) FROM transactions").fetchone()[0] or 0.0
    amount_saved = c.execute("SELECT SUM(amount) FROM transactions WHERE prediction = 1").fetchone()[0] or 0.0
    avg_proc_time = c.execute("SELECT AVG(processing_time_ms) FROM transactions").fetchone()[0] or 0.0

    conn.close()
    return {
        "total_transactions": total,
        "total_fraud": fraud_count,
        "total_legit": legit_count,
        "fraud_rate": (fraud_count / total * 100) if total > 0 else 0.0,
        "total_amount_processed": total_amount,
        "amount_saved": amount_saved,
        "avg_processing_time": avg_proc_time,
    }


def get_hourly_stats() -> list[dict]:
    """Return fraud and legit counts grouped by hour of day."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT substr(timestamp, 12, 2) AS hour,
               SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) AS fraud_count,
               SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) AS legit_count
        FROM transactions
        GROUP BY hour
        ORDER BY hour
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_category_stats() -> list[dict]:
    """Return fraud counts and rates grouped by merchant category."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT merchant_category AS category,
               SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) AS fraud_count,
               COUNT(*) AS total
        FROM transactions
        GROUP BY category
    """).fetchall()
    conn.close()

    result = []
    for row in rows:
        d = dict(row)
        d["fraud_rate"] = (d["fraud_count"] / d["total"] * 100) if d["total"] > 0 else 0.0
        result.append(d)
    return result


def save_model_performance(metrics: dict):
    """Persist model training metrics to the database."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO model_performance (model_name, auc, f1, precision_score, recall, accuracy, trained_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            metrics.get("model_name"),
            metrics.get("auc"),
            metrics.get("f1"),
            metrics.get("precision"),
            metrics.get("recall"),
            metrics.get("accuracy"),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_latest_model_info() -> dict:
    """Return the most recently saved model performance record."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM model_performance ORDER BY rowid DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else {}
