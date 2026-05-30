# Behavioral Proxies Plan (Expert-Aligned)

This plan follows the expert guidance in docs/task_help.md and the repository guidance in docs/alt_behavioral_todo.md and docs/data_contracts.md. Each item includes a status and what is still missing.

## Plan Status

### 1) Feature extraction layer (core priority)
Status: In progress
- Done: base feature modules and registry exist under `backend/behavioral_proxies/features`
- Done: expert features added (`utility_payment_consistency`, `recharge_variance`, `seasonal_recovery_score`)
- Done: tests cover the new feature columns and seasonality calendar behavior
- Not done:
  - Confirm windowing and as_of_date behavior for all signals
  - Ensure a single, dense row per account with consistent windows across data sources

### 2) Ingestion + staging (utilities, airtime, seasonality)
Status: Started (stubs only)
- Implemented: normalization stubs exist in backend/behavioral_proxies/ingestion
- Not done:
  - DB write logic into PostgreSQL staging tables
  - De-duplication, stricter validation, and UTC normalization rules
  - Router integration to accept raw payloads and call ingestion

### 3) Synthetic data + rule-based labels
Status: Partial
- Done: synthetic feature/training CSV generation exists in `backend/behavioral_proxies/utils/generate_synthetic_data.py`
- Not done:
  - Generate synthetic utilities/topups/seasonality data
  - Apply rule-based labeling logic from docs/task_help.md
  - Store labeled data for training

### 4) XGBoost training + CV
Status: Partial
- Done: `train_xgboost_classifier` returns a trained model
- Done: `split_train_validation` provides a time-aware split helper
- Done: validation metrics are computed (`auc`, `brier`, `precision_at_10p`)
- Done: `save_model` persists model artifacts
- Not done:
  - Add cross-validation helper
  - Add further hyperparameter search and persistent experiment logging

### 5) Explainability (SHAP)
Status: In progress
- Done: `backend/behavioral_proxies/evaluation/explain.py` computes SHAP values and extracts top positive/negative drivers per account
- Done: `backend/behavioral_proxies/utils/generate_explanations.py` loads a saved model and a features CSV to produce JSON explanations
- Not done:
  - Integrate explanations into API response and UI

### 6) Scoring pipeline integration
Status: Partial
- Done: `backend/behavioral_proxies/models/predict.py` has a scoring helper
- Done: the smoke pipeline writes scored output to `data/staged/scored.csv`
- Not done:
  - Load latest model + feature schema
  - Write predicted scores to behavioral_scores table
  - Connect scoring to backend/modules/behavioral.py and router flow

### 7) Demo path (feature → score → explanation)
Status: Not started
- Not done:
  - Expose behavioral score + explanation in API response
  - Add UI element or output for explanation

## Notes on What Has Not Been Done
- Rule-based labeling is still missing; the synthetic CSV generator exists, but it does not yet derive labels from the business rules.
- The feature layer still needs window alignment across sources and a single, dense row per account.
- XGBoost training still lacks cross-validation and experiment logging.
- SHAP explainability is implemented in the pipeline, but it is not yet surfaced in the API or UI.
- The behavioral score is not yet integrated into the API flow or frontend.
