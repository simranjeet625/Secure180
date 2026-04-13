"""
Export fraud detection data from SQLite to CSV for Tableau visualization.
Run this script to generate fraud_transactions.csv that can be imported into Tableau.
"""

import sqlite3
import csv
import os
from datetime import datetime

DATABASE_PATH = "database/fraud_detection.db"
OUTPUT_FILE = "data/fraud_transactions_tableau.csv"

def export_to_csv():
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found at: {DATABASE_PATH}")
        print("   Please run the system first: python run_system.py")
        return False
    
    # Connect to database
    print(f"📂 Connecting to: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"📊 Found tables: {[t[0] for t in tables]}")
    
    # Check if transactions table exists
    if ('transactions',) not in tables:
        print("❌ 'transactions' table not found!")
        print("   Run the system to generate data: python run_system.py")
        conn.close()
        return False
    
    # Get row count
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    print(f"📈 Found {count} transactions in database")
    
    if count == 0:
        print("❌ No transactions found!")
        print("   Run the system to generate data: python run_system.py")
        conn.close()
        return False
    
    # Fetch all data with column names
    cursor.execute("PRAGMA table_info(transactions)")
    columns_info = cursor.fetchall()
    columns = [col[1] for col in columns_info]
    
    print(f"📋 Columns: {columns}")
    
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    
    # Write to CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # Header
        writer.writerows(rows)     # Data
    
    conn.close()
    
    print(f"✅ Successfully exported to: {OUTPUT_FILE}")
    print(f"   Total rows: {count}")
    print(f"   Total columns: {len(columns)}")
    
    # Show file size
    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"   File size: {file_size / 1024:.2f} KB")
    
    return True


def export_with_aggregation():
    """Export pre-aggregated data for KPI visualizations"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    output_file = "data/fraud_summary_tableau.csv"
    
    # KPI Summary Query
    query = """
    SELECT 
        COUNT(*) as total_transactions,
        SUM(amount) as total_amount,
        SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_count,
        AVG(CASE WHEN prediction = 1 THEN 1.0 ELSE 0.0 END) * 100 as fraud_rate_percent,
        SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk_count,
        SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END) as medium_risk_count,
        SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) as low_risk_count
    FROM transactions
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    if row:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'total_transactions', 'total_amount', 'fraud_count', 
                'fraud_rate_percent', 'high_risk_count', 'medium_risk_count', 'low_risk_count'
            ])
            writer.writerow(row)
        
        print(f"✅ KPI Summary exported to: {output_file}")
    
    # Category breakdown
    category_file = "data/fraud_category_tableau.csv"
    query2 = """
    SELECT 
        merchant_category,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_count,
        AVG(fraud_probability) as avg_fraud_prob
    FROM transactions
    GROUP BY merchant_category
    ORDER BY total_amount DESC
    """
    
    cursor.execute(query2)
    rows = cursor.fetchall()
    
    with open(category_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'merchant_category', 'transaction_count', 'total_amount', 
            'fraud_count', 'avg_fraud_prob'
        ])
        writer.writerows(rows)
    
    print(f"✅ Category breakdown exported to: {category_file}")
    
    conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("FraudShield AI - Export for Tableau")
    print("=" * 50)
    
    success = export_to_csv()
    
    if success:
        print("\n" + "=" * 50)
        print("🎯 Next Steps for Tableau:")
        print("=" * 50)
        print("""
1. Open Tableau Desktop
2. Click "Connect" → "Text file" or "Microsoft Excel"
3. Select: fraud_transactions_tableau.csv
4. Drag table to the canvas
5. Create your visualizations!

Files created:
- fraud_transactions_tableau.csv (Full transaction data)
- fraud_summary_tableau.csv (KPI summary)
- fraud_category_tableau.csv (Category breakdown)
        """)
    
    # Export additional files
    try:
        export_with_aggregation()
    except Exception as e:
        print(f"⚠️ Could not export aggregation: {e}")