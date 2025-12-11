# Technical Notes & Hacks

This document outlines the technical implementation details, including temporary workarounds ("hacks") and specific configurations used in the Send Money Agent.

## 1. API Rate Limit Handling (Monkey Patch)

To improve user experience during periods of high API usage or lower quota tiers, we have implemented a **monkey patch** to intercept `429 RESOURCE_EXHAUSTED` errors from the underlying Google LLM library.

-   **File**: `send_money_agent/agent.py`
-   **Implementation**: Steps 24-54
-   **Function**: `patched_generate_content_async`
-   **Behavior**:
    -   Wraps the original `google_llm.Gemini.generate_content_async` method.
    -   When a `_ResourceExhaustedError` is caught, it catches the exception.
    -   It prints a warning to `sys.stderr`.
    -   It initiates a 60-second countdown (waiting for quota bucket refill).
    -   It automatically retries the request.
-   **Why**: To prevent the agent from crashing abruptly when rate limits are hit, allowing for a smoother (albeit paused) demo experience.

## 2. Persistence Model (CSV "Database")

The agent uses a flat CSV file as a persistent data store. This is a simplification for demonstration purposes.

-   **File**: `local_data/transactions.csv`
-   **Logic**: `send_money_agent/history.py`
-   **Behavior**:
    -   The file `local_data/transactions.csv` acts as the source of truth for all transaction history.
    -   New transfers are appended to this file.
    -   Limits are calculated by reading this file at runtime.
    -   **Seed Data**: The repo includes this file pre-populated with data for "Major Carlos" (`+15550001111`) to demonstrate history lookups and limit enforcement.

## 3. Test Mocking

To ensure tests are deterministic and do not depend on the state of the local CSV file, `TransactionHistory` is mocked in the test suite.

-   **Files**: `tests/test_tools.py`, `tests/test_history.py`
-   **Library**: `unittest.mock.patch`
-   **Mechanism**: The `TransactionHistory` class is patched during tests to return fixed lists of transactions or empty lists, regardless of what is on disk. This allows testing "limit exceeded" scenarios without actually filling up a real database.

## 4. User Login Simulation

The "Login" flow is a simulation.

-   **Tool**: `set_phone_number`
-   **Mechanism**: The agent asks for a phone number. It trusts whatever input is given.
-   **Hack**: There is no SMS verification or password check. If you enter `+15550001111`, you *become* "Major Carlos".
-   **Purpose**: To demonstrate user-specific context loading (history, limits) without building a full authentication system.

## 5. Async Loop Management

The ADK framework manages the asyncio event loop. Our retrying mechanism in the monkey patch intentionally uses `await asyncio.sleep(1)` to retain non-blocking behavior within that loop, ensuring the CLI doesn't freeze completely (though it will pause output).
