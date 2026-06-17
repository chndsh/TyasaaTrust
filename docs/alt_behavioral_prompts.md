# Prompts for Extracting Alternative Behavioral Proxies

This file contains ready-to-use prompts you can paste into an LLM or use with teammates to generate code, analyses, vendor requests, and documentation.

## How to use
- Preface prompts with context: data availability, time window, and privacy constraints.
- Use follow-ups to request code in a specific language (Python/pandas), or to constrain outputs (max 200 lines).


## Vendor / Data Request Prompts

- "We need a daily export of utility payment events for anonymized accounts. Include: account_id (hashed with our salt), provider, billing_period_start, billing_period_end, billed_amount, payment_date, payment_amount, payment_method. Deliver as CSV with timestamps in ISO8601. Provide last 3 years and incremental daily files. Also include data dictionary and sample rows."

- "Provide a description of how your meter-to-bill mapping works and any known missingness patterns or outages. Include confidence estimates per record if available." 


## ETL / Ingestion Prompts

- "Given a CSV with columns [account_id, payment_date, payment_amount, billed_amount], produce a Python/pandas script to:
  1) Parse dates and timezone-normalize to UTC
  2) Hash `account_id` with HMAC-SHA256 using a provided secret
  3) Remove duplicates and records with negative amounts
  4) Output a Parquet partitioned by year/month
Return only the code block."

- "Generate SQL (Postgres) to upsert new payment events into a staged table and compute `days_to_due` assuming `due_date` = billing_period_end + 15 days. Ensure idempotency."


## Feature Engineering Prompts

- "Write a Python function that, given a DataFrame of payments for one account, computes these features over the past 12 months: on_time_ratio, std_interpayment_days, missed_count, payment_amount_cv, days_since_last_payment. Use pandas and document assumptions."

- "Produce a vectorized pandas implementation to compute rolling top-up frequency per month, median_topup_amount, and burstiness (entropy of interarrival bins) across all accounts. Include unit tests with synthetic data." 


## Seasonality & External Calendar Prompts

- "Given a region-level crop calendar (planting and harvest windows), write code that aligns account activity by region and computes a `harvest_aligned_spike` feature: the normalized change in topup volume during harvest months vs baseline." 


## Modeling & Training Prompts

- "Create a light-weight training pipeline in Python that:
  - Loads features from Parquet
  - Splits data by time (train/validation/test)
  - Trains a LightGBM classifier to predict 90-day delinquency
  - Outputs evaluation metrics (AUC, Precision@K) and SHAP summary plot
Return runnable code and a requirements snippet."

- "Suggest hyperparameter ranges for a LightGBM model when features include many small-magnitude behavioral proxies; explain regularization choices." 


## Evaluation, Fairness, & Explainability Prompts

- "Produce code to compute calibration (reliability) curves and Brier score per region. Also compute false positive/negative rates per region and produce a short human-readable summary of disparities." 

- "Write a script that generates per-account SHAP explanations and formats them into a compact JSON with keys: account_id, score, top_5_positive_features, top_5_negative_features, confidence." 


## Privacy & Safety Prompts

- "Explain how to implement salted hashing for `account_id` and provide a Python snippet that supports key rotation without rehashing raw PII (i.e., store encrypted raw PII separately)."

- "Suggest a differential privacy mechanism to release aggregate top-up statistics per region while guaranteeing epsilon=1, and provide a simple implementation for counts and means." 


## Ops & Monitoring Prompts

- "Create a set of monitoring queries (SQL) to detect feature drift: compare current 28-day mean and std of `topup_freq_per_month` against a 90-day baseline; fire an alert if KL divergence exceeds threshold." 

- "Generate a concise runbook for scoring-service incidents including steps to: disable new scoring, revert to cached scores, inspect recent feature distributions, and re-run model on past day's data." 


## Stakeholder Communication Prompts

- "Draft a one-page explanation for product managers describing how payment consistency and top-up patterns are used to infer creditworthiness, including limitations, privacy safeguards, and sample use cases." 

- "Prepare a short FAQ for end-users describing what data is used, why, and how they can opt-out or request correction." 


## Developer / Codegen Prompts (Templates)

- Data-cleaning function (pandas):
  - "Write a function `clean_payments(df, salt)` that returns `df_clean` with hashed account ids, parsed dates, and no negatives. Use HMAC-SHA256. Include docstring and minimal tests."

- Feature computation (vectorized):
  - "Implement `compute_features(payments_df, window_months=12)` that returns a DataFrame indexed by `account_id` with the features from the guideline doc. Make it efficient for 10M rows." 


## Prompts for Generating Synthetic Data

- "Generate a synthetic dataset (Parquet) of 100k anonymized accounts with realistic monthly bill payments and top-ups over 3 years. Ensure seasonal harvest spikes for 20% of regions and include random missingness patterns. Provide the generator script in Python." 


## Prompt Engineering Tips
- Always include: data schema, time window, privacy constraints, and desired output format.
- Ask for concise code-only responses when you plan to copy-paste into your editor.
- Request tests and edge-case handling (missing data, duplicates) explicitly.

---
Last updated: 2026-05-30
