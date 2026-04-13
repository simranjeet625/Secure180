"""
FastAPI application — REST API + WebSocket server for FraudShield AI.

Serves the dashboard, exposes fraud statistics endpoints, and streams
live transaction data to connected clients via WebSocket.
"""

import asyncio
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # type: ignore[attr-defined]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[attr-defined]
from fastapi.responses import FileResponse  # type: ignore[attr-defined]

from realtime.transaction_simulator import TransactionSimulator  # type: ignore[attr-defined,no-redef]
from realtime.fraud_detector import FraudDetector  # type: ignore[attr-defined,no-redef]
from alerts.alert_system import alert_system  # type: ignore[attr-defined,no-redef]
from database.db_handler import (  # type: ignore[attr-defined,no-redef]
    insert_transaction, get_recent_transactions, get_fraud_transactions,
    get_fraud_stats, get_hourly_stats, get_category_stats,
    get_latest_model_info, init_db,
)
from config import TRANSACTION_INTERVAL_SECONDS  # type: ignore[attr-defined,no-redef]

# Power BI Real-time streaming
try:
    from power_bi.powerbi_pusher import push_to_power_bi
except ImportError:
    push_to_power_bi = None  # Fallback if Power BI not configured

app = FastAPI(title="FraudShield AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = TransactionSimulator()
detector = FraudDetector()


# ── WebSocket Connection Manager ──────────────────────────────────────────────

class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        json_msg = json.dumps(message)
        for conn in self.active_connections:
            try:
                await conn.send_text(json_msg)
            except Exception:
                pass


manager = ConnectionManager()


# ── Background Transaction Loop ──────────────────────────────────────────────

async def transaction_loop():
    """Generate, score, store, and broadcast transactions continuously."""
    while True:
        if detector.model is None:
            try:
                detector.load()
            except Exception:
                pass
            await asyncio.sleep(2)
            continue

        txn = simulator.generate_transaction()
        result = detector.predict(txn)
        insert_transaction(result)
        alert_system.log_transaction(result)

        # Push to Power BI for real-time dashboard
        if push_to_power_bi:
            try:
                push_to_power_bi(result)
            except Exception:
                pass  # Don't fail the main flow if Power BI fails

        await manager.broadcast({"type": "transaction", "data": result})

        # Broadcast stats every 5 transactions
        if simulator.transaction_count % 5 == 0:
            stats = _get_stats_internal()
            await manager.broadcast({"type": "stats_update", "data": stats})

        await asyncio.sleep(TRANSACTION_INTERVAL_SECONDS)


# ── Lifecycle Events ─────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    init_db()
    try:
        detector.load()
    except Exception:
        print("Model not found on startup, waiting for training...")
    asyncio.create_task(transaction_loop())


# ── Internal Helpers ─────────────────────────────────────────────────────────

def _get_stats_internal() -> dict:
    """Build a combined stats payload including model info."""
    stats = get_fraud_stats()
    model_info = get_latest_model_info()

    if not model_info and detector.model is not None:
        model_name = type(detector.model).__name__
        friendly = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', model_name).replace('Classifier', '').strip()
        model_info = {
            "model_name": friendly or model_name,
            "f1": None, "auc": None, "accuracy": None,
        }

    stats["model_info"] = model_info
    return stats


# ── REST Endpoints ───────────────────────────────────────────────────────────

@app.get("/")
async def get_dashboard():
    """Serve the main dashboard HTML."""
    return FileResponse(os.path.join(os.path.dirname(__file__), "dashboard", "index.html"))


@app.get("/dashboard")
async def get_dashboard_alias():
    """Alias for the dashboard."""
    return FileResponse(os.path.join(os.path.dirname(__file__), "dashboard", "index.html"))


@app.get("/health")
def health_check():
    """Return server and model status."""
    return {"status": "online", "model": "Loaded" if detector.model else "None"}


@app.get("/stats")
def stats_endpoint():
    """Return aggregated fraud statistics and model info."""
    return _get_stats_internal()


@app.get("/transactions")
def transactions_endpoint(limit: int = 100):
    """Return recent transactions, newest first."""
    return get_recent_transactions(limit)


@app.get("/transactions/fraud")
def fraud_transactions_endpoint(limit: int = 50):
    """Return recent fraud-flagged transactions."""
    return get_fraud_transactions(limit)


@app.get("/model-comparison")
def model_comparison_endpoint():
    """Return AutoML model comparison results from training."""
    json_path = "data/model_comparison.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            content = f.read()
            try:
                loaded = json.loads(content)
                if isinstance(loaded, str):
                    import ast
                    return ast.literal_eval(loaded)
                return loaded
            except Exception:
                return {}
    return {}


@app.get("/hourly-stats")
def hourly_stats_endpoint():
    """Return fraud/legit counts grouped by hour."""
    return get_hourly_stats()


@app.get("/category-stats")
def category_stats_endpoint():
    """Return fraud rates grouped by merchant category."""
    return get_category_stats()


# ── WebSocket Endpoint ───────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Stream live transaction data to connected clients."""
    await manager.connect(websocket)
    try:
        recent = get_recent_transactions(20)
        for txn in reversed(recent):
            await websocket.send_text(json.dumps({"type": "transaction", "data": txn}))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
