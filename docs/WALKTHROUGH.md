# Persistence and User Simulation Walkthrough

We have implemented persistent transaction history and a user identification system.

## New Features

### 1. Permanent Storage
- All transactions are now saved to `local_data/transactions.csv`.
- This file persists across agent restarts.
- **Note**: The initial demo data is committed to the repository.

### 2. Login Flow
- The agent now **requires** a phone number at the start of every session.
- You can use any phone number to create a new user profile.

### 3. "Major Carlos" Demo Profile
- I've seeded a demo user: **"Major Carlos"**.
- Phone Number: `+15550001111`
- He comes with a pre-populated history of 3 transactions.

## How to Test

### Step 1: Run the Agent
```bash
uv run adk run send_money_agent
```

### Step 2: Login as Major Carlos
When the agent asks for your phone number, type:
`+15550001111`
(Or just say "Major Carlos" - the agent might recognize it if you prompt it, but typing the number or saying "I am Major Carlos (phone +15550001111)" is safest).

**Expected Output:**
> "Welcome back, Major Carlos! Your daily limit remaining is $1200.00..."

### Step 3: Verify Persistence
1. Make a transfer as Major Carlos.
2. Exit the agent (`Ctrl+C`).
3. Restart the agent.
4. Login as `+15550001111` again.
5. Your limits should be lower, reflecting the transfer you just made!

## Technical Changes
- **`history.py`**: Now reads/writes to `local_data/`.
- **`tools.py`**: Added `set_phone_number` tool for login and limits checking.
- **`agent.py`**: Updated instructions to enforce the login step.
