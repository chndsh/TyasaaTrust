from __future__ import annotations

UTILITIES_COLUMNS = {
    "account_id",
    "provider",
    "billing_period_start",
    "billing_period_end",
    "billed_amount",
    "payment_date",
    "payment_amount",
    "payment_method",
}

AIRTIME_COLUMNS = {
    "account_id",
    "topup_ts",
    "topup_amount",
    "vendor",
}

SEASONALITY_COLUMNS = {
    "region_id",
    "season_label",
    "season_start_month",
    "season_end_month",
}

PAYMENT_FEATURE_COLUMNS = [
    "account_id_hash",
    "on_time_ratio",
    "utility_payment_consistency",
    "std_interpayment_days",
    "missed_count",
    "payment_amount_cv",
    "days_since_last_payment",
]

TOPUP_FEATURE_COLUMNS = [
    "account_id_hash",
    "topup_freq_per_month",
    "median_topup_amount",
    "large_topup_ratio",
    "burstiness",
    "recharge_variance",
]

SEASONALITY_FEATURE_COLUMNS = [
    "account_id_hash",
    "seasonal_amplitude",
    "harvest_aligned_spike",
    "rolling_monthly_variance",
    "seasonal_recovery_score",
]

FEATURE_COLUMNS = PAYMENT_FEATURE_COLUMNS + TOPUP_FEATURE_COLUMNS + SEASONALITY_FEATURE_COLUMNS
