"""Test Send Money Agent."""

import pytest
from send_money_agent.agent import create_agent


def test_create_agent():
    """Test agent creation."""
    agent = create_agent()

    assert agent is not None
    assert agent.name == "send_money_agent"
    assert agent.model == "gemini-2.5-flash-lite"


def test_agent_has_all_tools():
    """Test agent has all required tools."""
    agent = create_agent()

    tool_names = [
        tool.__name__ if hasattr(tool, "__name__") else str(tool)
        for tool in agent.tools
    ]

    # Should have 6 tools: 5 state update + 1 transfer
    required_tools = [
        "set_country",
        "set_amount",
        "set_beneficiary",
        "set_payment_method",
        "set_delivery_method",
        "transfer_money",
    ]

    for required in required_tools:
        assert any(required in str(name) for name in tool_names), f"Missing tool: {required}"


def test_agent_has_instruction():
    """Test agent has proper instruction."""
    agent = create_agent()

    # Check if instruction is callable (InstructionProvider) or string
    assert agent.instruction is not None

    # If it's a string, check it contains key phrases
    if isinstance(agent.instruction, str):
        instruction_lower = agent.instruction.lower()
        assert "transfer" in instruction_lower or "money" in instruction_lower
