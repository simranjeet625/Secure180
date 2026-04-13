"""
Terminal alert system for FraudShield AI.

Provides color-coded console output and persistent fraud logging
for real-time transaction monitoring.
"""

import os
from datetime import datetime
from colorama import Fore, Style, init  # type: ignore[attr-defined]

init(autoreset=True)


class AlertSystem:
    """Logs transactions to the terminal with severity-based coloring and writes fraud alerts to file."""

    def __init__(self):
        self.log_file = "alerts/fraud_alerts.log"
        os.makedirs("alerts", exist_ok=True)

    def log_transaction(self, result: dict):
        """Print a color-coded transaction summary and log fraud to file."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        amount = result["amount"]
        loc = result["location"]
        prob = result["fraud_probability"] * 100
        pred = result["prediction"]
        risk = result["risk_level"]

        if pred == 1:
            icon, color, status = "🚨", Fore.RED + Style.BRIGHT, "FRAUD DETECTED"
            log_msg = f"[{timestamp}] {icon} {status} | ${amount} | {loc} | Risk: {prob:.1f}%"
            print(color + log_msg)
            with open(self.log_file, "a") as f:
                f.write(log_msg + "\n")

        elif risk == "MEDIUM":
            icon, color, status = "🟡", Fore.YELLOW, "SUSPICIOUS"
            print(color + f"[{timestamp}] {icon} {status} | ${amount} | {loc} | Risk: {prob:.1f}%")

        else:
            icon, color, status = "✅", Fore.CYAN, "LEGITIMATE"
            print(color + f"[{timestamp}] {icon} {status} | ${amount} | {loc} | Risk: {prob:.1f}%")


alert_system = AlertSystem()
