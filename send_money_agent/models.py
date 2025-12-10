"""Pydantic data models for Send Money Agent."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, computed_field


# Supported values
SUPPORTED_COUNTRIES = [
    "México",
    "Guatemala",
    "Honduras",
    "El Salvador",
    "República Dominicana",
    "Colombia",
]

PAYMENT_METHODS = ["credit_card", "debit_card", "bank_transfer"]
DELIVERY_METHODS = ["digital_wallet", "bank_account"]

# Transfer limits
MIN_AMOUNT = 0.5
DAILY_LIMIT = 1500.0
MONTHLY_LIMIT = 3000.0
SEMESTER_LIMIT = 18000.0


class Beneficiary(BaseModel):
    """Beneficiary information."""

    firstname: str = Field(..., min_length=1, description="Beneficiary first name")
    lastname: str = Field(..., min_length=1, description="Beneficiary last name")

    @computed_field
    @property
    def full_name(self) -> str:
        """Get full name of beneficiary."""
        return f"{self.firstname} {self.lastname}"

    model_config = {"frozen": True}


class Transaction(BaseModel):
    """Transaction record."""

    beneficiary: Beneficiary
    country: str
    amount: float = Field(..., gt=0)
    payment_method: str
    delivery_method: str
    timestamp: datetime
    confirmation_code: Optional[str] = None

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate country is supported."""
        if v not in SUPPORTED_COUNTRIES:
            raise ValueError(
                f"Country must be one of: {', '.join(SUPPORTED_COUNTRIES)}"
            )
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is within acceptable range."""
        if v < MIN_AMOUNT:
            raise ValueError(f"Amount must be at least ${MIN_AMOUNT} USD")
        if v > DAILY_LIMIT:
            raise ValueError(f"Amount cannot exceed daily limit of ${DAILY_LIMIT} USD")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        """Validate payment method is supported."""
        if v not in PAYMENT_METHODS:
            raise ValueError(
                f"Payment method must be one of: {', '.join(PAYMENT_METHODS)}"
            )
        return v

    @field_validator("delivery_method")
    @classmethod
    def validate_delivery_method(cls, v: str) -> str:
        """Validate delivery method is supported."""
        if v not in DELIVERY_METHODS:
            raise ValueError(
                f"Delivery method must be one of: {', '.join(DELIVERY_METHODS)}"
            )
        return v

    model_config = {"frozen": True}


class TransferLimits(BaseModel):
    """User transfer limits tracking."""

    daily_limit: float = DAILY_LIMIT
    monthly_limit: float = MONTHLY_LIMIT
    semester_limit: float = SEMESTER_LIMIT

    daily_used: float = 0.0
    monthly_used: float = 0.0
    semester_used: float = 0.0

    @computed_field
    @property
    def daily_remaining(self) -> float:
        """Calculate remaining daily limit."""
        return self.daily_limit - self.daily_used

    @computed_field
    @property
    def monthly_remaining(self) -> float:
        """Calculate remaining monthly limit."""
        return self.monthly_limit - self.monthly_used

    @computed_field
    @property
    def semester_remaining(self) -> float:
        """Calculate remaining semester limit."""
        return self.semester_limit - self.semester_used

    def can_transfer(self, amount: float) -> tuple[bool, Optional[str]]:
        """Check if transfer amount is within all limits.

        Args:
            amount: Transfer amount to validate

        Returns:
            Tuple of (can_transfer: bool, reason: Optional[str])
            If can_transfer is False, reason explains which limit was exceeded
        """
        if amount > self.daily_remaining:
            return (
                False,
                f"Transfer would exceed daily limit. Remaining: ${self.daily_remaining:.2f} USD",
            )

        if amount > self.monthly_remaining:
            return (
                False,
                f"Transfer would exceed monthly limit. Remaining: ${self.monthly_remaining:.2f} USD",
            )

        if amount > self.semester_remaining:
            return (
                False,
                f"Transfer would exceed semester limit. Remaining: ${self.semester_remaining:.2f} USD",
            )

        return (True, None)

    def add_transfer(self, amount: float) -> None:
        """Add transfer amount to usage tracking.

        Args:
            amount: Transfer amount to add
        """
        self.daily_used += amount
        self.monthly_used += amount
        self.semester_used += amount
