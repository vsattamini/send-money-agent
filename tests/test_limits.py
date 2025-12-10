"""Test transfer limits tracking."""

import pytest
from datetime import datetime, timedelta
from send_money_agent.limits import (
    LimitsTracker,
    calculate_period_usage,
)
from send_money_agent.models import Beneficiary, Transaction


def test_calculate_period_usage_daily():
    """Test calculating daily usage."""
    now = datetime.now()
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=100.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(hours=2),
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Jane", lastname="Doe"),
            country="Colombia",
            amount=200.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(hours=5),
        ),
        # This one is from yesterday, shouldn't count
        Transaction(
            beneficiary=Beneficiary(firstname="Old", lastname="Transfer"),
            country="México",
            amount=500.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=2),
        ),
    ]

    daily_usage = calculate_period_usage(transactions, now, period="daily")
    assert daily_usage == 300.0  # Only today's transactions


def test_calculate_period_usage_monthly():
    """Test calculating monthly usage."""
    now = datetime.now()
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=100.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=5),
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Jane", lastname="Doe"),
            country="Colombia",
            amount=200.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=15),
        ),
        # This one is from 2 months ago, shouldn't count
        Transaction(
            beneficiary=Beneficiary(firstname="Old", lastname="Transfer"),
            country="México",
            amount=500.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=65),
        ),
    ]

    monthly_usage = calculate_period_usage(transactions, now, period="monthly")
    assert monthly_usage == 300.0


def test_calculate_period_usage_semester():
    """Test calculating semester usage."""
    now = datetime.now()
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=100.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=30),
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Jane", lastname="Doe"),
            country="Colombia",
            amount=200.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=90),
        ),
        # This one is from 7 months ago, shouldn't count
        Transaction(
            beneficiary=Beneficiary(firstname="Old", lastname="Transfer"),
            country="México",
            amount=500.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=210),
        ),
    ]

    semester_usage = calculate_period_usage(transactions, now, period="semester")
    assert semester_usage == 300.0


def test_limits_tracker_check_limits_within():
    """Test LimitsTracker when transfer is within limits."""
    now = datetime.now()
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=500.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(hours=2),
        ),
    ]

    tracker = LimitsTracker(transactions, now)
    can_transfer, reason = tracker.check_limits(400.0)

    assert can_transfer is True
    assert reason is None


def test_limits_tracker_check_limits_exceeds_daily():
    """Test LimitsTracker when exceeding daily limit."""
    now = datetime.now()
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
    can_transfer, reason = tracker.check_limits(200.0)

    assert can_transfer is False
    assert "daily" in reason.lower()
    assert "100.00" in reason  # Remaining daily


def test_limits_tracker_check_limits_exceeds_monthly():
    """Test LimitsTracker when exceeding monthly limit."""
    now = datetime.now()
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=1000.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=5),
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Jane", lastname="Doe"),
            country="Colombia",
            amount=1800.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=10),
        ),
    ]

    tracker = LimitsTracker(transactions, now)
    can_transfer, reason = tracker.check_limits(300.0)

    assert can_transfer is False
    assert "monthly" in reason.lower()
    assert "200.00" in reason  # Remaining monthly


def test_limits_tracker_check_limits_exceeds_semester():
    """Test LimitsTracker when exceeding semester limit."""
    now = datetime.now()
    # Spread transactions across months to avoid monthly limit
    # Use smaller amounts that add up to near semester limit
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=2900.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=35),  # Outside monthly window
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Jane", lastname="Doe"),
            country="Colombia",
            amount=2900.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=65),  # Outside monthly window
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Carlos", lastname="Smith"),
            country="Guatemala",
            amount=2900.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=95),  # Outside monthly window
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Maria", lastname="Jones"),
            country="Honduras",
            amount=2900.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=125),  # Outside monthly window
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Pedro", lastname="Garcia"),
            country="El Salvador",
            amount=2900.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(days=155),  # Outside monthly window
        ),
        Transaction(
            beneficiary=Beneficiary(firstname="Ana", lastname="Lopez"),
            country="Colombia",
            amount=2900.0,
            payment_method="debit_card",
            delivery_method="bank_account",
            timestamp=now - timedelta(days=175),  # Last one in semester
        ),
    ]
    # Total: 6 * $2900 = $17,400 within semester (limit is $18,000)
    # Each is outside the monthly window (30 days)

    tracker = LimitsTracker(transactions, now)
    can_transfer, reason = tracker.check_limits(700.0)  # Would be $18,100 total

    assert can_transfer is False
    assert "semester" in reason.lower()
    assert "600.00" in reason  # Remaining semester ($18,000 - $17,400 = $600)


def test_limits_tracker_get_current_limits():
    """Test getting current limit status."""
    now = datetime.now()
    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=500.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(hours=2),
        ),
    ]

    tracker = LimitsTracker(transactions, now)
    limits = tracker.get_current_limits()

    assert limits.daily_used == 500.0
    assert limits.daily_remaining == 1000.0
    assert limits.monthly_used == 500.0
    assert limits.semester_used == 500.0
