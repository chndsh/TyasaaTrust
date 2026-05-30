# Alternative Behavioral Proxies - TODO and File Guide

Scope: Part 3 (Smart Digital Footprint). This plan keeps code quality high by sequencing work, adding tests, and defining data contracts before modeling.

## Open Questions (need answers before final modeling)
- Labels: What is the target event (default, late payment, or repayment), and what window (30/60/90 days)?
- DB engine: Postgres, MySQL, SQLite, or other?
- Time coverage: how many months/years of history per signal?
- Seasonality source: do we already have region-level crop calendar data, and region mapping per account?

## Proposed File Structure
- src/
  - ingestion/
    - utilities.py
    - airtime.py
    - seasonality.py
  - features/
    - payments_consistency.py
    - topup_patterns.py
    - cashflow_seasonality.py
    - feature_registry.py
  - privacy/
    - hashing.py
    - k_anonymity.py
  - models/
    - train.py
    - predict.py
  - evaluation/
    - metrics.py
    - bias_audit.py
  - utils/
    - schema.py
    - io.py
    - google_ai.py
- docs/
  - alt_behavioral_proxies.md
  - alt_behavioral_prompts.md
  - data_contracts.md
  - alt_behavioral_todo.md
- tests/
  - test_features_payments.py
  - test_features_topups.py
  - test_seasonality.py
- db/
  - init.sql
- .env.example

## Per-File TODOs

### src/ingestion/utilities.py
- Read raw utilities data into a staging DataFrame.
- Validate required columns and types.
- Normalize timestamps to UTC.
- Use privacy.hashing for account_id hashing before DB write.
- Write to staging DB table.

### src/ingestion/airtime.py
- Read airtime top-up events.
- Validate schema, remove negative amounts, de-duplicate.
- Normalize timestamps to UTC.
- Hash account_id before DB write.
- Write to staging DB table.

### src/ingestion/seasonality.py
- Load region-level crop calendar or seasonality reference.
- Normalize windows and store in a reference DB table.

### src/features/payments_consistency.py
- Implement: on_time_ratio, std_interpayment_days, missed_count, payment_amount_cv, days_since_last_payment.
- Assume due_date = billing_period_end + 15 days (update if business rule differs).
- Add vectorized functions that work on all accounts.

### src/features/topup_patterns.py
- Implement: topup_freq_per_month, median_topup_amount, large_topup_ratio, burstiness.
- Use rolling time windows, month-bucketed metrics.

### src/features/cashflow_seasonality.py
- Implement: seasonal_amplitude, harvest_aligned_spike, rolling_monthly_variance.
- Align accounts to region crop calendar; document assumptions.

### src/features/feature_registry.py
- Central registry that returns the full feature set for training/scoring.
- Define consistent feature names and ordering.

### src/privacy/hashing.py
- Implement HMAC-SHA256 hashing with key rotation support.
- Avoid storing raw PII in staged tables.

### src/privacy/k_anonymity.py
- Utility for simple group size checks before any aggregate release.

### src/models/train.py
- Time-based split (train/valid/test).
- Train scikit-learn model (logistic regression or gradient boosting).
- Save model artifact and feature schema.

### src/models/predict.py
- Load model artifact and feature schema.
- Score new accounts from features.
- Output score with confidence flags.

### src/evaluation/metrics.py
- Compute AUC, Precision@K, Brier score, calibration.
- Provide helper to slice by region/segment.

### src/evaluation/bias_audit.py
- Compute FP/FN rates across regions.
- Summarize disparities.

### src/utils/schema.py
- Centralize schema definitions and column constants.

### src/utils/io.py
- DB read/write utilities, retry logic, and batching.

### src/utils/google_ai.py
- Config stub only: load API key from env.
- Provide placeholder client init function; no usage yet.

### docs/data_contracts.md
- Define minimal schema for utilities, topups, seasonality, and staged feature tables.
- Document hashing and retention policy.

### tests/test_features_payments.py
- Unit tests for payment consistency features with synthetic data.

### tests/test_features_topups.py
- Unit tests for topup behavior features with synthetic data.

### tests/test_seasonality.py
- Unit tests for seasonality alignment and harvest spike feature.

### db/init.sql
- Add staging tables for utilities, airtime, seasonality.
- Add feature table schema.

### .env.example
- Add GOOGLE_AI_STUDIO_API_KEY=your_key_here

## Execution Order
1) Define schemas in docs/data_contracts.md and db/init.sql
2) Implement ingestion + hashing + validation
3) Implement feature engineering + tests
4) Train baseline model (scikit-learn)
5) Add evaluation and fairness checks

## Google AI Studio Key Usage (Stub)
- Store key in .env (not committed)
- Load via src/utils/google_ai.py
- Do not log the key or include it in outputs
