Here's the complete logic broken into clear layers.

---

## Backend Logic

### 1. Database Query

```sql
SELECT
    transaction_id,
    merchant_id,
    type,
    amount,
    transaction_date
FROM transactions
WHERE merchant_id = :merchant_id
ORDER BY transaction_date ASC;
```

---

### 2. Python Backend (FastAPI example)

```python
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from collections import defaultdict
from scipy import stats
import numpy as np
import pandas as pd
from datetime import datetime

app = FastAPI()

@app.get("/merchant/{merchant_id}/analysis")
def analyse_merchant(merchant_id: int, db: Session = Depends(get_db)):

    # ── 1. Fetch all transactions for this merchant ──────────────────────
    rows = db.execute(
        text("""
            SELECT transaction_id, type, amount, transaction_date
            FROM transactions
            WHERE merchant_id = :mid
            ORDER BY transaction_date ASC
        """),
        {"mid": merchant_id}
    ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No transactions found for this merchant.")

    df = pd.DataFrame(rows, columns=["transaction_id", "type", "amount", "transaction_date"])
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["year"] = df["transaction_date"].dt.year

    # ── 2. Group by type ─────────────────────────────────────────────────
    result = {}
    grouped = df.groupby("type")

    for tx_type, group in grouped:

        # ── 3. Transactions per year (annualised monthly rate = count / 12) ──
        yearly_counts = (
            group.groupby("year")
                 .size()
                 .reset_index(name="tx_count")
        )
        yearly_counts["tx_per_month"] = yearly_counts["tx_count"] / 12

        counts = yearly_counts["tx_count"].values  # raw yearly counts

        # ── 4. Variance and Coefficient of Variation (CoV) ───────────────
        variance      = float(np.var(counts, ddof=1))         # sample variance
        std_dev        = float(np.std(counts, ddof=1))
        mean_count     = float(np.mean(counts))
        coeff_of_var   = float(std_dev / mean_count) if mean_count != 0 else 0.0
        # CoV interpretation:
        #   < 0.2  → very stable volume
        #   0.2–0.5 → moderate fluctuation
        #   > 0.5  → high volatility

        # ── 5. Slope (Linear Regression over years) ──────────────────────
        years  = yearly_counts["year"].values.astype(float)
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, counts)
        # slope > 0  → transaction volume is growing year-over-year
        # slope < 0  → transaction volume is declining
        # slope ≈ 0  → flat/stable

        trend_direction = (
            "increasing" if slope > 0.5
            else "decreasing" if slope < -0.5
            else "stable"
        )

        result[tx_type] = {
            "total_transactions"    : int(group.shape[0]),
            "years_active"          : int(yearly_counts.shape[0]),
            "yearly_breakdown"      : yearly_counts.to_dict(orient="records"),
            "avg_tx_per_month"      : round(mean_count / 12, 2),
            "variance"              : round(variance, 4),
            "std_deviation"         : round(std_dev, 4),
            "coefficient_of_variation": round(coeff_of_var, 4),
            "slope"                 : round(float(slope), 4),
            "r_squared"             : round(float(r_value ** 2), 4),
            "p_value"               : round(float(p_value), 4),
            "trend"                 : trend_direction,
        }

    return {
        "merchant_id" : merchant_id,
        "analysis"    : result,
    }
```

---

### 3. What Each Metric Means (for your team)

| Metric | Formula | Tells You |
|---|---|---|
| `tx_per_month` | `yearly_count / 12` | Normalised activity rate |
| `variance` | `σ²` (sample) | Raw spread of yearly counts |
| `std_deviation` | `√variance` | Same units as count — easier to read |
| `coeff_of_variation` | `std / mean` | Volatility relative to size; comparable across types |
| `slope` | Linear regression coefficient | Direction and speed of volume change |
| `r_squared` | `r²` from regression | How well the trend line fits (1.0 = perfect trend) |
| `p_value` | From regression | Is the slope statistically significant? (< 0.05 = yes) |

**One critical correction to flag:** CoV and variance are computed on *yearly counts*, not monthly. If you compute them on monthly data instead, the values will be 12× noisier and not comparable to the slope which is yearly. Keep them on the same time unit — yearly is the right call here.

---

### 4. Sample API Response

```json
{
  "merchant_id": 4821,
  "analysis": {
    "debit": {
      "total_transactions": 144,
      "years_active": 3,
      "yearly_breakdown": [
        {"year": 2022, "tx_count": 38, "tx_per_month": 3.17},
        {"year": 2023, "tx_count": 47, "tx_per_month": 3.92},
        {"year": 2024, "tx_count": 59, "tx_per_month": 4.92}
      ],
      "avg_tx_per_month": 4.0,
      "variance": 110.33,
      "std_deviation": 10.5,
      "coefficient_of_variation": 0.22,
      "slope": 10.5,
      "r_squared": 0.9991,
      "p_value": 0.018,
      "trend": "increasing"
    },
    "credit": {
      ...
    }
  }
}
```

---

### 5. Frontend Call (fetch example)

```javascript
async function fetchMerchantAnalysis(merchantId) {
  const res = await fetch(`/merchant/${merchantId}/analysis`);
  if (!res.ok) throw new Error("Merchant not found or no data.");
  const data = await res.json();
  return data.analysis;
}
```

---

## GitHub Copilot Prompt

Paste this directly as a comment block above the function you want Copilot to generate:

```python
# Generate a FastAPI endpoint GET /merchant/{merchant_id}/analysis
# 
# Steps:
# 1. Accept merchant_id as an integer path parameter.
# 2. Query a PostgreSQL table `transactions` with columns:
#    transaction_id (int), merchant_id (int), type (varchar),
#    amount (numeric), date (date), mer_name(varchar).
# 3. Fetch all rows where merchant_id matches. Raise 404 if none found.
# 4. Load results into a pandas DataFrame.
# 5. Group rows by the `type` column.
# 6. For each group:
#    a. Count transactions per year using groupby on year extracted from transaction_date.
#    b. Compute tx_per_month = yearly_count / 12 for each year.
#    c. Compute sample variance (ddof=1) and standard deviation of yearly counts.
#    d. Compute coefficient of variation = std / mean of yearly counts.
#    e. Run scipy.stats.linregress(years, yearly_counts) to get slope, r_value, p_value.
#    f. Set trend = "increasing" if slope > 0.5, "decreasing" if slope < -0.5, else "stable".
# 7. Return a JSON response with merchant_id and per-type analysis dict
#    containing: total_transactions, years_active, yearly_breakdown,
#    avg_tx_per_month, variance, std_deviation, coefficient_of_variation,
#    slope, r_squared, p_value, trend.
# Use SQLAlchemy session dependency injection. Round all floats to 4 decimal places.
```

