"""
Real-time Tableau Data Connector.
This creates a local web server that Tableau can connect to for live data.

Tableau Options for Live Connection:
1. Tableau Data Server (requires Tableau Server/Online)
2. Web Data Connector (JSON API) - what we're building
3. PostgreSQL/MySQL connector
4. ODBC connection

This script creates Option 2 - a JSON API that Tableau can refresh automatically.
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import sqlite3
import os

DATABASE_PATH = "database/fraud_detection.db"
API_PORT = 8899

class TableauDataHandler(BaseHTTPRequestHandler):
    """HTTP handler for Tableau data connection"""
    
    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Get data from database
            data = self.get_transaction_data()
            self.wfile.write(json.dumps(data).encode())
            
        elif self.path == '/summary':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = self.get_summary_data()
            self.wfile.write(json.dumps(data).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_transaction_data(self):
        """Fetch all transactions as JSON"""
        if not os.path.exists(DATABASE_PATH):
            return {"error": "Database not found"}
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, transaction_id, timestamp, amount, 
                   merchant_category, location, fraud_probability,
                   prediction, risk_level
            FROM transactions 
            ORDER BY id DESC
            LIMIT 10000
        """)
        
        rows = cursor.fetchall()
        data = []
        
        for row in rows:
            data.append({
                'id': row['id'],
                'transaction_id': row['transaction_id'],
                'timestamp': row['timestamp'],
                'amount': float(row['amount']),
                'merchant_category': row['merchant_category'],
                'location': row['location'],
                'fraud_probability': float(row['fraud_probability']),
                'prediction': row['prediction'],
                'risk_level': row['risk_level']
            })
        
        conn.close()
        return {"transactions": data, "count": len(data)}
    
    def get_summary_data(self):
        """Get KPI summary"""
        if not os.path.exists(DATABASE_PATH):
            return {"error": "Database not found"}
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount) as total_amount,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_count,
                SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk,
                SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END) as medium_risk,
                SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) as low_risk
            FROM transactions
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_transactions": row[0],
            "total_amount": float(row[1]) if row[1] else 0,
            "fraud_count": row[2],
            "high_risk": row[3],
            "medium_risk": row[4],
            "low_risk": row[5]
        }
    
    def log_message(self, format, *args):
        # Suppress HTTP logs
        pass


def start_api_server():
    """Start the API server in a separate thread"""
    server = HTTPServer(('localhost', API_PORT), TableauDataHandler)
    print(f"🌐 Tableau Data API running at: http://localhost:{API_PORT}/data")
    print(f"   Summary endpoint: http://localhost:{API_PORT}/summary")
    print(f"   Health check: http://localhost:{API_PORT}/health")
    print("\n📊 Tableau Web Data Connector Setup:")
    print(f"   1. In Tableau, go to: Connect → Web Data Connector")
    print(f"   2. Enter URL: http://localhost:{API_PORT}/data")
    print(f"   3. Click 'Get Data'")
    print(f"   4. Enable 'Refresh' for automatic updates")
    print("\n Press Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.shutdown()


def create_tableau_web_connector_html():
    """Create a Web Data Connector HTML file for Tableau"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>FraudShield AI - Tableau Connector</title>
    <style>
        body { 
            font-family: Arial; 
            padding: 40px; 
            background: #1a1a2e;
            color: white;
        }
        h1 { color: #e94560; }
        .status { 
            background: #16213e; 
            padding: 20px; 
            border-radius: 10px;
            margin: 20px 0;
        }
        .btn {
            background: #e94560;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .btn:hover { background: #d63447; }
        table { 
            border-collapse: collapse; 
            width: 100%;
            margin-top: 20px;
        }
        th, td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #333;
        }
        th { background: #16213e; }
        .high { color: #e74c3c; }
        .medium { color: #f39c12; }
        .low { color: #27ae60; }
    </style>
</head>
<body>
    <h1>🛡️ FraudShield AI - Tableau Web Connector</h1>
    
    <div class="status">
        <h3>📊 Live Data Connection</h3>
        <p>API Endpoint: <strong>http://localhost:8899/data</strong></p>
        <p>Status: <span id="status">Connecting...</span></p>
    </div>
    
    <button class="btn" onclick="testConnection()">🔄 Test Connection</button>
    <button class="btn" onclick="loadData()">📥 Load Data</button>
    
    <div id="results"></div>
    
    <script>
        const API_URL = 'http://localhost:8899';
        
        async function testConnection() {
            try {
                const res = await fetch(API_URL + '/health');
                const data = await res.json();
                document.getElementById('status').innerHTML = '✅ Connected';
                document.getElementById('status').style.color = '#27ae60';
            } catch (e) {
                document.getElementById('status').innerHTML = '❌ Not Connected';
                document.getElementById('status').style.color = '#e74c3c';
            }
        }
        
        async function loadData() {
            try {
                const res = await fetch(API_URL + '/summary');
                const data = await res.json();
                
                let html = '<table><tr><th>Metric</th><th>Value</th></tr>';
                html += '<tr><td>Total Transactions</td><td>' + data.total_transactions + '</td></tr>';
                html += '<tr><td>Total Amount</td><td>$' + data.total_amount.toFixed(2) + '</td></tr>';
                html += '<tr><td>Fraud Count</td><td class="high">' + data.fraud_count + '</td></tr>';
                html += '<tr><td>High Risk</td><td class="high">' + data.high_risk + '</td></tr>';
                html += '<tr><td>Medium Risk</td><td class="medium">' + data.medium_risk + '</td></tr>';
                html += '<tr><td>Low Risk</td><td class="low">' + data.low_risk + '</td></tr>';
                html += '</table>';
                
                document.getElementById('results').innerHTML = html;
            } catch (e) {
                document.getElementById('results').innerHTML = 'Error: ' + e.message;
            }
        }
        
        // Auto test on load
        testConnection();
    </script>
</body>
</html>"""
    
    with open("tableau_connector.html", "w") as f:
        f.write(html)
    print("✅ Created: tableau_connector.html")


if __name__ == "__main__":
    print("=" * 60)
    print("🛡️ FraudShield AI - Tableau Live Connection")
    print("=" * 60)
    
    # Create web connector HTML
    create_tableau_web_connector_html()
    
    # Start API server
    print("\n🚀 Starting real-time data server...")
    start_api_server()