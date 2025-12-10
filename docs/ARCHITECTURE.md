# Architecture Overview

## System Design

The Send Money Agent is built with a simple, focused architecture using Google's Agent Development Kit (ADK):

```
User (WhatsApp) → LlmAgent → State Management → Tools → Transfer Execution
                       ↓
                 Transaction History
                 Limit Validation
```

## Key Components

### 1. Agent (`agent.py`)

The core LlmAgent configured with:
- **Model**: Gemini 2.5 Flash Lite (optimized for speed)
- **Instruction**: Comprehensive prompt with conversational guidelines
- **Tools**: 6 ADK tools for state management and transfer execution
- **State Templating**: Uses `{field?}` syntax to track collected information

### 2. Data Models (`models.py`)

Pydantic v2 models for validation:

- **Beneficiary**: First name, last name, computed full_name
- **Transaction**: Complete transfer record with validation for country, amount, methods
- **TransferLimits**: Daily/monthly/semester limit tracking with remaining calculations

Constants defined:
- Supported countries (6 Latin American countries)
- Payment methods (credit_card, debit_card, bank_transfer)
- Delivery methods (digital_wallet, bank_account)
- Limit values ($1,500 daily, $3,000 monthly, $18,000 semester)

### 3. State Update Tools (`tools.py`)

Five tools for updating conversation state:

- `set_country(country)` - Validates and normalizes country names
- `set_amount(amount)` - Validates minimum amount ($0.50)
- `set_beneficiary(firstname, lastname)` - Validates and stores names
- `set_payment_method(payment_method)` - Validates payment method
- `set_delivery_method(delivery_method)` - Validates delivery method

Each tool:
- Accepts ToolContext with state access
- Validates input against supported options
- Updates tool_context.state directly
- Returns structured response with success status

### 4. Transfer Execution (`tools.py`)

Primary tool for executing transfers:

- `transfer_money(...)` - Requires all 6 parameters
- Validates all fields using Pydantic models
- Generates unique confirmation code
- Returns transfer details or error message

**Mock Implementation**: Generates TXN-XXXXXXXX confirmation codes without actual payment processing.

### 5. Transaction History (`history.py`)

CSV-based mock database:

- **TransactionHistory**: Loads and queries CSV file
- **find_beneficiary_history()**: Case-insensitive name matching
- Returns most recent transactions first
- Used for suggesting previous transfer details

### 6. Limits Tracking (`limits.py`)

Real datetime-based limit validation:

- **calculate_period_usage()**: Sums amounts for daily/monthly/semester periods
- **LimitsTracker**: Validates transfer amounts against current usage
- Returns detailed error messages with remaining amounts

## State Management

ADK's native session state is used (no custom abstractions):

```python
tool_context.state = {
    "country": "Colombia",
    "amount": 150.0,
    "beneficiary_firstname": "John",
    "beneficiary_lastname": "Matthews",
    "payment_method": "credit_card",
    "delivery_method": "digital_wallet",
}
```

The agent tracks state using templating syntax in instructions:
```
Country: {country?}
Amount: {amount?}
```

## Conversation Flow

1. **Information Collection**:
   - Agent asks for one piece at a time
   - Calls state update tool immediately when user provides info
   - Confirms inline with next question

2. **History Lookup**:
   - When beneficiary name is ambiguous, lookup previous transfers
   - Suggest details from most recent transaction
   - User confirms or provides corrections

3. **Limit Validation**:
   - When amount is set, validate against limits
   - If exceeded, explain remaining balance
   - Allow user to adjust amount

4. **Corrections**:
   - State update tools can be called multiple times
   - Each call overwrites previous value
   - Agent acknowledges correction naturally

5. **Final Confirmation**:
   - Agent summarizes all details
   - Waits for explicit confirmation
   - Calls transfer_money with all parameters

6. **Transfer Execution**:
   - Pydantic validates all fields
   - Generate confirmation code
   - Return success or detailed error

## Why This Architecture?

**Simplicity**: No custom state management, no complex abstractions
**Reliability**: Pydantic validation at every step
**Flexibility**: State update tools enable corrections
**Testability**: Each component has clear responsibilities
**Scalability**: Easy to add new countries, methods, or features

## Production Considerations

Current implementation is mock/demonstration. For production:

1. **Database**: Replace CSV with PostgreSQL or Cloud Spanner
2. **Payment Integration**: Connect real payment APIs
3. **Session Storage**: Use persistent session service (not in-memory)
4. **Authentication**: Integrate WhatsApp user verification
5. **Monitoring**: Add telemetry and logging
6. **Rate Limiting**: Implement anti-fraud measures
7. **Compliance**: Add KYC/AML validation

See ADK documentation for production deployment: https://google.github.io/adk-docs/
