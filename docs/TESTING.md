# Testing Guide

This project maintains a high standard of code quality through comprehensive testing. We use `pytest` as our testing framework.

## Quick Start

Run all tests:

```bash
pytest tests/ -v
```

## Test Structure

The `tests/` directory mirrors the structure of the application:

| Test File | Component Tested | Description |
|-----------|------------------|-------------|
| `test_models.py` | `models.py` | Validates Pydantic models (Beneficiary, Transaction, Limits) |
| `test_history.py` | `history.py` | Tests CSV loading and fuzzy beneficiary search |
| `test_limits.py` | `limits.py` | Verifies daily/monthly/semester limit calculations |
| `test_tools.py` | `tools.py` | Tests individual ADK tools (set_*, transfer_money) |
| `test_agent.py` | `agent.py` | Verifies agent configuration and instructions |
| `test_integration.py` | Integration | Tests end-to-end workflows (lookup, limits, execution) |

## Key Test Scenarios

### 1. Data Validation (Unit Tests)
- **Countries**: Verifies that only supported countries (e.g., Mexico, Colombia) are accepted.
- **Amounts**: Checks minimum ($0.50) and maximum limits.
- **Methods**: Validates payment and delivery methods against allowlists.

### 2. Logic Verification
- **Limit Tracking**: We simulate transactions with various timestamps to ensure daily, monthly, and semester limits are calculated correctly.
- **Beneficiary Search**: Tests exact matches, case-insensitive matches, and finding the most recent transaction.

### 3. Integration Workflows
- **Ambiguous Beneficiary**: Simulates the flow where a user gives a name ("John") and the system finds "John Matthews" in history.
- **Limit Exceeded**: Simulates a user trying to send more than allowed, verifying the correct error message and remaining balance are returned.
- **Full Transfer**: Verifies a complete transfer flow from data collection to confirmation code generation.

## Test Coverage

We aim for high test coverage on core business logic.

To run with coverage report (requires `pytest-cov`):

```bash
pip install pytest-cov
pytest --cov=send_money_agent tests/
```

## Mocking

- **Database**: We use `data/transaction_history.csv` as a mock database.
- **Dates**: In limit tests, we often pass specific `datetime` objects to simulate different points in time.
