"""
Power BI Setup Script for FraudShield AI.

This script helps you set up the Power BI streaming dataset and get your credentials.
Run this from your local machine after installing requirements.
"""

import json
import requests

# Configuration - Fill in your Azure AD app details
TENANT_ID = "your-tenant-id"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
WORKSPACE_ID = "your-workspace-id"

# Dataset name
DATASET_NAME = "FraudShield Transactions"

# Define the schema for the streaming dataset
DATASET_SCHEMA = {
    "name": DATASET_NAME,
    "tables": [{
        "name": "Transaction",
        "columns": [
            {"name": "transaction_id", "dataType": "String"},
            {"name": "timestamp", "dataType": "DateTime"},
            {"name": "amount", "dataType": "Double"},
            {"name": "merchant_category", "dataType": "String"},
            {"name": "location", "dataType": "String"},
            {"name": "fraud_probability", "dataType": "Double"},
            {"name": "prediction", "dataType": "Int64"},
            {"name": "risk_level", "dataType": "String"},
            {"name": "processing_time_ms", "dataType": "Double"},
            {"name": "model_used", "dataType": "String"},
        ]
    }]
}


def get_access_token():
    """Get OAuth access token."""
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://analysis.windows.net/powerbi/api/.default",
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def create_streaming_dataset():
    """Create a streaming dataset in Power BI."""
    access_token = get_access_token()
    
    url = f"https://api.powerbi.com/v2.0/myorg/groups/{WORKSPACE_ID}/datasets"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Enable streaming
    dataset = DATASET_SCHEMA.copy()
    dataset["isStreamable"] = True
    
    response = requests.post(url, headers=headers, json=dataset)
    response.raise_for_status()
    
    dataset_info = response.json()
    print(f"✅ Created streaming dataset!")
    print(f"   Dataset ID: {dataset_info['id']}")
    print(f"   Dataset Name: {dataset_info['name']}")
    
    # Save the dataset ID
    with open("powerbi_dataset_info.json", "w") as f:
        json.dump(dataset_info, f, indent=2)
    
    print(f"\n📝 Next steps:")
    print(f"   1. Copy this Dataset ID to power_bi/config.py")
    print(f"   2. Dataset ID: {dataset_info['id']}")
    print(f"   3. Then restart your FraudShield system")
    
    return dataset_info["id"]


if __name__ == "__main__":
    print("=" * 60)
    print("Power BI Streaming Dataset Setup")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Create an Azure AD App with Power BI API permissions")
    print("2. Give the app admin access to your Power BI workspace")
    print("3. Update this script with your credentials\n")
    
    try:
        dataset_id = create_streaming_dataset()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("  - Updated TENANT_ID, CLIENT_ID, CLIENT_SECRET, WORKSPACE_ID")
        print("  - Granted Power BI workspace access to your Azure AD app")
