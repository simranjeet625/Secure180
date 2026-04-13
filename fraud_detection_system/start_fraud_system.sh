#!/bin/bash

# FraudShield AI — Startup Script
# This script activates the virtual environment and launches the system.

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "--------------------------------------------------"
echo "🚀 Initializing FraudShield AI..."
echo "--------------------------------------------------"

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found. Activating..."
    source .venv/bin/activate
else
    echo "❌ Error: .venv directory not found."
    echo "Please ensure you have set up the virtual environment."
    exit 1
fi

# Run the system
python3 run_system.py
