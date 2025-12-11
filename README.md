# Send Money Agent - WhatsApp Transfer Assistant

A conversational AI agent for WhatsApp-based money transfers, built with Google's Agent Development Kit (ADK).

## Features

- Conversational flow with inline confirmations
- Transaction history lookup for beneficiary suggestions
- Real-time transfer limit validation (daily/monthly/semester)
- Mock transfer execution with confirmation codes
- WhatsApp-optimized UX

## Quick Start

```bash
# Setup
pip install -e ".[dev]"

# Set API key
export GOOGLE_API_KEY="your-google-api-key"

# Run agent
uv run adk run send_money_agent
# Run agent
uv run adk run send_money_agent
```

> **Note**: If you hit the API rate limit (429 Resource Exhausted), the agent will automatically pause for 60 seconds and retry.

## New Features & Demo (Persistence)

The agent now supports persistent transaction history and user login.

**Demo Profile: "Major Carlos"**
- **Phone**: `+15550001111`
- **History**: Pre-loaded with 3 past transactions.
- **Limits**: Shows real-time limit usage based on history.

**Try it out:**
1. Run: `uv run adk run send_money_agent`
2. Enter phone: `+15550001111` (or say "I am Major Carlos")
3. Make a transfer and restart—your history is saved in `local_data/`.

See [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) for full details on persistence and simulation.

## Example Usage

```
User: Send money to John
Agent: I see you previously sent to John Matthews in Colombia via digital wallet.
       Is this the same person?
User: Yes
Agent: Great! What amount would you like to send?
User: $150
Agent: Perfect. $150 to John Matthews in Colombia. How would you like to pay?
User: Credit card
Agent: And how should John receive it?
User: Digital wallet
Agent: Let me confirm: Send $150.00 USD to John Matthews in Colombia,
       paying with credit card, delivered to digital wallet. Proceed?
User: Yes
Agent: ✅ Transfer confirmed! Confirmation code: TXN-A3F2B8E1
```

See [examples/conversations.md](examples/conversations.md) for more scenarios.

## Architecture

**Simple & Focused**:
- One primary tool: `transfer_money()`
- Five state update tools for collecting information
- ADK session state (no custom state management)
- Pydantic validation for all data
- CSV-based transaction history (mock DB)

```
User → LlmAgent → ADK State → transfer_money() → Confirmation
         ↓
   Transaction History Lookup
   Limit Validation
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_models.py -v        # Pydantic validation
pytest tests/test_limits.py -v        # Limit tracking
pytest tests/test_tools.py -v         # Tool functionality
pytest tests/test_integration.py -v   # End-to-end workflows
```

**Test Coverage**: 55+ tests covering:
- Pydantic model validation
- Transaction history lookup
- Transfer limit calculations
- Tool validation and execution
- Integration workflows

## Development

### Project Structure

```
send_money_agent/
├── agent.py          # Main LlmAgent
├── models.py         # Pydantic models
├── tools.py          # ADK tools (6 total)
├── history.py        # Transaction history
├── limits.py         # Limit tracking
tests/
├── test_models.py    # Model validation tests
├── test_history.py   # History lookup tests
├── test_limits.py    # Limit tracking tests
├── test_tools.py     # Tool tests
├── test_agent.py     # Agent configuration tests
└── test_integration.py  # End-to-end tests
examples/
├── conversations.md  # Example conversations
└── demo.py          # Runnable demo
data/
└── transaction_history.csv  # Mock database
```

### Running Demo

```bash
python examples/demo.py
```

Shows:
- Pydantic model creation
- Transaction history lookup
- Limit tracking calculations
- Tool execution
- Agent configuration

### Configuration

Update constants in `models.py`:
```python
DAILY_LIMIT = 1500.0
MONTHLY_LIMIT = 3000.0
SEMESTER_LIMIT = 18000.0
```

## Transfer Details

**Countries**: México, Guatemala, Honduras, El Salvador, República Dominicana, Colombia

**Limits**:
- Daily: $1,500 USD
- Monthly: $3,000 USD
- Semester: $18,000 USD

**Payment Methods**: Credit Card, Debit Card, Bank Transfer

**Delivery Methods**: Digital Wallet, Bank Account

## Production Deployment

**Current**: In-memory session (for development)

**Production**: Use persistent session service

```bash
# With PostgreSQL
adk web send_money_agent \
  --session_service_uri="postgresql://user:pass@host:5432/db"

# With Vertex AI
adk web send_money_agent \
  --session_service=vertexai
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Walkthrough & Persistence](docs/WALKTHROUGH.md)
- [Technical Notes & Hacks](docs/TECHNICAL_NOTES.md)
- [Example Conversations](examples/conversations.md)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK State Management](https://google.github.io/adk-docs/sessions/state/)

## Tech Stack

- **Google ADK v1.20+**: Agent framework
- **Gemini 2.5 Flash Lite**: LLM
- **Python 3.12**: Implementation
- **Pydantic v2**: Data validation
- **Pytest**: Testing

## License

Educational/demonstration project for Felix Pago interview.
