#!/usr/bin/env python3
"""A terminal-based expense tracker with category summaries and filtering."""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_FILE = Path.home() / ".expenses.json"

CATEGORIES = [
    "food", "transport", "entertainment", "utilities",
    "shopping", "health", "education", "other"
]

def load_expenses():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

def add_expense(amount, category, description):
    if category not in CATEGORIES:
        print(f"Invalid category. Choose from: {', '.join(CATEGORIES)}")
        return

    expenses = load_expenses()
    expense = {
        "id": len(expenses) + 1,
        "amount": round(float(amount), 2),
        "category": category,
        "description": description,
        "date": datetime.now().isoformat()
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"Added: ${expense['amount']:.2f} for {category} - {description}")

def list_expenses(category=None, days=None):
    expenses = load_expenses()

    if days:
        cutoff = datetime.now() - timedelta(days=days)
        expenses = [e for e in expenses if datetime.fromisoformat(e["date"]) >= cutoff]

    if category:
        expenses = [e for e in expenses if e["category"] == category]

    if not expenses:
        print("No expenses found.")
        return

    print(f"\n{'ID':<4} {'Date':<12} {'Category':<14} {'Amount':>10}  Description")
    print("-" * 70)

    total = 0
    for e in expenses:
        date = datetime.fromisoformat(e["date"]).strftime("%Y-%m-%d")
        print(f"{e['id']:<4} {date:<12} {e['category']:<14} ${e['amount']:>9.2f}  {e['description']}")
        total += e["amount"]

    print("-" * 70)
    print(f"{'Total:':<32} ${total:>9.2f}")

def summary(days=None):
    expenses = load_expenses()

    if days:
        cutoff = datetime.now() - timedelta(days=days)
        expenses = [e for e in expenses if datetime.fromisoformat(e["date"]) >= cutoff]

    if not expenses:
        print("No expenses found.")
        return

    by_category = defaultdict(float)
    for e in expenses:
        by_category[e["category"]] += e["amount"]

    total = sum(by_category.values())

    period = f"last {days} days" if days else "all time"
    print(f"\nExpense Summary ({period})")
    print("-" * 40)

    for cat in sorted(by_category.keys(), key=lambda c: by_category[c], reverse=True):
        amount = by_category[cat]
        pct = (amount / total) * 100
        bar = "█" * int(pct / 5)
        print(f"{cat:<14} ${amount:>9.2f} ({pct:>5.1f}%) {bar}")

    print("-" * 40)
    print(f"{'Total':<14} ${total:>9.2f}")

def delete_expense(expense_id):
    expenses = load_expenses()
    original_len = len(expenses)
    expenses = [e for e in expenses if e["id"] != expense_id]

    if len(expenses) == original_len:
        print(f"Expense #{expense_id} not found.")
        return

    save_expenses(expenses)
    print(f"Deleted expense #{expense_id}")

def main():
    parser = argparse.ArgumentParser(description="Track your expenses from the terminal")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("amount", type=float, help="Amount spent")
    add_parser.add_argument("category", choices=CATEGORIES, help="Expense category")
    add_parser.add_argument("description", help="Description of expense")

    list_parser = subparsers.add_parser("list", help="List expenses")
    list_parser.add_argument("-c", "--category", choices=CATEGORIES, help="Filter by category")
    list_parser.add_argument("-d", "--days", type=int, help="Show only last N days")

    summary_parser = subparsers.add_parser("summary", help="Show expense summary by category")
    summary_parser.add_argument("-d", "--days", type=int, help="Summarize only last N days")

    delete_parser = subparsers.add_parser("delete", help="Delete an expense")
    delete_parser.add_argument("id", type=int, help="Expense ID to delete")

    subparsers.add_parser("categories", help="List available categories")

    args = parser.parse_args()

    if args.command == "add":
        add_expense(args.amount, args.category, args.description)
    elif args.command == "list":
        list_expenses(args.category, args.days)
    elif args.command == "summary":
        summary(args.days)
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "categories":
        print("Available categories:", ", ".join(CATEGORIES))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
