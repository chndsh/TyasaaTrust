# Data Contracts - Alternative Behavioral Proxies

All staged data is stored in PostgreSQL. Hash all account identifiers before writing to the database. Use UTC timestamps for all time fields.

## Table: utilities_payments

Columns:
- account_id_hash (text)
- provider (text) - electricity, water, internet
- billing_period_start (date)
- billing_period_end (date)
- billed_amount (numeric)
- payment_date (date, nullable)
- payment_amount (numeric, nullable)
- payment_method (text, nullable)

## Table: airtime_topups

Columns:
- account_id_hash (text)
- topup_ts (timestamptz)
- topup_amount (numeric)
- vendor (text, nullable)

## Table: seasonality_calendar

Columns:
- region_id (text)
- season_label (text) - harvest, planting, off_season
- season_start_month (smallint)
- season_end_month (smallint)

## Table: behavioral_features

Columns:
- account_id_hash (text)
- as_of_date (date)
- on_time_ratio (numeric)
- utility_payment_consistency (numeric)
- std_interpayment_days (numeric)
- missed_count (int)
- payment_amount_cv (numeric)
- days_since_last_payment (int)
- topup_freq_per_month (numeric)
- median_topup_amount (numeric)
- large_topup_ratio (numeric)
- burstiness (numeric)
- recharge_variance (numeric)
- seasonal_amplitude (numeric)
- harvest_aligned_spike (numeric)
- rolling_monthly_variance (numeric)
- seasonal_recovery_score (numeric)

## Table: behavioral_scores

Columns:
- account_id_hash (text)
- as_of_date (date)
- score (numeric)
- model_version (text, nullable)
- score_details (jsonb, nullable)

## Notes
- Use salted HMAC-SHA256 for hashing account identifiers.
- Store raw PII outside these tables with stricter access controls.
- Keep a data access audit log for compliance.
