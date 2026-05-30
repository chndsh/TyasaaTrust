## 2026-05-30
1. Updated `backend/modules/social_graph.py` to validate 10-digit merchant IDs and scale stub scores/signals to 0–1000 integers.
2. Updated `backend/modules/behavioral.py` with merchant ID validation and integer-scaled behavioral signals.
3. Enhanced `backend/modules/psychometric.py` to enforce merchant IDs, output 0–1000 integer scores, store latest scores, and return scaled breakdowns.
4. Refactored `backend/modules/fusion.py` to compute weighted composite scores (50/30/20) with 0–1000 clamping.
5. Hardened `backend/routers/graph.py`, `psych.py`, `ingest.py`, and `scoring.py` with merchant ID validation, integer score schemas, and a GET `/scores/{merchant_id}` endpoint.
6. Rebuilt `frontend/app.py` with premium dark mode styling, 10-digit merchant input, psychometric CTA, and composite score display.
7. Restyled `frontend/pages/3_quiz.py`, enforced merchant ID validation, replaced result breakdown with thank-you completion and redirect.
8. Restyled `frontend/pages/2_graph_explorer.py` and `frontend/pages/4_dashboard.py` with dark mode cards, 10-digit validation, and metric presentation.
9. Updated `README.md` and `PROJECT_DOCUMENTATION.md` to reflect new validation rules, scoring ranges, weighted fusion formula, and UI flow.
