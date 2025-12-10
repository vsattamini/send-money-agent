"""Test state update and transfer tools."""

import pytest
from unittest.mock import Mock
from datetime import datetime
from send_money_agent.tools import (
    set_country,
    set_amount,
    set_beneficiary,
    set_payment_method,
    set_delivery_method,
    transfer_money,
)
from send_money_agent.models import Beneficiary


# State Update Tool Tests

def test_set_country_valid():
    """Test setting valid country."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_country(mock_context, "Colombia")

    assert result["success"] is True
    assert mock_context.state["country"] == "Colombia"
    assert result["country"] == "Colombia"


def test_set_country_invalid():
    """Test setting invalid country."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_country(mock_context, "France")

    assert result["success"] is False
    assert "error" in result
    assert "country" not in mock_context.state


def test_set_country_updates_existing():
    """Test updating existing country (correction)."""
    mock_context = Mock()
    mock_context.state = {"country": "México"}

    result = set_country(mock_context, "Colombia")

    assert result["success"] is True
    assert mock_context.state["country"] == "Colombia"


def test_set_amount_valid():
    """Test setting valid amount."""
    mock_context = Mock()
    mock_context.state = {"phone_number": "+1234567890"}

    result = set_amount(mock_context, 150.0)

    assert result["success"] is True
    assert mock_context.state["amount"] == 150.0
    assert result["amount"] == 150.0


def test_set_amount_below_minimum():
    """Test setting amount below minimum."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_amount(mock_context, 0.3)

    assert result["success"] is False
    assert "0.5" in result["error"]


def test_set_amount_validates_limits():
    """Test amount validates against user limits."""
    # Note: This requires transaction history, simplified for now
    mock_context = Mock()
    mock_context.state = {}

    result = set_amount(mock_context, 500.0)

    assert result["success"] is True
    # Limit validation will be enhanced with history lookup


def test_set_beneficiary_valid():
    """Test setting beneficiary."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_beneficiary(mock_context, "John", "Matthews")

    assert result["success"] is True
    assert mock_context.state["beneficiary_firstname"] == "John"
    assert mock_context.state["beneficiary_lastname"] == "Matthews"
    assert result["beneficiary"] == "John Matthews"


def test_set_beneficiary_missing_lastname():
    """Test setting beneficiary without lastname."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_beneficiary(mock_context, "John", "")

    assert result["success"] is False
    assert "both" in result["error"].lower()


def test_set_payment_method_valid():
    """Test setting valid payment method."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_payment_method(mock_context, "credit_card")

    assert result["success"] is True
    assert mock_context.state["payment_method"] == "credit_card"


def test_set_payment_method_invalid():
    """Test setting invalid payment method."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_payment_method(mock_context, "crypto")

    assert result["success"] is False
    assert "payment" in result["error"].lower()


def test_set_delivery_method_valid():
    """Test setting valid delivery method."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_delivery_method(mock_context, "digital_wallet")

    assert result["success"] is True
    assert mock_context.state["delivery_method"] == "digital_wallet"


def test_set_delivery_method_invalid():
    """Test setting invalid delivery method."""
    mock_context = Mock()
    mock_context.state = {}

    result = set_delivery_method(mock_context, "cash_pickup")

    assert result["success"] is False
    assert "delivery" in result["error"].lower()


# Transfer Money Tool Tests


def test_transfer_money_success():
    """Test successful transfer execution."""
    mock_context = Mock()
    mock_context.state = {
        "phone_number": "+1234567890",
    }

    result = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="John",
        beneficiary_lastname="Matthews",
        country="Colombia",
        amount=100.0,
        payment_method="credit_card",
        delivery_method="digital_wallet",
    )

    assert result["success"] is True
    assert "confirmation_code" in result
    assert result["confirmation_code"].startswith("TXN-")
    assert result["amount"] == 100.0
    assert result["beneficiary"] == "John Matthews"


def test_transfer_money_invalid_country():
    """Test transfer with invalid country."""
    mock_context = Mock()
    mock_context.state = {"phone_number": "+1234567890"}

    result = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="John",
        beneficiary_lastname="Doe",
        country="France",
        amount=100.0,
        payment_method="credit_card",
        delivery_method="digital_wallet",
    )

    assert result["success"] is False
    assert "error" in result
    assert "country" in result["error"].lower()


def test_transfer_money_invalid_amount():
    """Test transfer with invalid amount."""
    mock_context = Mock()
    mock_context.state = {"phone_number": "+1234567890"}

    result = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="John",
        beneficiary_lastname="Doe",
        country="México",
        amount=0.3,  # Below minimum
        payment_method="credit_card",
        delivery_method="digital_wallet",
    )

    assert result["success"] is False
    assert "error" in result
    assert "0.5" in result["error"]  # Minimum amount


def test_transfer_money_invalid_payment_method():
    """Test transfer with invalid payment method."""
    mock_context = Mock()
    mock_context.state = {"phone_number": "+1234567890"}

    result = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="John",
        beneficiary_lastname="Doe",
        country="México",
        amount=100.0,
        payment_method="crypto",
        delivery_method="digital_wallet",
    )

    assert result["success"] is False
    assert "error" in result
    assert "payment" in result["error"].lower()


def test_transfer_money_invalid_delivery_method():
    """Test transfer with invalid delivery method."""
    mock_context = Mock()
    mock_context.state = {"phone_number": "+1234567890"}

    result = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="John",
        beneficiary_lastname="Doe",
        country="México",
        amount=100.0,
        payment_method="credit_card",
        delivery_method="cash_pickup",
    )

    assert result["success"] is False
    assert "error" in result
    assert "delivery" in result["error"].lower()


def test_transfer_money_generates_unique_codes():
    """Test that transfer generates unique confirmation codes."""
    mock_context = Mock()
    mock_context.state = {"phone_number": "+1234567890"}

    result1 = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="John",
        beneficiary_lastname="Doe",
        country="México",
        amount=100.0,
        payment_method="credit_card",
        delivery_method="digital_wallet",
    )

    result2 = transfer_money(
        tool_context=mock_context,
        beneficiary_firstname="Jane",
        beneficiary_lastname="Doe",
        country="Colombia",
        amount=200.0,
        payment_method="debit_card",
        delivery_method="bank_account",
    )

    assert result1["confirmation_code"] != result2["confirmation_code"]
