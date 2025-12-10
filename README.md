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
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[dev]"

# Set API key
export GOOGLE_API_KEY="your-google-api-key"

# Run agent
uv run adk run send_money_agent/agent.py
```

## Transfer Details

**Countries:** México, Guatemala, Honduras, El Salvador, República Dominicana, Colombia

**Limits:**
- Daily: $1,500 USD
- Monthly: $3,000 USD
- Semester: $18,000 USD

**Payment Methods:** Credit Card, Debit Card, Bank Transfer

**Delivery Methods:** Digital Wallet, Bank Account
