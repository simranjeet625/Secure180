# Complete Power BI Dashboard Setup Guide

This guide walks you through creating your FraudShield dashboard in Power BI from scratch — no prior Power BI knowledge needed!

---

## What You'll Build

Your final dashboard will look like this:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRAUDSHIELD DASHBOARD                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Total TXN    │  │ Fraud Count  │  │ Avg Fraud %  │     │
│  │    1,234     │  │      23      │  │    2.1%      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────┐     │
│  │ Transactions by     │  │ Risk Level Distribution │     │
│  │ Category (Bar)     │  │ (Pie Chart)              │     │
│  │                     │  │                          │     │
│  │ grocery   ████     │  │     ██  HIGH              │     │
│  │ online    ██       │  │   ███████ MEDIUM         │     │
│  │ travel    █████    │  │   ██████████ LOW         │     │
│  └─────────────────────┘  └─────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Access Power BI

1. Open your browser and go to: **https://app.powerbi.com**
2. Sign in with your Microsoft/Work account
3. You'll see your "Workspaces" on the left sidebar

---

## Step 2: Create Streaming Dataset

### Option A: Using the Setup Script (After you have Azure credentials)

Once you've configured your credentials in `config.py`:

```bash
cd fraud_detection_system/power_bi
python setup_power_bi.py
```

This creates the dataset automatically and saves the Dataset ID.

### Option B: Manual Creation (Easier!)

1. In Power BI, click **+ New** → **Streaming dataset**
2. Select **API** as the source
3. Name it: `FraudShield Transactions`
4. Add these fields (use the dropdowns):

| Field Name | Data Type |
|------------|-----------|
| transaction_id | Text |
| timestamp | Date/Time |
| amount | Number (Decimal) |
| merchant_category | Text |
| location | Text |
| fraud_probability | Number (Decimal) |
| prediction | Number (Whole) |
| risk_level | Text |
| processing_time_ms | Number (Decimal) |
| model_used | Text |

5. Toggle **Enable historical data analysis** → **Yes**
6. Click **Create**
7. **IMPORTANT**: Copy the "Push URL" shown — you'll need it for config.py

---

## Step 3: Create the Report

### 3.1 Start a New Report

1. Go to your workspace in Power BI
2. Find your dataset (FraudShield Transactions)
3. Click the **Create report** icon (or click the 3 dots → Create report)

### 3.2 Build Your First Card (Total Transactions)

1. In the right panel, expand your dataset fields
2. Find **transaction_id** field
3. Drag it onto the canvas
4. In the "Visualizations" panel (right side), click **Card** icon
5. The card shows "Count of transaction_id" — that's your total!
6. In the right panel, rename the title to: **"Total Transactions"**
7. Use the formatting options (paint roller icon) to:
   - Set font size to 24
   - Set color to blue

### 3.3 Build Fraud Count Card

1. Click on the canvas to add a new visual
2. Drag **prediction** field to canvas
3. Click **Card** visual
4. In the right panel, for "Field", change to show sum of prediction
   - Actually, we want COUNT where prediction = 1
5. Click the down arrow on prediction in the fields list → choose **Count (Distinct)** instead, but for fraud we need:
   - Add a **Filter** on this visual
   - Set prediction = 1
   - Then the card shows fraud count!

**Simpler way**: Just copy the first card, then add a filter:
- Click the card → in Filters panel → drag prediction to filter area
- Set "is" to "1"
- Rename to "Fraud Count"

### 3.4 Build Average Fraud Probability Card

1. Drag **fraud_probability** to canvas
2. Click **Card** visual
3. In the right panel, change from "Count" to "Average"
4. Format: set decimal places to 1, add "%" suffix in label
5. Rename to "Avg Fraud Probability"

### 3.5 Build Transactions by Category (Bar Chart)

1. Drag **merchant_category** to canvas
2. Click **Stacked bar chart** visual (in Visualizations panel)
3. Drag **transaction_id** to "Value" area
4. It should auto-count transactions per category
5. Format:
   - Title: "Transactions by Category"
   - Turn on data labels
   - Choose a nice color scheme

### 3.6 Build Risk Level Distribution (Pie Chart)

1. Drag **risk_level** to canvas
2. Click **Pie chart** visual
3. Drag **transaction_id** to "Values"
4. Format:
   - Title: "Risk Level Distribution"
   - Turn on labels
   - Choose colors: High=Red, Medium=Orange, Low=Green

---

## Step 4: Save and Pin

1. Click **Save** (top right)
2. Name: "FraudShield Dashboard"
3. Click **File** → **Save**
4. To pin to a dashboard:
   - Click **Pin** icon (top of your report)
   - Select "New dashboard" or existing
5. Now you can view it in your workspace!

---

## Step 5: Make it Real-Time

Since we're using streaming dataset:
1. Keep FraudShield running
2. Your Power BI dashboard will auto-refresh
3. New transactions appear in real-time!

---

## Quick Reference: Which Visual to Use

| Metric | Visual Type | Fields to Use |
|--------|--------------|---------------|
| Total Transactions | Card | transaction_id (Count) |
| Fraud Count | Card | prediction (Count with filter=1) |
| Avg Fraud Probability | Card | fraud_probability (Average) |
| By Category | Bar Chart | merchant_category + Count |
| Risk Distribution | Pie/Donut | risk_level + Count |
| Over Time | Line Chart | timestamp + Count |
| By Location | Map | location + Count |

---

## Troubleshooting

### No data appearing?
- Check your push URL is correct in config.py
- Make sure POWER_BI_ENABLED = True
- Check the Python logs for any errors

### Charts not updating?
- Power BI caches data — click Refresh in the visual
- Or use "Refresh" button in the report toolbar

### Need more help?
- Power BI has built-in help: Click "Learn" in the toolbar
- Search YouTube: "Power BI beginners tutorial"

---

Now go create your dashboard! Let me know when you're done and I can help with any issues.
