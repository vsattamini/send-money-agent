"""Seed data for the Send Money Agent demo."""

import csv
from datetime import datetime, timedelta
from pathlib import Path

# Demo user: Major Carlos
MAJOR_CARLOS_PHONE = "+15550001111"
MAJOR_CARLOS_NAME = "Carlos Saavedra"

def create_seed_data():
    """Create initial seed data for the demo."""
    # Ensure local_data exists
    data_dir = Path("local_data")
    data_dir.mkdir(exist_ok=True)
    
    csv_path = data_dir / "transactions.csv"
    
    # Don't overwrite if exists and has content (basic check)
    if csv_path.exists() and csv_path.stat().st_size > 100:
        print(f"Data file already exists with content: {csv_path}")
        return

    print(f"Seeding data to: {csv_path}")
    
    now = datetime.now()
    
    # Create Major Carlos history
    # 1. Sent to Mom in Colombia last month
    # 2. Sent to Cousin in Mexico last week
    # 3. Sent to Friend in El Salvador yesterday
    
    headers = [
        "phone_number", "beneficiary_firstname", "beneficiary_lastname",
        "country", "amount", "payment_method", "delivery_method",
        "timestamp", "confirmation_code"
    ]
    
    rows = [
        # Old transfer (last month)
        {
            "phone_number": MAJOR_CARLOS_PHONE,
            "beneficiary_firstname": "Maria",
            "beneficiary_lastname": "Saavedra",
            "country": "Colombia",
            "amount": 200.0,
            "payment_method": "bank_transfer",
            "delivery_method": "bank_account",
            "timestamp": (now - timedelta(days=40)).isoformat(),
            "confirmation_code": "TXN-SEED-001"
        },
        # Recent transfer (last week)
        {
            "phone_number": MAJOR_CARLOS_PHONE,
            "beneficiary_firstname": "Juan",
            "beneficiary_lastname": "Perez",
            "country": "México",
            "amount": 150.0,
            "payment_method": "credit_card",
            "delivery_method": "digital_wallet",
            "timestamp": (now - timedelta(days=7)).isoformat(),
            "confirmation_code": "TXN-SEED-002"
        },
         # Very recent transfer (yesterday)
        {
            "phone_number": MAJOR_CARLOS_PHONE,
            "beneficiary_firstname": "Ana",
            "beneficiary_lastname": "Gomez",
            "country": "El Salvador",
            "amount": 300.0,
            "payment_method": "debit_card",
            "delivery_method": "digital_wallet",
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "confirmation_code": "TXN-SEED-003"
        }
    ]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        
    print("Seed data created successfully.")
    print(f"Major Carlos Phone: {MAJOR_CARLOS_PHONE}")

if __name__ == "__main__":
    create_seed_data()
