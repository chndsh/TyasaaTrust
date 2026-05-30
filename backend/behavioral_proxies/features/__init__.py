"""Consolidated feature computations for behavioral proxy signals.

This module centralizes small feature compute functions previously split
across multiple files so callers can import from a single place.
"""

from __future__ import annotations

import math
from typing import Optional

import pandas as pd

from ..utils.schema import (
    TOPUP_FEATURE_COLUMNS,
    PAYMENT_FEATURE_COLUMNS,
    SEASONALITY_FEATURE_COLUMNS,
)


# --- Topup patterns -------------------------------------------------
REQUIRED_TOPUP_COLS = {"account_id_hash", "topup_ts", "topup_amount"}


def _large_topup_ratio(series: pd.Series) -> float:
    series = series.dropna()
    if series.empty:
        return 0.0
    threshold = series.quantile(0.95)
    return float((series > threshold).mean())


def _burstiness(series: pd.Series) -> float:
    series = series.dropna().sort_values()
    if len(series) < 2:
        return 0.0
    diffs = series.diff().dt.total_seconds() / 86400.0
    mean = diffs.mean()
    if mean == 0:
        return 0.0
    return float(diffs.std() / mean)


def _coefficient_of_variation(series: pd.Series) -> float:
    series = series.dropna()
    if series.empty:
        return float("nan")
    mean = series.mean()
    if mean == 0:
        return 0.0
    return float(series.std() / mean)


def compute_topup_patterns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=TOPUP_FEATURE_COLUMNS
        ).set_index("account_id_hash")

    missing = REQUIRED_TOPUP_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing topup columns: {sorted(missing)}")

    data = df.copy()
    data["topup_ts"] = pd.to_datetime(data["topup_ts"], errors="coerce")
    data["month"] = data["topup_ts"].dt.to_period("M")

    monthly_counts = data.groupby(["account_id_hash", "month"]).size()
    topup_freq_per_month = monthly_counts.groupby("account_id_hash").mean()

    median_topup_amount = (
        data.groupby("account_id_hash")["topup_amount"].median()
    )
    large_topup_ratio = data.groupby("account_id_hash")["topup_amount"].apply(
        _large_topup_ratio
    )
    burstiness = data.groupby("account_id_hash")["topup_ts"].apply(_burstiness)
    recharge_variance = data.groupby("account_id_hash")["topup_amount"].apply(
        _coefficient_of_variation
    )

    features = pd.DataFrame(
        {
            "topup_freq_per_month": topup_freq_per_month,
            "median_topup_amount": median_topup_amount,
            "large_topup_ratio": large_topup_ratio,
            "burstiness": burstiness,
            "recharge_variance": recharge_variance,
        }
    )
    features.index.name = "account_id_hash"
    return features


# --- Payment consistency ---------------------------------------------
REQUIRED_PAYMENT_COLS = {
    "account_id_hash",
    "payment_date",
    "billing_period_end",
    "billed_amount",
    "payment_amount",
}


def _std_interpayment_days(series: pd.Series) -> float:
    series = series.dropna().sort_values()
    if len(series) < 2:
        return 0.0
    diffs = series.diff().dt.days
    return float(diffs.std())


def compute_payment_consistency(
    df: pd.DataFrame,
    as_of_date: Optional[str] = None,
    due_days: int = 15,
    window_days: int = 90,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=PAYMENT_FEATURE_COLUMNS
        ).set_index("account_id_hash")

    missing = REQUIRED_PAYMENT_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing payment columns: {sorted(missing)}")

    data = df.copy()
    data["payment_date"] = pd.to_datetime(
        data["payment_date"], errors="coerce"
    )
    data["billing_period_end"] = pd.to_datetime(
        data["billing_period_end"], errors="coerce"
    )
    data["due_date"] = data["billing_period_end"] + pd.to_timedelta(
        due_days, unit="D"
    )
    data["on_time"] = data["payment_date"].notna() & (
        data["payment_date"] <= data["due_date"]
    )
    data["missed"] = data["payment_date"].isna() | (
        data["payment_amount"].fillna(0) < data["billed_amount"].fillna(0)
    )
    data = data.sort_values(["account_id_hash", "payment_date"])

    grouped = data.groupby("account_id_hash")
    on_time_ratio = grouped["on_time"].mean()
    missed_count = grouped["missed"].sum()
    payment_amount_cv = grouped["payment_amount"].apply(
        _coefficient_of_variation
    )
    std_interpayment_days = grouped["payment_date"].apply(
        _std_interpayment_days
    )

    if as_of_date:
        ref_date = pd.to_datetime(as_of_date)
    else:
        ref_date = data["payment_date"].max()
    if pd.isna(ref_date):
        ref_date = pd.Timestamp.utcnow().normalize()

    days_since_last_payment = (
        ref_date - grouped["payment_date"].max()
    ).dt.days

    window_start = ref_date - pd.Timedelta(days=window_days)
    windowed = data[
        data["payment_date"].notna()
        & (data["payment_date"] >= window_start)
        & (data["payment_date"] <= ref_date)
    ].copy()
    windowed["month"] = windowed["payment_date"].dt.to_period("M")
    months_with_payment = (
        windowed.groupby("account_id_hash")["month"].nunique()
    )
    months_in_window = max(1, int(math.ceil(window_days / 30)))
    utility_payment_consistency = months_with_payment.reindex(
        grouped.size().index, fill_value=0
    ) / months_in_window

    features = pd.DataFrame(
        {
            "on_time_ratio": on_time_ratio,
            "utility_payment_consistency": utility_payment_consistency,
            "std_interpayment_days": std_interpayment_days,
            "missed_count": missed_count,
            "payment_amount_cv": payment_amount_cv,
            "days_since_last_payment": days_since_last_payment,
        }
    )
    features.index.name = "account_id_hash"
    return features


