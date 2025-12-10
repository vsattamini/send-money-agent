"""Transaction history management using CSV as mock database."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from send_money_agent.models import Beneficiary, SUPPORTED_COUNTRIES


class TransactionHistoryRecord(BaseModel):
    """Record from transaction history."""

    phone_number: str
    beneficiary: Beneficiary
    country: str
    amount: float
    payment_method: str
    delivery_method: str
    timestamp: datetime
    confirmation_code: str


class TransactionHistory:
    """Manager for transaction history CSV."""

    def __init__(self, csv_path: Optional[Path] = None):
        """Initialize transaction history.

        Args:
            csv_path: Path to CSV file. Defaults to data/transaction_history.csv
        """
        if csv_path is None:
            csv_path = Path(__file__).parent.parent / "data" / "transaction_history.csv"
        self.csv_path = csv_path

    def load_all(self) -> List[TransactionHistoryRecord]:
        """Load all transactions from CSV.

        Returns:
            List of TransactionHistoryRecord objects
        """
        records = []

        if not self.csv_path.exists():
            return records

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = TransactionHistoryRecord(
                    phone_number=row["phone_number"],
                    beneficiary=Beneficiary(
                        firstname=row["beneficiary_firstname"],
                        lastname=row["beneficiary_lastname"],
                    ),
                    country=row["country"],
                    amount=float(row["amount"]),
                    payment_method=row["payment_method"],
                    delivery_method=row["delivery_method"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    confirmation_code=row["confirmation_code"],
                )
                records.append(record)

        return records

    def get_user_transactions(self, phone_number: str) -> List[TransactionHistoryRecord]:
        """Get all transactions for a specific user.

        Args:
            phone_number: User's phone number

        Returns:
            List of transactions for this user, sorted by timestamp descending
        """
        all_records = self.load_all()
        user_records = [r for r in all_records if r.phone_number == phone_number]

        # Sort by timestamp descending (most recent first)
        user_records.sort(key=lambda x: x.timestamp, reverse=True)

        return user_records


def find_beneficiary_history(
    history: TransactionHistory,
    phone_number: str,
    firstname: Optional[str] = None,
    lastname: Optional[str] = None,
) -> List[TransactionHistoryRecord]:
    """Find transaction history for a beneficiary.

    Args:
        history: TransactionHistory instance
        phone_number: User's phone number
        firstname: Beneficiary first name (case insensitive)
        lastname: Beneficiary last name (case insensitive, optional)

    Returns:
        List of matching transactions, sorted by timestamp descending
    """
    user_txns = history.get_user_transactions(phone_number)

    if not firstname:
        return []

    # Filter by beneficiary name (case insensitive)
    matches = []
    for txn in user_txns:
        firstname_match = txn.beneficiary.firstname.lower() == firstname.lower()

        if lastname:
            lastname_match = txn.beneficiary.lastname.lower() == lastname.lower()
            if firstname_match and lastname_match:
                matches.append(txn)
        else:
            if firstname_match:
                matches.append(txn)

    return matches
