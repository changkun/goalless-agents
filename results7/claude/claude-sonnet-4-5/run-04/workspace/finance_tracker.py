#!/usr/bin/env python3
"""
Personal Finance Tracker - Track expenses, categorize spending, and visualize insights
"""
import json
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Optional


DATA_FILE = Path.home() / ".finance_tracker.json"


def load_data() -> List[Dict]:
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []


def save_data(data: List[Dict]):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_expense(amount: float, category: str, description: str, date: Optional[str] = None):
    data = load_data()
    expense = {
        'id': len(data) + 1,
        'amount': amount,
        'category': category,
        'description': description,
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'type': 'expense'
    }
    data.append(expense)
    save_data(data)
    print(f"✅ Added expense: ${amount:.2f} - {category} - {description}")


def add_income(amount: float, source: str, date: Optional[str] = None):
    data = load_data()
    income = {
        'id': len(data) + 1,
        'amount': amount,
        'source': source,
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'type': 'income'
    }
    data.append(income)
    save_data(data)
    print(f"✅ Added income: ${amount:.2f} - {source}")


def list_transactions(limit: int = 10, transaction_type: Optional[str] = None):
    data = load_data()
    if transaction_type:
        data = [t for t in data if t['type'] == transaction_type]

    if not data:
        print("No transactions found.")
        return

    print(f"\n{'ID':<5} {'Date':<12} {'Type':<8} {'Amount':<10} {'Category/Source':<20} {'Description'}")
    print("-" * 90)

    for transaction in sorted(data, key=lambda x: x['date'], reverse=True)[:limit]:
        tid = transaction['id']
        date = transaction['date']
        ttype = transaction['type']
        amount = transaction['amount']

        if ttype == 'expense':
            cat_src = transaction['category']
            desc = transaction.get('description', '')
            print(f"{tid:<5} {date:<12} {ttype:<8} ${amount:<9.2f} {cat_src:<20} {desc}")
        else:
            source = transaction['source']
            print(f"{tid:<5} {date:<12} {ttype:<8} ${amount:<9.2f} {source:<20}")


def show_summary(month: Optional[str] = None):
    data = load_data()

    if month:
        data = [t for t in data if t['date'].startswith(month)]
        period = f"for {month}"
    else:
        period = "overall"

    if not data:
        print(f"No transactions found {period}.")
        return

    total_income = sum(t['amount'] for t in data if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in data if t['type'] == 'expense')
    net = total_income - total_expenses

    category_totals = defaultdict(float)
    for t in data:
        if t['type'] == 'expense':
            category_totals[t['category']] += t['amount']

    print(f"\n💰 Financial Summary {period}")
    print("=" * 50)
    print(f"Total Income:    ${total_income:>12.2f}")
    print(f"Total Expenses:  ${total_expenses:>12.2f}")
    print(f"Net:             ${net:>12.2f}")
    print(f"Status:          {'🟢 Surplus' if net >= 0 else '🔴 Deficit'}")

    if category_totals:
        print(f"\n📊 Spending by Category")
        print("-" * 50)
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

        max_amount = max(category_totals.values())
        for category, amount in sorted_categories:
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            bar_length = int((amount / max_amount) * 30) if max_amount > 0 else 0
            bar = "█" * bar_length
            print(f"{category:<15} ${amount:>9.2f} ({percentage:>5.1f}%) {bar}")


def delete_transaction(transaction_id: int):
    data = load_data()
    original_length = len(data)
    data = [t for t in data if t['id'] != transaction_id]

    if len(data) < original_length:
        save_data(data)
        print(f"✅ Deleted transaction #{transaction_id}")
    else:
        print(f"❌ Transaction #{transaction_id} not found")


def main():
    parser = argparse.ArgumentParser(
        description="Personal Finance Tracker - Manage your expenses and income",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add-expense 45.99 groceries "Weekly shopping at Whole Foods"
  %(prog)s add-income 3000 salary
  %(prog)s list
  %(prog)s summary
  %(prog)s summary --month 2026-04
  %(prog)s delete 5
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add expense
    expense_parser = subparsers.add_parser('add-expense', help='Add a new expense')
    expense_parser.add_argument('amount', type=float, help='Amount spent')
    expense_parser.add_argument('category', help='Category (e.g., groceries, rent, entertainment)')
    expense_parser.add_argument('description', help='Description of the expense')
    expense_parser.add_argument('--date', help='Date (YYYY-MM-DD, defaults to today)')

    # Add income
    income_parser = subparsers.add_parser('add-income', help='Add income')
    income_parser.add_argument('amount', type=float, help='Amount received')
    income_parser.add_argument('source', help='Source of income (e.g., salary, freelance)')
    income_parser.add_argument('--date', help='Date (YYYY-MM-DD, defaults to today)')

    # List transactions
    list_parser = subparsers.add_parser('list', help='List recent transactions')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of transactions to show')
    list_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')

    # Summary
    summary_parser = subparsers.add_parser('summary', help='Show financial summary')
    summary_parser.add_argument('--month', help='Filter by month (YYYY-MM)')

    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete a transaction')
    delete_parser.add_argument('id', type=int, help='Transaction ID to delete')

    args = parser.parse_args()

    if args.command == 'add-expense':
        add_expense(args.amount, args.category, args.description, args.date)
    elif args.command == 'add-income':
        add_income(args.amount, args.source, args.date)
    elif args.command == 'list':
        list_transactions(args.limit, args.type)
    elif args.command == 'summary':
        show_summary(args.month)
    elif args.command == 'delete':
        delete_transaction(args.id)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
