"""
Power BI Real-time Pusher for FraudShield AI

This module sends transaction data to Power BI streaming dataset
using the Push URL (no OAuth required - uses embedded key).
"""

import json
import requests
import logging
from typing import Dict, Any, Optional

from .config import POWER_BI_ENABLED, POWER_BI_PUSH_URL

logger = logging.getLogger(__name__)


def push_to_power_bi(transaction: Dict[str, Any]) -> bool:
    """
    Push a single transaction to Power BI streaming dataset.
    
    Args:
        transaction: Transaction data dictionary
        
    Returns:
        True if successful, False otherwise
    """
    if not POWER_BI_ENABLED:
        return False
    
    if not POWER_BI_PUSH_URL:
        logger.warning("Power BI Push URL not configured")
        return False
    
    try:
        # Power BI expects an array of rows
        rows = [{
            "transaction_id": str(transaction.get("transaction_id", "")),
            "timestamp": transaction.get("timestamp", ""),
            "amount": float(transaction.get("amount", 0)),
            "merchant_category": str(transaction.get("merchant_category", "")),
            "location": str(transaction.get("location", "")),
            "fraud_probability": float(transaction.get("fraud_probability", 0)),
            "prediction": int(transaction.get("prediction", 0)),
            "risk_level": str(transaction.get("risk_level", "UNKNOWN")),
            "processing_time_ms": float(transaction.get("processing_time_ms", 0)),
            "model_used": str(transaction.get("model_used", "unknown")),
        }]
        
        # Send to Power BI Push API
        response = requests.post(
            POWER_BI_PUSH_URL,
            json=rows,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            logger.debug(f"Pushed transaction {transaction.get('transaction_id')} to Power BI")
            return True
        else:
            logger.warning(f"Power BI push failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error pushing to Power BI: {e}")
        return False


def test_connection() -> bool:
    """
    Test the Power BI connection by pushing a test record.
    
    Returns:
        True if connection works, False otherwise
    """
    test_transaction = {
        "transaction_id": "TEST-001",
        "timestamp": "2024-01-01T00:00:00",
        "amount": 100.0,
        "merchant_category": "test",
        "location": "test",
        "fraud_probability": 0.5,
        "prediction": 0,
        "risk_level": "LOW",
        "processing_time_ms": 10.0,
        "model_used": "test",
    }
    
    return push_to_power_bi(test_transaction)
