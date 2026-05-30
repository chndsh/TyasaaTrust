"""Generate mock transaction data for local development."""

from __future__ import annotations

import argparse
import calendar
import json
import os
import sys
from datetime import date
from typing import Any, Dict, List
from uuid import uuid4

# Compute the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if not os.path.exists(os.path.join(project_root, "backend")):
    if project_root in sys.path:
        sys.path.remove(project_root)
    project_root = os.path.dirname(project_root)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

MERCHANTS: Dict[str, str] = {
    "9800000000": "Sajilo Kirana",
    "9800000001": "Himal Wholesale",
    "9800000002": "Bhaktapur Supplies",
    "9800000003": "Thamel Traders",
    "9800000004": "NEA",
    "9800000005": "KUKL",
    "9800000006": "Internet",
}

UTILITY_MERCHANTS = ("9800000004", "9800000005", "9800000006")
FRAUD_RING = ("9800000001", "9800000002", "9800000003")

UTILITY_BASE_AMOUNTS = {
    "9800000004": 1600,
    "9800000005": 1100,
    "9800000006": 1800,
}

UTILITY_MONTHLY_INCREASE = {
    "9800000004": 120,
    "9800000005": 90,
    "9800000006": 150,
}

UTILITY_PAYMENT_DAYS = {
    "9800000004": 5,
    "9800000005": 12,
    "9800000006": 20,
}

FRAUD_RING_MONTH_OFFSETS = (1, 4, 7, 10)
FRAUD_RING_AMOUNTS = (25000, 25500, 26000, 26500)


def shift_month(anchor: date, months_back: int) -> date:
    year = anchor.year
    month = anchor.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    day = min(anchor.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def month_anchors(reference_date: date | None = None, months: int = 12) -> List[date]:
    anchor = (reference_date or date.today()).replace(day=15)
    return [shift_month(anchor, offset) for offset in range(months - 1, -1, -1)]


def clamp_day(year: int, month: int, day: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


def build_transaction(
    initiating_id: str,
    receiving_id: str,
    amount: float,
    transaction_date: date,
) -> Dict[str, Any]:
    return {
        "transaction_id": str(uuid4()),
        "initiating_merchant_id": initiating_id,
        "initiating_merchant_name": MERCHANTS[initiating_id],
        "receiving_merchant_id": receiving_id,
        "receiving_merchant_name": MERCHANTS[receiving_id],
        "transaction_amount": round(amount, 2),
        "transaction_date": transaction_date.isoformat(),
    }


def generate_utility_payments(months: List[date]) -> List[Dict[str, Any]]:
    transactions: List[Dict[str, Any]] = []
    for index, anchor in enumerate(months):
        for merchant_id in UTILITY_MERCHANTS:
            payment_day = UTILITY_PAYMENT_DAYS[merchant_id]
            tx_date = clamp_day(anchor.year, anchor.month, payment_day)
            amount = UTILITY_BASE_AMOUNTS[merchant_id] + (
                UTILITY_MONTHLY_INCREASE[merchant_id] * index
            )
            transactions.append(
                build_transaction("9800000000", merchant_id, amount, tx_date)
            )
    return transactions


def generate_fraud_ring(months: List[date]) -> List[Dict[str, Any]]:
    transactions: List[Dict[str, Any]] = []
    for index, month_offset in enumerate(FRAUD_RING_MONTH_OFFSETS):
        anchor = months[month_offset]
        last_day = calendar.monthrange(anchor.year, anchor.month)[1]
        start_day = min(10, last_day - 2)
        amount = FRAUD_RING_AMOUNTS[index]
        day_one = clamp_day(anchor.year, anchor.month, start_day)
        day_two = clamp_day(anchor.year, anchor.month, start_day + 1)
        day_three = clamp_day(anchor.year, anchor.month, start_day + 2)
        transactions.extend(
            [
                build_transaction(FRAUD_RING[0], FRAUD_RING[1], amount, day_one),
                build_transaction(FRAUD_RING[1], FRAUD_RING[2], amount, day_two),
                build_transaction(FRAUD_RING[2], FRAUD_RING[0], amount, day_three),
            ]
        )
    return transactions


def generate_transactions(reference_date: date | None = None) -> List[Dict[str, Any]]:
    months = month_anchors(reference_date=reference_date, months=12)
    transactions = generate_utility_payments(months)
    transactions.extend(generate_fraud_ring(months))
    transactions.sort(key=lambda tx: tx["transaction_date"])
    return transactions


def get_transactions_by_merchant(
    transactions: List[Dict[str, Any]],
    merchant_id: str,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for transaction in transactions:
        if merchant_id == transaction["initiating_merchant_id"]:
            collaborating_id = transaction["receiving_merchant_id"]
            collaborating_name = transaction["receiving_merchant_name"]
            tx_type = "paid"
            merchant_name = transaction["initiating_merchant_name"]
        elif merchant_id == transaction["receiving_merchant_id"]:
            collaborating_id = transaction["initiating_merchant_id"]
            collaborating_name = transaction["initiating_merchant_name"]
            tx_type = "received"
            merchant_name = transaction["receiving_merchant_name"]
        else:
            continue
        results.append(
            {
                "merchant_id": merchant_id,
                "merchant_name": merchant_name,
                "collaborating_merchant_id": collaborating_id,
                "collaborating_merchant_name": collaborating_name,
                "collaborating_merchant": f"{collaborating_name} ({collaborating_id})",
                "transaction_type": tx_type,
                "transaction_amount": transaction["transaction_amount"],
                "transaction_date": transaction["transaction_date"],
            }
        )
    results.sort(key=lambda tx: tx["transaction_date"])
    return results


def write_json(output_path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def main() -> None:
    data_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Generate mock transaction data.")
    parser.add_argument(
        "--output",
        default=os.path.join(data_dir, "mock_transactions.json"),
        help="Where to write the transaction list JSON file.",
    )
    parser.add_argument(
        "--merchant-id",
        help="Optional merchant id to print the merchant-specific view to stdout.",
    )
    args = parser.parse_args()

    transactions = generate_transactions()
    write_json(args.output, transactions)

    if args.merchant_id:
        merchant_view = get_transactions_by_merchant(transactions, args.merchant_id)
        print(json.dumps(merchant_view, indent=2, ensure_ascii=False))

    print(f"Generated {len(transactions)} transactions into {args.output}")


if __name__ == "__main__":
    main()
