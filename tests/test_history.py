"""Test transaction history module."""

import pytest
from pathlib import Path
from send_money_agent.history import (
    TransactionHistory,
    find_beneficiary_history,
)
from send_money_agent.models import Beneficiary


@pytest.fixture
def history():
    """Create TransactionHistory instance with test data."""
    test_data_path = Path(__file__).parent.parent / "data" / "transaction_history.csv"
    return TransactionHistory(csv_path=test_data_path)


def test_load_history(history):
    """Test loading transaction history from CSV."""
    transactions = history.load_all()
    assert len(transactions) > 0
    assert all(hasattr(t, "beneficiary") for t in transactions)


def test_get_user_transactions(history):
    """Test getting transactions for specific user."""
    user_txns = history.get_user_transactions("+1234567890")
    assert len(user_txns) == 4  # Based on mock CSV

    # Verify all transactions belong to user
    phone_numbers = {txn.phone_number for txn in user_txns}
    assert phone_numbers == {"+1234567890"}


def test_get_user_transactions_empty(history):
    """Test getting transactions for user with no history."""
    user_txns = history.get_user_transactions("+9999999999")
    assert len(user_txns) == 0


def test_find_beneficiary_history_exact_match(history):
    """Test finding exact beneficiary match."""
    matches = find_beneficiary_history(
        history, "+1234567890", firstname="John", lastname="Matthews"
    )
    assert len(matches) == 2  # Two transactions to John Matthews

    # Verify beneficiary details
    for match in matches:
        assert match.beneficiary.firstname == "John"
        assert match.beneficiary.lastname == "Matthews"


def test_find_beneficiary_history_firstname_only(history):
    """Test finding beneficiary by first name only."""
    matches = find_beneficiary_history(history, "+1234567890", firstname="John")
    assert len(matches) == 2


def test_find_beneficiary_history_no_match(history):
    """Test finding beneficiary with no matches."""
    matches = find_beneficiary_history(
        history, "+1234567890", firstname="Unknown", lastname="Person"
    )
    assert len(matches) == 0


def test_find_beneficiary_history_case_insensitive(history):
    """Test beneficiary search is case insensitive."""
    matches = find_beneficiary_history(
        history, "+1234567890", firstname="john", lastname="matthews"
    )
    assert len(matches) == 2


def test_get_most_recent_to_beneficiary(history):
    """Test getting most recent transaction to beneficiary."""
    matches = find_beneficiary_history(
        history, "+1234567890", firstname="John", lastname="Matthews"
    )
    most_recent = matches[0]  # Should be sorted by timestamp desc

    assert most_recent.beneficiary.full_name == "John Matthews"
    assert most_recent.confirmation_code == "TXN-003"  # Most recent


def test_transaction_history_record_structure(history):
    """Test TransactionHistoryRecord has all required fields."""
    records = history.load_all()
    record = records[0]

    assert hasattr(record, "phone_number")
    assert hasattr(record, "beneficiary")
    assert hasattr(record, "country")
    assert hasattr(record, "amount")
    assert hasattr(record, "payment_method")
    assert hasattr(record, "delivery_method")
    assert hasattr(record, "timestamp")
    assert hasattr(record, "confirmation_code")
