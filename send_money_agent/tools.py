"""ADK tools for Send Money Agent."""

import secrets
from datetime import datetime
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext
from pydantic import ValidationError
from send_money_agent.models import (
    Beneficiary,
    Transaction,
    SUPPORTED_COUNTRIES,
    PAYMENT_METHODS,
    DELIVERY_METHODS,
    MIN_AMOUNT,
)


def set_country(tool_context: ToolContext, country: str) -> Dict[str, Any]:
    """Set or update the destination country for the transfer.

    Args:
        tool_context: ADK tool context with state access
        country: Destination country name

    Returns:
        Dictionary with success status and country value or error message
    """
    # Normalize to title case and validate
    country_lower = country.lower()
    normalized_country = None

    for supported in SUPPORTED_COUNTRIES:
        if supported.lower() == country_lower:
            normalized_country = supported
            break

    if not normalized_country:
        return {
            "success": False,
            "error": f"Country '{country}' is not supported. Supported countries: {', '.join(SUPPORTED_COUNTRIES)}",
        }

    # Update state
    tool_context.state["country"] = normalized_country

    return {
        "success": True,
        "country": normalized_country,
        "message": f"Country set to {normalized_country}",
    }


def set_amount(tool_context: ToolContext, amount: float) -> Dict[str, Any]:
    """Set or update the transfer amount.

    Args:
        tool_context: ADK tool context with state access
        amount: Amount to send in USD

    Returns:
        Dictionary with success status, amount, and any limit warnings
    """
    # Validate minimum
    if amount < MIN_AMOUNT:
        return {
            "success": False,
            "error": f"Amount must be at least ${MIN_AMOUNT} USD",
        }

    # TODO: Add limit validation using transaction history
    # For now, just validate against Pydantic model max (daily limit)
    try:
        # This will raise if amount > DAILY_LIMIT
        Transaction(
            beneficiary=Beneficiary(firstname="Test", lastname="User"),
            country="México",
            amount=amount,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=datetime.now(),
        )
    except ValidationError as e:
        return {
            "success": False,
            "error": str(e.errors()[0]["msg"]),
        }

    # Update state
    tool_context.state["amount"] = amount

    return {
        "success": True,
        "amount": amount,
        "message": f"Amount set to ${amount:.2f} USD",
    }


def set_beneficiary(
    tool_context: ToolContext, firstname: str, lastname: str
) -> Dict[str, Any]:
    """Set or update the beneficiary (recipient) of the transfer.

    Args:
        tool_context: ADK tool context with state access
        firstname: Beneficiary first name
        lastname: Beneficiary last name

    Returns:
        Dictionary with success status and beneficiary full name
    """
    # Validate both names provided
    if not firstname or not lastname:
        return {
            "success": False,
            "error": "Both first name and last name are required for beneficiary",
        }

    # Create beneficiary to validate
    try:
        beneficiary = Beneficiary(firstname=firstname, lastname=lastname)
    except ValidationError as e:
        return {
            "success": False,
            "error": str(e.errors()[0]["msg"]),
        }

    # Update state
    tool_context.state["beneficiary_firstname"] = firstname
    tool_context.state["beneficiary_lastname"] = lastname

    return {
        "success": True,
        "beneficiary": beneficiary.full_name,
        "message": f"Beneficiary set to {beneficiary.full_name}",
    }


def set_payment_method(tool_context: ToolContext, payment_method: str) -> Dict[str, Any]:
    """Set or update the payment method.

    Args:
        tool_context: ADK tool context with state access
        payment_method: Payment method ID (credit_card, debit_card, bank_transfer)

    Returns:
        Dictionary with success status and payment method
    """
    if payment_method not in PAYMENT_METHODS:
        return {
            "success": False,
            "error": f"Payment method '{payment_method}' is not supported. Supported: {', '.join(PAYMENT_METHODS)}",
        }

    # Update state
    tool_context.state["payment_method"] = payment_method

    # Map to display name
    display_names = {
        "credit_card": "Credit Card",
        "debit_card": "Debit Card",
        "bank_transfer": "Bank Transfer",
    }

    return {
        "success": True,
        "payment_method": payment_method,
        "message": f"Payment method set to {display_names.get(payment_method, payment_method)}",
    }


def set_delivery_method(
    tool_context: ToolContext, delivery_method: str
) -> Dict[str, Any]:
    """Set or update the delivery method.

    Args:
        tool_context: ADK tool context with state access
        delivery_method: Delivery method ID (digital_wallet, bank_account)

    Returns:
        Dictionary with success status and delivery method
    """
    if delivery_method not in DELIVERY_METHODS:
        return {
            "success": False,
            "error": f"Delivery method '{delivery_method}' is not supported. Supported: {', '.join(DELIVERY_METHODS)}",
        }

    # Update state
    tool_context.state["delivery_method"] = delivery_method

    # Map to display name
    display_names = {
        "digital_wallet": "Digital Wallet",
        "bank_account": "Bank Account",
    }

    return {
        "success": True,
        "delivery_method": delivery_method,
        "message": f"Delivery method set to {display_names.get(delivery_method, delivery_method)}",
    }


def transfer_money(
    tool_context: ToolContext,
    beneficiary_firstname: str,
    beneficiary_lastname: str,
    country: str,
    amount: float,
    payment_method: str,
    delivery_method: str,
) -> Dict[str, Any]:
    """Execute a money transfer (mock implementation).

    This is the primary tool that executes the transfer after all details
    have been collected and validated.

    Args:
        tool_context: ADK tool context with state access
        beneficiary_firstname: Beneficiary first name
        beneficiary_lastname: Beneficiary last name
        country: Destination country
        amount: Transfer amount in USD
        payment_method: Payment method (credit_card, debit_card, bank_transfer)
        delivery_method: Delivery method (digital_wallet, bank_account)

    Returns:
        Dictionary with success status, confirmation code, or error message
    """
    try:
        # Create and validate beneficiary
        beneficiary = Beneficiary(
            firstname=beneficiary_firstname, lastname=beneficiary_lastname
        )

        # Create and validate transaction (Pydantic will validate all fields)
        transaction = Transaction(
            beneficiary=beneficiary,
            country=country,
            amount=amount,
            payment_method=payment_method,
            delivery_method=delivery_method,
            timestamp=datetime.now(),
        )

        # Generate mock confirmation code
        confirmation_code = f"TXN-{secrets.token_hex(4).upper()}"

        # Store confirmation in state for reference
        tool_context.state["last_transfer_confirmation"] = confirmation_code
        tool_context.state["last_transfer_amount"] = amount
        tool_context.state["last_transfer_beneficiary"] = beneficiary.full_name

        return {
            "success": True,
            "confirmation_code": confirmation_code,
            "amount": amount,
            "beneficiary": beneficiary.full_name,
            "country": country,
            "payment_method": payment_method,
            "delivery_method": delivery_method,
            "message": f"Transfer of ${amount:.2f} USD to {beneficiary.full_name} in {country} confirmed. Confirmation code: {confirmation_code}",
        }

    except ValidationError as e:
        # Extract first error message
        error_msg = str(e.errors()[0]["msg"]) if e.errors() else str(e)
        return {"success": False, "error": error_msg}

    except Exception as e:
        return {"success": False, "error": f"Transfer failed: {str(e)}"}
