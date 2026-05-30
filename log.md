# Change Log

## 2026-05-30
- Added a deterministic mock transaction generator (`backend/data/mock_generator.py`) that creates 12 months of transactions, including utility payments and a fraud ring scenario.
- Added `workingwithmock_data.md` to document how the generator works, the schemas, and how to use the data.

### Schemas
**Transaction**
- `transaction_id`
- `initiating_merchant_id`
- `initiating_merchant_name`
- `receiving_merchant_id`
- `receiving_merchant_name`
- `transaction_amount`
- `transaction_date`

**Merchant Transaction View**
- `merchant_id`
- `merchant_name`
- `collaborating_merchant_id`
- `collaborating_merchant_name`
- `collaborating_merchant`
- `transaction_type` (`paid` or `received`)
- `transaction_amount`
- `transaction_date`
