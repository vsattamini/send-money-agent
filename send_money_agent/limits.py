"""Transfer limits tracking with real datetime calculations."""

from datetime import datetime, timedelta
from typing import List, Literal, Optional, Tuple
from send_money_agent.models import Transaction, TransferLimits


def calculate_period_usage(
    transactions: List[Transaction],
    current_time: datetime,
    period: Literal["daily", "monthly", "semester"],
) -> float:
    """Calculate total transfer amount for a time period.

    Args:
        transactions: List of transactions
        current_time: Current datetime for period calculation
        period: Time period to calculate ("daily", "monthly", "semester")

    Returns:
        Total amount transferred in the period
    """
    if period == "daily":
        cutoff = current_time - timedelta(days=1)
    elif period == "monthly":
        cutoff = current_time - timedelta(days=30)
    elif period == "semester":
        cutoff = current_time - timedelta(days=180)
    else:
        raise ValueError(f"Invalid period: {period}")

    # Sum amounts for transactions after cutoff
    total = sum(
        txn.amount for txn in transactions if txn.timestamp >= cutoff
    )

    return total


class LimitsTracker:
    """Track and validate transfer limits for a user."""

    def __init__(self, transactions: List[Transaction], current_time: Optional[datetime] = None):
        """Initialize limits tracker.

        Args:
            transactions: User's transaction history
            current_time: Current time for calculations (defaults to now)
        """
        self.transactions = transactions
        self.current_time = current_time or datetime.now()

    def get_current_limits(self) -> TransferLimits:
        """Get current transfer limits with usage calculated.

        Returns:
            TransferLimits with current usage amounts
        """
        daily_used = calculate_period_usage(
            self.transactions, self.current_time, "daily"
        )
        monthly_used = calculate_period_usage(
            self.transactions, self.current_time, "monthly"
        )
        semester_used = calculate_period_usage(
            self.transactions, self.current_time, "semester"
        )

        return TransferLimits(
            daily_used=daily_used,
            monthly_used=monthly_used,
            semester_used=semester_used,
        )

    def check_limits(self, amount: float) -> Tuple[bool, Optional[str]]:
        """Check if a transfer amount is within limits.

        Args:
            amount: Transfer amount to validate

        Returns:
            Tuple of (can_transfer, reason)
            If can_transfer is False, reason explains which limit was exceeded
        """
        limits = self.get_current_limits()
        return limits.can_transfer(amount)