# --- Cashflow seasonality -------------------------------------------
REQUIRED_SEASONALITY_COLS = {"account_id_hash", "topup_ts", "topup_amount"}
_SEASON_LABEL_HINTS = ("harvest", "season", "peak")


def _seasonal_recovery_score(series: pd.Series) -> float:
    values = series.dropna().sort_index().to_numpy()
    if len(values) < 2:
        return 1.0

    dips = [
        idx
        for idx in range(1, len(values))
        if values[idx] < values[idx - 1] * 0.7
    ]
    if not dips:
        return 1.0

    recoveries = 0
    for dip_idx in dips:
        if dip_idx + 1 < len(values):
            if values[dip_idx + 1] >= values[dip_idx - 1] * 0.85:
                recoveries += 1

    return recoveries / len(dips)


def _month_in_range(month: int, start_month: int, end_month: int) -> bool:
    if start_month <= end_month:
        return start_month <= month <= end_month
    return month >= start_month or month <= end_month


def _calendar_season_months(seasonality_df: pd.DataFrame) -> set[int]:
    label_series = seasonality_df.get(
        "season_label", pd.Series(dtype=str)
    ).astype(str)
    seasonal_rows = seasonality_df[
        label_series.str.contains(
            "|".join(_SEASON_LABEL_HINTS), case=False, na=False
        )
    ]
    source = seasonal_rows if not seasonal_rows.empty else seasonality_df
    months: set[int] = set()
    for _, row in source.iterrows():
        start_month = int(row["season_start_month"])
        end_month = int(row["season_end_month"])
        months.update(
            month
            for month in range(1, 13)
            if _month_in_range(month, start_month, end_month)
        )
    return months


def _harvest_alignment_score(
    data: pd.DataFrame, seasonality_df: pd.DataFrame | None
) -> pd.Series:
    if seasonality_df is None or seasonality_df.empty:
        return pd.Series(dtype=float)

    calendar_cols = {
        "region_id",
        "season_label",
        "season_start_month",
        "season_end_month",
    }
    missing = calendar_cols - set(seasonality_df.columns)
    if missing:
        raise ValueError(f"Missing seasonality columns: {sorted(missing)}")

    if "region_id" in data.columns:
        merged = data.merge(
            seasonality_df,
            on="region_id",
            how="left",
            suffixes=("", "_season"),
        )
        merged["month"] = merged["topup_ts"].dt.month
        merged["is_harvest_month"] = merged.apply(
            lambda row: _month_in_range(
                int(row["month"]),
                int(row["season_start_month"]),
                int(row["season_end_month"]),
            )
            if pd.notna(row["season_start_month"])
            and pd.notna(row["season_end_month"])
            else False,
            axis=1,
        )
    else:
        harvest_months = _calendar_season_months(seasonality_df)
        if not harvest_months:
            return pd.Series(dtype=float)
        merged = data.copy()
        merged["month"] = merged["topup_ts"].dt.month
        merged["is_harvest_month"] = merged["month"].isin(harvest_months)

    seasonal_amount = (
        merged.loc[merged["is_harvest_month"]]
        .groupby("account_id_hash")["topup_amount"]
        .sum()
    )
    total_amount = merged.groupby("account_id_hash")["topup_amount"].sum()
    aligned = (seasonal_amount / total_amount).fillna(0.0)
    aligned.name = "harvest_aligned_spike"
    return aligned


def compute_cashflow_seasonality(
    topup_df: pd.DataFrame, seasonality_df: pd.DataFrame | None = None
) -> pd.DataFrame:
    if topup_df.empty:
        return pd.DataFrame(columns=SEASONALITY_FEATURE_COLUMNS).set_index(
            "account_id_hash"
        )

    missing = REQUIRED_SEASONALITY_COLS - set(topup_df.columns)
    if missing:
        raise ValueError(f"Missing seasonality columns: {sorted(missing)}")

    data = topup_df.copy()
    data["topup_ts"] = pd.to_datetime(data["topup_ts"], errors="coerce")
    data["month"] = data["topup_ts"].dt.to_period("M")

    monthly_totals = data.groupby(["account_id_hash", "month"])[
        "topup_amount"
    ].sum()
    seasonal_amplitude = monthly_totals.groupby("account_id_hash").apply(
        lambda series: float(series.max() - series.min())
    )
    rolling_monthly_variance = monthly_totals.groupby("account_id_hash").var()
    seasonal_recovery_score = monthly_totals.groupby("account_id_hash").apply(
        _seasonal_recovery_score
    )
    harvest_aligned_spike = _harvest_alignment_score(data, seasonality_df)
    harvest_aligned_spike = harvest_aligned_spike.reindex(
        seasonal_amplitude.index
    )

    features = pd.DataFrame(
        {
            "seasonal_amplitude": seasonal_amplitude,
            "harvest_aligned_spike": harvest_aligned_spike,
            "rolling_monthly_variance": rolling_monthly_variance,
            "seasonal_recovery_score": seasonal_recovery_score,
        }
    )
    features.index.name = "account_id_hash"
    return features


# --- Registry -------------------------------------------------------
def build_feature_set(
    utilities_df: pd.DataFrame,
    topups_df: pd.DataFrame,
    seasonality_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    payments = compute_payment_consistency(utilities_df)
    topups = compute_topup_patterns(topups_df)
    seasonality = compute_cashflow_seasonality(topups_df, seasonality_df)

    features = payments.join(topups, how="outer").join(
        seasonality, how="outer"
    )
    features.index.name = "account_id_hash"
    return features.reset_index()


__all__ = [
    "compute_topup_patterns",
    "compute_payment_consistency",
    "compute_cashflow_seasonality",
    "build_feature_set",
]
