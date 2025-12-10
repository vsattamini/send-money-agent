"""Integration tests for complete workflows."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from send_money_agent.agent import create_agent, AGENT_INSTRUCTION
from send_money_agent.models import Beneficiary, Transaction
from send_money_agent.history import TransactionHistory, find_beneficiary_history
from send_money_agent.limits import LimitsTracker


def test_end_to_end_beneficiary_lookup():
    """Test complete flow of looking up beneficiary history."""
    # Load history with test data
    test_data_path = Path(__file__).parent.parent / "data" / "transaction_history.csv"
    history = TransactionHistory(csv_path=test_data_path)

    # Find John Matthews transactions
    matches = find_beneficiary_history(
        history, "+1234567890", firstname="John", lastname="Matthews"
    )

    assert len(matches) > 0
    most_recent = matches[0]

    # Verify we can use this info for a new transfer
    assert most_recent.country in ["Colombia", "México", "Guatemala", "Honduras", "El Salvador", "República Dominicana"]
    assert most_recent.delivery_method in ["digital_wallet", "bank_account"]


def test_end_to_end_limit_validation():
    """Test complete flow of validating transfer limits."""
    now = datetime.now()

    # Create mock transaction history for user
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=1000.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(hours=5),
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Jane", lastname="Doe"),
            country="Colombia",
            amount=300.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=10),
        ),
    ]

    # Check limits for new transfer
    tracker = LimitsTracker(transactions, now)

    # Should be able to transfer $400 (within daily limit)
    can_transfer, reason = tracker.check_limits(400.0)
    assert can_transfer is True

    # Should NOT be able to transfer $600 (exceeds daily limit)
    can_transfer, reason = tracker.check_limits(600.0)
    assert can_transfer is False
    assert "daily" in reason.lower()


def test_end_to_end_new_transfer_validation():
    """Test creating a valid new transfer."""
    transaction = Transaction(
        beneficiary=Beneficiary(firstname="Carlos", lastname="Rodriguez"),
        country="Guatemala",
        amount=250.0,
        payment_method="bank_transfer",
        delivery_method="bank_account",
        timestamp=datetime.now(),
    )

    assert transaction.beneficiary.full_name == "Carlos Rodriguez"
    assert transaction.country == "Guatemala"
    assert transaction.amount == 250.0


def test_workflow_ambiguous_beneficiary_resolution():
    """Test workflow for resolving ambiguous beneficiary names."""
    # User says "send to John"
    # Agent should lookup history
    test_data_path = Path(__file__).parent.parent / "data" / "transaction_history.csv"
    history = TransactionHistory(csv_path=test_data_path)
    matches = find_beneficiary_history(history, "+1234567890", firstname="John")

    # Should find John Matthews
    assert len(matches) > 0

    # Get most recent
    most_recent = matches[0]

    # Agent can suggest: "I see you previously sent to John Matthews in Colombia"
    suggested_country = most_recent.country
    suggested_method = most_recent.delivery_method

    # User confirms, agent uses these details
    assert suggested_country is not None
    assert suggested_method is not None


def test_workflow_limit_exceeded_handling():
    """Test workflow when user exceeds transfer limit."""
    now = datetime.now()

    # User has used $1,400 today
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=1400.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(hours=2),
        ),
    ]

    tracker = LimitsTracker(transactions, now)

    # User tries to send $200
    can_transfer, reason = tracker.check_limits(200.0)

    # Should be blocked
    assert can_transfer is False

    # Reason should explain daily limit and remaining amount
    assert "daily" in reason.lower()
    assert "100.00" in reason  # $1500 - $1400 = $100 remaining


def test_workflow_multiple_beneficiaries():
    """Test handling multiple beneficiaries in history."""
    test_data_path = Path(__file__).parent.parent / "data" / "transaction_history.csv"
    history = TransactionHistory(csv_path=test_data_path)

    # Get all transactions for user
    user_txns = history.get_user_transactions("+1234567890")

    # Should have multiple different beneficiaries
    beneficiary_names = {txn.beneficiary.full_name for txn in user_txns}

    assert len(beneficiary_names) > 1
    assert "John Matthews" in beneficiary_names
    assert "Maria Garcia" in beneficiary_names
