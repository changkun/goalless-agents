# 💰 Personal Finance Tracker

A lightweight command-line tool to track your expenses and income, categorize spending, and visualize your financial insights.

## Features

- ✅ Track expenses with categories and descriptions
- ✅ Record income from various sources
- ✅ List recent transactions
- ✅ View financial summaries with visual spending breakdowns
- ✅ Filter by month or transaction type
- ✅ Simple JSON-based storage in your home directory

## Installation

```bash
chmod +x finance_tracker.py
# Optional: create an alias in your shell config
alias finance='python3 /workspace/finance_tracker.py'
```

## Usage

### Add an Expense
```bash
./finance_tracker.py add-expense 45.99 groceries "Weekly shopping at Whole Foods"
./finance_tracker.py add-expense 1200 rent "April rent payment" --date 2026-04-01
./finance_tracker.py add-expense 89.50 entertainment "Concert tickets"
```

### Add Income
```bash
./finance_tracker.py add-income 3000 salary
./finance_tracker.py add-income 500 freelance "Website project" --date 2026-04-15
```

### List Transactions
```bash
# Show last 10 transactions
./finance_tracker.py list

# Show last 20 transactions
./finance_tracker.py list --limit 20

# Show only expenses
./finance_tracker.py list --type expense

# Show only income
./finance_tracker.py list --type income
```

### View Summary
```bash
# Overall summary
./finance_tracker.py summary

# Summary for specific month
./finance_tracker.py summary --month 2026-04
```

### Delete a Transaction
```bash
./finance_tracker.py delete 5
```

## Example Output

```
💰 Financial Summary for 2026-04
==================================================
Total Income:    $     3500.00
Total Expenses:  $     2156.49
Net:             $     1343.51
Status:          🟢 Surplus

📊 Spending by Category
--------------------------------------------------
rent            $  1200.00 ( 55.6%) ██████████████████████████████
groceries       $   445.99 ( 20.7%) ███████████████
entertainment   $   289.50 ( 13.4%) ███████████
utilities       $   150.00 (  7.0%) █████
coffee          $    71.00 (  3.3%) ███
```

## Data Storage

All data is stored in `~/.finance_tracker.json` as a simple JSON file. You can back it up, edit it manually, or migrate it as needed.

## Tips

- Use consistent category names (e.g., "groceries" not "Groceries" or "grocery")
- Add detailed descriptions to remember what each expense was for
- Review your monthly summary to identify spending patterns
- Set up a shell alias for quick access
