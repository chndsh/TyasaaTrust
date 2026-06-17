-- Transaction schema and mock seed data for PostgreSQL

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP FUNCTION IF EXISTS get_transactions_by_merchant(TEXT);
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS behavioral_scores CASCADE;
DROP TABLE IF EXISTS behavioral_features CASCADE;
DROP TABLE IF EXISTS seasonality_calendar CASCADE;
DROP TABLE IF EXISTS airtime_topups CASCADE;
DROP TABLE IF EXISTS utilities_payments CASCADE;

CREATE TABLE IF NOT EXISTS transactions (
	transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	initiating_merchant_id TEXT NOT NULL,
	initiating_merchant_name TEXT NOT NULL,
	receiving_merchant_id TEXT NOT NULL,
	receiving_merchant_name TEXT NOT NULL,
	transaction_amount NUMERIC(12, 2) NOT NULL CHECK (transaction_amount > 0),
	transaction_date DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_initiating_merchant_id
	ON transactions (initiating_merchant_id, transaction_date);

CREATE INDEX IF NOT EXISTS idx_transactions_receiving_merchant_id
	ON transactions (receiving_merchant_id, transaction_date);

CREATE INDEX IF NOT EXISTS idx_transactions_transaction_date
	ON transactions (transaction_date);

CREATE OR REPLACE FUNCTION get_transactions_by_merchant(p_merchant_id TEXT)
RETURNS TABLE (
	merchant_id TEXT,
	merchant_name TEXT,
	collaborating_merchant_id TEXT,
	collaborating_merchant_name TEXT,
	collaborating_merchant TEXT,
	transaction_type TEXT,
	transaction_amount NUMERIC(12, 2),
	transaction_date DATE
)
LANGUAGE sql
STABLE
AS $$
	SELECT
		t.initiating_merchant_id AS merchant_id,
		t.initiating_merchant_name AS merchant_name,
		t.receiving_merchant_id AS collaborating_merchant_id,
		t.receiving_merchant_name AS collaborating_merchant_name,
		format('%s (%s)', t.receiving_merchant_name, t.receiving_merchant_id) AS collaborating_merchant,
		'paid'::TEXT AS transaction_type,
		t.transaction_amount,
		t.transaction_date
	FROM transactions AS t
	WHERE t.initiating_merchant_id = p_merchant_id

	UNION ALL

	SELECT
		t.receiving_merchant_id AS merchant_id,
		t.receiving_merchant_name AS merchant_name,
		t.initiating_merchant_id AS collaborating_merchant_id,
		t.initiating_merchant_name AS collaborating_merchant_name,
		format('%s (%s)', t.initiating_merchant_name, t.initiating_merchant_id) AS collaborating_merchant,
		'received'::TEXT AS transaction_type,
		t.transaction_amount,
		t.transaction_date
	FROM transactions AS t
	WHERE t.receiving_merchant_id = p_merchant_id

	ORDER BY transaction_date, transaction_type, collaborating_merchant_id;
$$;

WITH month_anchors AS (
	SELECT
		month_index,
		(date_trunc('month', CURRENT_DATE) - ((11 - month_index) || ' months')::INTERVAL + INTERVAL '14 days')::DATE AS anchor_date
	FROM generate_series(0, 11) AS month_index
),
utility_config AS (
	SELECT *
	FROM (VALUES
		(1, '9800000004', 'NEA', 1600::NUMERIC, 120::NUMERIC, 5),
		(2, '9800000005', 'KUKL', 1100::NUMERIC, 90::NUMERIC, 12),
		(3, '9800000006', 'Internet', 1800::NUMERIC, 150::NUMERIC, 20)
	) AS t(sort_order, merchant_id, merchant_name, base_amount, monthly_increase, payment_day)
)
INSERT INTO transactions (
	initiating_merchant_id,
	initiating_merchant_name,
	receiving_merchant_id,
	receiving_merchant_name,
	transaction_amount,
	transaction_date
)
SELECT
	'9800000000',
	'Sajilo Kirana',
	u.merchant_id,
	u.merchant_name,
	(u.base_amount + (u.monthly_increase * m.month_index))::NUMERIC(12, 2),
	make_date(
		EXTRACT(YEAR FROM m.anchor_date)::INT,
		EXTRACT(MONTH FROM m.anchor_date)::INT,
		LEAST(
			u.payment_day,
			EXTRACT(DAY FROM (DATE_TRUNC('month', m.anchor_date) + INTERVAL '1 month - 1 day'))::INT
		)
	)
FROM month_anchors AS m
CROSS JOIN utility_config AS u
ORDER BY m.anchor_date, u.sort_order;

WITH month_anchors AS (
	SELECT
		month_index,
		(date_trunc('month', CURRENT_DATE) - ((11 - month_index) || ' months')::INTERVAL + INTERVAL '14 days')::DATE AS anchor_date
	FROM generate_series(0, 11) AS month_index
),
fraud_plan AS (
	SELECT *
	FROM (VALUES
		(1, 25000::NUMERIC, 1),
		(4, 25500::NUMERIC, 2),
		(7, 26000::NUMERIC, 3),
		(10, 26500::NUMERIC, 4)
	) AS t(month_index, amount, plan_order)
),
fraud_ring AS (
	SELECT *
	FROM (VALUES
		(1, '9800000001', 'Himal Wholesale', '9800000002', 'Bhaktapur Supplies'),
		(2, '9800000002', 'Bhaktapur Supplies', '9800000003', 'Thamel Traders'),
		(3, '9800000003', 'Thamel Traders', '9800000001', 'Himal Wholesale')
	) AS t(ring_order, initiating_merchant_id, initiating_merchant_name, receiving_merchant_id, receiving_merchant_name)
)
INSERT INTO transactions (
	initiating_merchant_id,
	initiating_merchant_name,
	receiving_merchant_id,
	receiving_merchant_name,
	transaction_amount,
	transaction_date
)
SELECT
	f.initiating_merchant_id,
	f.initiating_merchant_name,
	f.receiving_merchant_id,
	f.receiving_merchant_name,
	f.amount::NUMERIC(12, 2),
	make_date(
		EXTRACT(YEAR FROM m.anchor_date)::INT,
		EXTRACT(MONTH FROM m.anchor_date)::INT,
		10 + r.ring_order - 1
	)
FROM fraud_plan AS f
JOIN month_anchors AS m
	ON m.month_index = f.month_index
CROSS JOIN fraud_ring AS r
ORDER BY f.plan_order, r.ring_order;

COMMIT;