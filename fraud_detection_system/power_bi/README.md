# Power BI Integration for FraudShield AI

This module enables real-time streaming of transaction data to Power BI dashboards.

## Overview

When transactions are processed by FraudShield AI, they can be automatically pushed to a Power BI streaming dataset for real-time visualization in Power BI dashboards.

## Files

- `config.py` - Configuration for Power BI credentials
- `powerbi_pusher.py` - Main module that handles data streaming
- `setup_power_bi.py` - Script to create the Power BI streaming dataset

## Setup Instructions

### Step 1: Create Azure AD App

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **App registrations** → **New registration**
3. Name: `FraudShield Power BI`
4. Supported account types: Single tenant (your org)
5. After creation, note down:
   - Application (client) ID → CLIENT_ID
   - Directory (tenant) ID → TENANT_ID

### Step 2: Add Power BI API Permissions

1. In your Azure AD app, go to **API permissions**
2. Click **Add a permission** → **Power BI API**
3. Select these delegated permissions:
   - `Dataset.ReadWrite.All`
   - `Report.ReadWrite.All`
4. Click **Grant admin consent** (or request admin to approve)

### Step 3: Create Client Secret

1. In your Azure AD app, go to **Certificates & secrets**
2. Click **New client secret**
3. Note the secret value → CLIENT_SECRET

### Step 4: Get Workspace ID

1. Go to [Power BI](https://app.powerbi.com)
2. Open your workspace settings
3. Copy the Workspace ID from the URL:
   - `app.powerbi.com/groups/<THIS_IS_YOUR_WORKSPACE_ID>/...`

### Step 5: Create Streaming Dataset

```bash
cd fraud_detection_system
source .venv/bin/activate
cd power_bi
python setup_power_bi.py
```

This will create a streaming dataset and output the Dataset ID.

### Step 6: Update Configuration

Edit `power_bi/config.py` and replace the placeholder values:

```python
POWER_BI_WORKSPACE_ID = "your-actual-workspace-id"
POWER_BI_DATASET_ID = "your-dataset-id-from-step-5"
POWER_BI_CLIENT_ID = "your-client-id"
POWER_BI_CLIENT_SECRET = "your-client-secret"
POWER_BI_TENANT_ID = "your-tenant-id"
```

### Step 7: Enable Power BI

In `power_bi/config.py`, ensure:
```python
POWER_BI_ENABLED = True
```

## How It Works

1. When FraudShield processes a transaction, it's pushed to Power BI
2. The transaction data is transformed to match Power BI's schema
3. Data is sent in real-time via Power BI's Push API
4. Power BI dashboards automatically update with new data

## Testing

1. Start FraudShield: `./start_fraud_system.sh`
2. In Power BI, create a report using your streaming dataset
3. Add a "Card" visualization for key metrics
4. Watch real-time updates as transactions flow in!

## Troubleshooting

### "Failed to get access token"
- Verify Azure AD app credentials are correct
- Ensure API permissions are granted
- Check that admin consent was given

### "Failed to push to Power BI"
- Verify Dataset ID is correct
- Check Power BI workspace is accessible
- Ensure dataset is set to "Streaming"

## Alternative: Without Authentication

If you don't want to set up Azure AD, you can use the "Embed" token approach:
1. In Power BI, go to your dataset → "Security"
2. Enable "Anonymous" (not recommended for production)

Or use the simpler approach:
1. Create a streaming dataset manually in Power BI UI
2. Get the push URL from dataset settings
3. Use that URL directly (no auth required for some dataset types)
