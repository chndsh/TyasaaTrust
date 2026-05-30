# Alternative Behavioral Proxies for Credit Signals

## Goal
Translate non-traditional data (utility payment consistency, airtime top-ups, cash-flow seasonality) into predictive credit signals while preserving privacy and fairness.

## Recommended Project File Structure

Suggested repository layout for this work (create under your project root):

- data/
  - raw/                  # raw ingestions (S3, vendor dumps)
  - staged/               # cleaned, normalized tables
  - synthetic/            # generated synthetic datasets for testing
- src/
  - ingestion/            # connectors, anonymization pipelines
    - electricity.py
    - water.py
    - airtime.py
  - features/             # feature engineering code
    - payments_consistency.py
    - topup_patterns.py
    - seasonality.py
  - models/               # training & scoring pipelines
    - train.py
    - predict.py
  - evaluation/           # metrics, backtests, fairness checks
    - metrics.py
    - bias_audit.py
  - utils/
    - privacy.py          # hashing, tokenization, k-anonymity helpers
    - schema.py
- docs/
  - alt_behavioral_proxies.md
  - alt_behavioral_prompts.md
- notebooks/              # EDA, prototyping notebooks
- infra/                  # deployment manifests, monitoring


## Data Sources & Minimal Schema

- Utility payments (per household/account):
  - account_id (hashed)
  - provider (electricity|water|internet)
  - billing_period_start, billing_period_end
  - billed_amount
  - payment_date
  - payment_amount
  - payment_method

- Airtime / Top-ups (per phone/account):
  - account_id (hashed)
  - timestamp
  - topup_amount
  - vendor

- External calendar / agriculture seasonality
  - region_id
  - crop_calendar (planting, harvest windows)


## Data Privacy & Compliance Checklist
- Collect only necessary fields; avoid PII when possible.
- Hash or pseudonymize `account_id` at ingestion using a salted, secret key.
- Store raw PII separately with strict access controls if needed.
- Maintain an audit log for data access and transformations.
- Apply differential privacy or k-anonymity for any released aggregates.


## Feature Engineering Patterns

1. Payment Consistency Features
   - on_time_ratio: fraction of payments within X days of due date
   - std_interpayment_days: standard deviation of days between payments
   - missed_count: number of missed payments in window
   - payment_amount_cv: coefficient of variation of payment amounts

2. Payment Recency & Momentum
   - days_since_last_payment
   - trend_slope: slope of payment amounts over last N periods

3. Top-up Behavioral Features
   - topup_freq_per_month
   - median_topup_amount
   - large_topup_ratio: fraction of topups > p95
   - burstiness: entropy or Gini of topup interarrival times

4. Cash-flow Seasonality
   - seasonal_amplitude: difference between peak & trough average balances/topups
   - harvest-aligned-spike: binary or scaled feature for expected harvest months
   - rolling_monthly_variance

5. Cross-signal Fusion
   - cross_consistency_score: correlation between top-up frequency and bill payments
   - liquidity_proxy: short-term inflow/outflow balance estimate


## Labeling & Targets
- If you have credit outcomes (default / repayment): create rolling labels (30/60/90 days delinquency).
- For weak/noisy labels: consider label noise-aware losses or Bayesian label models.


## Modeling Recommendations
- Start with interpretable models: logistic regression with calibrated probabilities, or gradient-boosted trees using SHAP for explanations.
- Regularize heavily for small-signal features (L1/L2, monotonic constraints where appropriate).
- Use temporal cross-validation (time-based splits) to avoid leakage.


## Evaluation & Monitoring
- Metrics: AUC, Precision@K, calibration (Brier), lift curves, and business KPIs (loss given default, expected revenue).
- Backtest across seasons to ensure model robustness to harvest cycles.
- Fairness checks: parity of false-positive/negative rates across regions/demographics when those are available.
- Drift detection: track feature distribution drift and performance decay.


## Explainability & Operationalization
- Compute per-account explanations (SHAP) for onboarding and dispute handling.
- Expose model confidence & data-quality flags with each score.
- Runtime scoring: implement a feature store or lightweight scoring service that fetches precomputed features for low-latency decisions.


## Quick Implementation Checklist
- Define ingestion contracts with vendors (fields, cadence, delivery).
- Build salted hashing and retention rules in `src/ingestion`.
- Implement feature transforms in `src/features` with unit tests.
- Train models with time-split CV and store artifacts in `models/`.
- Deploy scoring endpoint and add monitoring/alerts for drift and anomalies.

---
Last updated: 2026-05-30
