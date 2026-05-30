# Working with mock transaction data

## Overview
`backend/data/mock_generator.py` produces deterministic mock transactions spanning the last 12 months.
The data is designed to demonstrate normal utility payments, a fraud ring, and merchant-specific views.

## How to run the generator
- From the repository root, run: `python backend/data/mock_generator.py`
- Optional output location: `--output /path/to/mock_transactions.json`
- Optional merchant view: `--merchant-id 9800000000` (prints the merchant-specific view to stdout)

By default, the generator writes `backend/data/mock_transactions.json`.

## Base transaction schema
Each transaction contains:
- `transaction_id` (uuid string)
- `initiating_merchant_id`
- `initiating_merchant_name`
- `receiving_merchant_id`
- `receiving_merchant_name`
- `transaction_amount`
- `transaction_date` (ISO `YYYY-MM-DD`)

## Merchant view schema
When you retrieve transactions by merchant id (via `get_transactions_by_merchant` or `--merchant-id`):
- `merchant_id`
- `merchant_name`
- `collaborating_merchant_id`
- `collaborating_merchant_name`
- `collaborating_merchant` (combined display label)
- `transaction_type` (`paid` or `received`)
- `transaction_amount`
- `transaction_date`

## Scenario details baked into the data
- **9800000000 (Sajilo Kirana)** pays monthly utility bills with growing amounts.
- **9800000001, 9800000002, 9800000003** form a circular fraud ring with equal-amount transactions.
- **9800000004 (NEA), 9800000005 (KUKL), 9800000006 (Internet)** only appear as receivers.

## Using the data in code
- Import `generate_transactions` to get the base array of transactions.
- Import `get_transactions_by_merchant` to build the merchant-centric view needed by the UI or analytics.
