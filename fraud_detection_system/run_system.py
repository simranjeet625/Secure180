"""
FraudShield AI — Main Entry Point.

Orchestrates the full system lifecycle:
  1. Generate synthetic dataset (if missing)
  2. Train AutoML model (if missing)
  3. Initialize SQLite database
  4. Launch FastAPI server with WebSocket streaming
"""

import os
import sys
import uvicorn  # type: ignore[attr-defined]
from colorama import init, Fore, Style  # type: ignore[attr-defined]

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import MODEL_SAVE_PATH, DATABASE_PATH  # type: ignore[attr-defined,no-redef]

init(autoreset=True)


def print_banner():
    """Display the startup banner."""
    banner = f"""
{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FRAUDSHIELD AI — REAL-TIME FRAUD DETECTION
  Developer: Ankit and Simranjeet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
"""
    print(banner)


def main():
    """Run the complete FraudShield AI pipeline."""
    print_banner()

    # Step 1 — Initialize Database
    print(f"{Fore.BLUE}🗄️  Initializing database...{Style.RESET_ALL}")
    from database.db_handler import init_db  # type: ignore[attr-defined,no-redef]
    init_db()

    # Step 2 — Dataset Generation
    data_path = "data/creditcard_sample.csv"
    if not os.path.exists(data_path):
        print(f"{Fore.YELLOW}Dataset not found. Generating...{Style.RESET_ALL}")
        from data.generate_dataset import generate_data  # type: ignore[attr-defined,no-redef]
        generate_data()
    else:
        print(f"{Fore.GREEN}✅ Dataset ready: 50,000 transactions{Style.RESET_ALL}")

    # Step 3 — Train Model (PyCaret saves with .pkl extension)
    model_file = MODEL_SAVE_PATH + ".pkl"
    if not os.path.exists(model_file):
        print(f"{Fore.YELLOW}🤖 AutoML Training (this may take a few minutes)...{Style.RESET_ALL}")
        from models.automl_trainer import train_model  # type: ignore[attr-defined,no-redef]
        metrics = train_model()
        print(
            f"{Fore.GREEN}✅ Best Model: {metrics.get('model_name')} | "
            f"F1: {metrics.get('f1'):.3f} | AUC: {metrics.get('auc'):.3f}{Style.RESET_ALL}"
        )
        from database.db_handler import save_model_performance  # type: ignore[attr-defined,no-redef]
        save_model_performance(metrics)
    else:
        print(f"{Fore.GREEN}✅ Model already trained.{Style.RESET_ALL}")
        from database.db_handler import get_latest_model_info, save_model_performance  # type: ignore[attr-defined,no-redef]
        if not get_latest_model_info():
            import joblib  # type: ignore[attr-defined,no-redef]
            import re
            try:
                mdl = joblib.load(model_file)
                raw_name = type(mdl).__name__
                friendly = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', raw_name).replace('Classifier', '').strip()
                save_model_performance({
                    'model_name': friendly or raw_name,
                    'f1': None, 'auc': None,
                    'precision': None, 'recall': None, 'accuracy': None,
                })
                print(f"{Fore.GREEN}✅ Model info saved: {friendly}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Could not read model name: {e}{Style.RESET_ALL}")

    # Step 4 — Start Server
    print(f"{Fore.CYAN}🚀 Starting server...{Style.RESET_ALL}")
    print("""
  ┌─────────────────────────────────────┐
  │  🌐 Dashboard: http://localhost:8000 │
  │  📡 WebSocket: ws://localhost:8000/ws│
  │  📖 API Docs:  http://localhost:8000/docs│
  └─────────────────────────────────────┘
    """)
    print("  Transactions generating every 2 seconds...")
    print("  Press Ctrl+C to stop.")

    try:
        uvicorn.run("api.main_api:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
