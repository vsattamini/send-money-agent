"""Demo script showcasing Send Money Agent capabilities."""

from datetime import datetime
from send_money_agent.models import Beneficiary, Transaction
from send_money_agent.history import TransactionHistory, find_beneficiary_history
from send_money_agent.limits import LimitsTracker
from send_money_agent.tools import (
    set_country,
    set_amount,
    set_beneficiary,
    set_payment_method,
    set_delivery_method,
    transfer_money,
)
from send_money_agent.agent import create_agent


def demo_models():
    """Demonstrate Pydantic models."""
    print("\n=== Demo 1: Pydantic Data Models ===\n")

    # Create beneficiary
    beneficiary = Beneficiary(firstname="John", lastname="Matthews")
    print(f"Beneficiary: {beneficiary.full_name}")

    # Create transaction
    transaction = Transaction(
        beneficiary=beneficiary,
        country="Colombia",
        amount=150.0,
        payment_method="credit_card",
        delivery_method="digital_wallet",
        timestamp=datetime.now(),
    )
    print(f"Transaction: ${transaction.amount} to {transaction.beneficiary.full_name} in {transaction.country}")


def demo_history_lookup():
    """Demonstrate transaction history lookup."""
    print("\n=== Demo 2: Transaction History Lookup ===\n")

    history = TransactionHistory()

    # Find John Matthews in history
    matches = find_beneficiary_history(
        history, "+1234567890", firstname="John", lastname="Matthews"
    )

    if matches:
        print(f"Found {len(matches)} previous transactions to John Matthews:")
        for match in matches:
            print(f"  - ${match.amount} to {match.country} via {match.delivery_method}")
            print(f"    Date: {match.timestamp.strftime('%Y-%m-%d')}")
    else:
        print("No previous transactions found")


def demo_limits_tracking():
    """Demonstrate transfer limits tracking."""
    print("\n=== Demo 3: Transfer Limits Tracking ===\n")

    # Create mock transaction history
    from datetime import timedelta
    now = datetime.now()

    transactions = [
        Transaction(
            beneficiary=Beneficiary(firstname="John", lastname="Doe"),
            country="México",
            amount=1000.0,
            payment_method="credit_card",
            delivery_method="digital_wallet",
            timestamp=now - timedelta(hours=5),
        ),
    ]

    tracker = LimitsTracker(transactions, now)
    limits = tracker.get_current_limits()

    print(f"Current Usage:")
    print(f"  Daily: ${limits.daily_used:.2f} / ${limits.daily_limit:.2f} (${limits.daily_remaining:.2f} remaining)")
    print(f"  Monthly: ${limits.monthly_used:.2f} / ${limits.monthly_limit:.2f} (${limits.monthly_remaining:.2f} remaining)")
    print(f"  Semester: ${limits.semester_used:.2f} / ${limits.semester_limit:.2f} (${limits.semester_remaining:.2f} remaining)")

    # Check if can transfer $400
    can_transfer, reason = tracker.check_limits(400.0)
    print(f"\nCan transfer $400? {can_transfer}")
    if not can_transfer:
        print(f"  Reason: {reason}")


def demo_tools():
    """Demonstrate ADK tools."""
    print("\n=== Demo 4: ADK Tools ===\n")

    # Mock tool context
    class MockContext:
        def __init__(self):
            self.state = {"phone_number": "+1234567890"}

    context = MockContext()

    # Set country
    result = set_country(context, "Colombia")
    print(f"set_country: {result['message']}")

    # Set amount
    result = set_amount(context, 150.0)
    print(f"set_amount: {result['message']}")

    # Set beneficiary
    result = set_beneficiary(context, "John", "Matthews")
    print(f"set_beneficiary: {result['message']}")

    # Set payment method
    result = set_payment_method(context, "credit_card")
    print(f"set_payment_method: {result['message']}")

    # Set delivery method
    result = set_delivery_method(context, "digital_wallet")
    print(f"set_delivery_method: {result['message']}")

    # Execute transfer
    result = transfer_money(
        tool_context=context,
        beneficiary_firstname="John",
        beneficiary_lastname="Matthews",
        country="Colombia",
        amount=150.0,
        payment_method="credit_card",
        delivery_method="digital_wallet",
    )
    print(f"\ntransfer_money: {result['message']}")


def demo_agent():
    """Demonstrate agent configuration."""
    print("\n=== Demo 5: Agent Configuration ===\n")

    agent = create_agent()

    print(f"Agent Name: {agent.name}")
    print(f"Model: {agent.model}")
    print(f"Number of Tools: {len(agent.tools)}")
    print(f"Tool Names: {', '.join([t.__name__ for t in agent.tools])}")


def main():
    """Run all demos."""
    print("=" * 60)
    print("SEND MONEY AGENT - DEMONSTRATION")
    print("=" * 60)

    demo_models()
    demo_history_lookup()
    demo_limits_tracking()
    demo_tools()
    demo_agent()

    print("\n" + "=" * 60)
    print("Demo complete! Run agent with: uv run adk run send_money_agent")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
