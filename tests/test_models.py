"""Test Pydantic data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from send_money_agent.models import (
    Beneficiary,
    Transaction,
    TransferLimits,
    SUPPORTED_COUNTRIES,
    PAYMENT_METHODS,
    DELIVERY_METHODS,
)


def test_beneficiary_validation():
    """Test Beneficiary model validation."""
    beneficiary = Beneficiary(firstname="John", lastname="Matthews")
    assert beneficiary.firstname == "John"
    assert beneficiary.lastname == "Matthews"
    assert beneficiary.full_name == "John Matthews"


def test_beneficiary_requires_both_names():
    """Test Beneficiary requires firstname and lastname."""
    with pytest.raises(ValidationError):
        Beneficiary(firstname="John")


def test_transaction_valid():
    """Test valid Transaction creation."""
    transaction = Transaction(
        beneficiary=Beneficiary(firstname="John", lastname="Matthews"),
        country="Colombia",
        amount=100.50,
        payment_method="credit_card",
        delivery_method="digital_wallet",
        timestamp=datetime.now(),
    )
    assert transaction.beneficiary.full_name == "John Matthews"
    assert transaction.country == "Colombia"
    assert transaction.amount == 100.50


def test_transaction_country_validation():
    """Test Transaction validates country."""
    with pytest.raises(ValidationError) as exc_info:
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="France",  # Not supported
            amount=100.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=datetime.now(),
        )
    assert "country" in str(exc_info.value).lower()


def test_transaction_amount_validation():
    """Test Transaction validates amount range."""
    # Too low
    with pytest.raises(ValidationError):
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=0.3,  # Below 0.5 minimum
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=datetime.now(),
        )

    # Too high
    with pytest.raises(ValidationError):
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=20000.0,  # Above daily limit
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=datetime.now(),
        )


def test_transaction_payment_method_validation():
    """Test Transaction validates payment method."""
    with pytest.raises(ValidationError):
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=100.0,
            payment_method="crypto",  # Not supported
            delivery_method="digital_wallet",
            timestamp=datetime.now(),
        )


def test_transaction_delivery_method_validation():
    """Test Transaction validates delivery method."""
    with pytest.raises(ValidationError):
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=100.0,
            payment_method="credit_card",
            delivery_method="cash_pickup",  # Not supported
            timestamp=datetime.now(),
        )


def test_transfer_limits_initialization():
    """Test TransferLimits initialization."""
    limits = TransferLimits()
    assert limits.daily_limit == 1500.0
    assert limits.monthly_limit == 3000.0
    assert limits.semester_limit == 18000.0
    assert limits.daily_used == 0.0
    assert limits.monthly_used == 0.0
    assert limits.semester_used == 0.0


def test_transfer_limits_remaining():
    """Test TransferLimits remaining calculations."""
    limits = TransferLimits(daily_used=500.0, monthly_used=1000.0, semester_used=5000.0)
    assert limits.daily_remaining == 1000.0
    assert limits.monthly_remaining == 2000.0
    assert limits.semester_remaining == 13000.0


def test_transfer_limits_can_transfer():
    """Test TransferLimits can_transfer validation."""
    limits = TransferLimits(daily_used=1400.0, monthly_used=2500.0, semester_used=10000.0)

    # Can transfer within all limits
    can_transfer, reason = limits.can_transfer(50.0)
    assert can_transfer is True
    assert reason is None

    # Cannot transfer - exceeds daily limit
    can_transfer, reason = limits.can_transfer(200.0)
    assert can_transfer is False
    assert "daily" in reason.lower()
    assert "100.00" in reason  # Remaining daily limit

    # Cannot transfer - exceeds monthly limit
    limits_monthly = TransferLimits(daily_used=0.0, monthly_used=2900.0, semester_used=10000.0)
    can_transfer, reason = limits_monthly.can_transfer(200.0)
    assert can_transfer is False
    assert "monthly" in reason.lower()
    assert "100.00" in reason


def test_supported_constants():
    """Test that supported constants are defined correctly."""
    assert len(SUPPORTED_COUNTRIES) == 6
    assert "México" in SUPPORTED_COUNTRIES
    assert "Colombia" in SUPPORTED_COUNTRIES

    assert len(PAYMENT_METHODS) == 3
    assert "credit_card" in PAYMENT_METHODS

    assert len(DELIVERY_METHODS) == 2
    assert "digital_wallet" in DELIVERY_METHODS
    assert "bank_account" in DELIVERY_METHODS
