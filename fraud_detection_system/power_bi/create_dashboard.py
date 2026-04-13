"""
Auto-create Power BI Dashboard for FraudShield
Run this after setting up the streaming dataset
"""

import requests
import json
import os

# Your credentials
POWERBI_WORKSPACE_ID = "34bd8bed-2ac1-41ae-9f08-4e0a3f11706c"  # from your Push URL
POWERBI_DATASET_ID = "b711598e-6df8-4367-bae2-33eb883426bb"  # from your Push URL

# For creating reports, you need to use the Power BI JavaScript SDK or REST API
# But this requires embedding credentials which is complex

# Alternative: Export a template that can be imported
# Let's create a simple HTML dashboard instead that works with your data!

HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>FraudShield Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
               background: #0f172a; color: white; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; color: #22d3ee; }
        .header p { color: #94a3b8; margin-top: 5px; }
        
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #1e293b; border-radius: 12px; padding: 20px; text-align: center;
                     border: 1px solid #334155; }
        .stat-card .label { color: #94a3b8; font-size: 0.9rem; margin-bottom: 8px; }
        .stat-card .value { font-size: 2.5rem; font-weight: bold; color: #22d3ee; }
        .stat-card.fraud .value { color: #f87171; }
        .stat-card.risk .value { color: #fbbf24; }
        
        .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .chart { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .chart h3 { margin-bottom: 15px; color: #e2e8f0; }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { color: #94a3b8; font-weight: 500; }
        .risk-high { color: #f87171; }
        .risk-medium { color: #fbbf24; }
        .risk-low { color: #4ade80; }
        
        #live { margin-top: 30px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ FraudShield Dashboard</h1>
        <p>Real-time fraud detection monitoring</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="label">Total Transactions</div>
            <div class="value" id="total">0</div>
        </div>
        <div class="stat-card fraud">
            <div class="label">Fraud Detected</div>
            <div class="value" id="fraud">0</div>
        </div>
        <div class="stat-card">
            <div class="label">Avg Fraud %</div>
            <div class="value" id="avg">0%</div>
        </div>
        <div class="stat-card risk">
            <div class="label">High Risk</div>
            <div class="value" id="high">0</div>
        </div>
    </div>
    
    <div class="charts">
        <div class="chart">
            <h3>📊 By Category</h3>
            <div id="categoryChart"></div>
        </div>
        <div class="chart">
            <h3>🎯 Risk Distribution</h3>
            <div id="riskChart"></div>
        </div>
    </div>
    
    <div class="chart" id="live">
        <h3>📋 Recent Transactions</h3>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Fraud %</th>
                    <th>Risk</th>
                </tr>
            </thead>
            <tbody id="transactions"></tbody>
        </table>
    </div>

    <script>
        // Connect to your WebSocket
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        let total = 0, fraud = 0, totalProb = 0, highRisk = 0;
        let categories = {};
        let risks = { LOW: 0, MEDIUM: 0, HIGH: 0 };
        let transactions = [];
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'transaction') {
                const t = data.data;
                total++;
                if (t.prediction === 1) fraud++;
                totalProb += t.fraud_probability;
                if (t.risk_level === 'HIGH') highRisk++;
                
                categories[t.merchant_category] = (categories[t.merchant_category] || 0) + 1;
                risks[t.risk_level] = (risks[t.risk_level] || 0) + 1;
                
                transactions.unshift(t);
                if (transactions.length > 10) transactions.pop();
                
                updateUI();
            }
        };
        
        function updateUI() {
            document.getElementById('total').textContent = total;
            document.getElementById('fraud').textContent = fraud;
            document.getElementById('avg').textContent = total ? (totalProb / total * 100).toFixed(1) + '%' : '0%';
            document.getElementById('high').textContent = highRisk;
            
            // Category chart
            let catHtml = '';
            for (const [cat, count] of Object.entries(categories)) {
                const pct = (count / total * 100).toFixed(0);
                catHtml += `<div style="margin: 8px 0;"><span>${cat}</span> <span style="float:right">${pct}%</span>
                    <div style="background:#334155;height:8px;border-radius:4px;margin-top:4px">
                        <div style="background:#22d3ee;height:100%;width:${pct}%"></div>
                    </div></div>`;
            }
            document.getElementById('categoryChart').innerHTML = catHtml;
            
            // Risk chart
            let riskHtml = '';
            for (const [risk, count] of Object.entries(risks)) {
                const pct = (count / total * 100).toFixed(0);
                const color = risk === 'HIGH' ? '#f87171' : risk === 'MEDIUM' ? '#fbbf24' : '#4ade80';
                riskHtml += `<div style="margin: 8px 0;"><span>${risk}</span> <span style="float:right">${pct}%</span>
                    <div style="background:#334155;height:8px;border-radius:4px;margin-top:4px">
                        <div style="background:${color};height:100%;width:${pct}%"></div>
                    </div></div>`;
            }
            document.getElementById('riskChart').innerHTML = riskHtml;
            
            // Transactions table
            let html = '';
            for (const t of transactions) {
                const riskClass = t.risk_level === 'HIGH' ? 'risk-high' : t.risk_level === 'MEDIUM' ? 'risk-medium' : 'risk-low';
                html += `<tr>
                    <td>${t.transaction_id}</td>
                    <td>$${t.amount}</td>
                    <td>${t.merchant_category}</td>
                    <td>${(t.fraud_probability * 100).toFixed(1)}%</td>
                    <td class="${riskClass}">${t.risk_level}</td>
                </tr>`;
            }
            document.getElementById('transactions').innerHTML = html;
        }
    </script>
</body>
</html>
"""

# Save the dashboard
with open("fraud_detection_system/dashboard/index.html", "w") as f:
    f.write(HTML_DASHBOARD)

print("✅ Created real-time dashboard at: fraud_detection_system/dashboard/index.html")
print("\nThis dashboard connects directly to your WebSocket and shows:")
print("  - Total transactions")
print("  - Fraud count")  
print("  - Average fraud probability")
print("  - Risk distribution")
print("  - Recent transactions")
print("\nThis is much easier than Power BI - just open the HTML file in your browser!")
print("\nTo view it, make sure FraudShield is running, then open:")
print("  http://localhost:3000")
