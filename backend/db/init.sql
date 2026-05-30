-- Behavioral proxies staging and features (PostgreSQL)

CREATE TABLE IF NOT EXISTS utilities_payments (
	id BIGSERIAL PRIMARY KEY,
	account_id_hash TEXT NOT NULL,
	provider TEXT NOT NULL,
	billing_period_start DATE NOT NULL,
	billing_period_end DATE NOT NULL,
	billed_amount NUMERIC(12, 2) NOT NULL,
	payment_date DATE,
	payment_amount NUMERIC(12, 2),
	payment_method TEXT,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_utilities_account_id_hash
	ON utilities_payments (account_id_hash);

CREATE TABLE IF NOT EXISTS airtime_topups (
	id BIGSERIAL PRIMARY KEY,
	account_id_hash TEXT NOT NULL,
	topup_ts TIMESTAMPTZ NOT NULL,
	topup_amount NUMERIC(12, 2) NOT NULL,
	vendor TEXT,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_airtime_account_id_hash
	ON airtime_topups (account_id_hash);

CREATE TABLE IF NOT EXISTS seasonality_calendar (
	id BIGSERIAL PRIMARY KEY,
	region_id TEXT NOT NULL,
	season_label TEXT NOT NULL,
	season_start_month SMALLINT NOT NULL,
	season_end_month SMALLINT NOT NULL,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS behavioral_features (
	id BIGSERIAL PRIMARY KEY,
	account_id_hash TEXT NOT NULL,
	as_of_date DATE NOT NULL,
	on_time_ratio NUMERIC(6, 4),
	utility_payment_consistency NUMERIC(6, 4),
	std_interpayment_days NUMERIC(10, 4),
	missed_count INTEGER,
	payment_amount_cv NUMERIC(10, 4),
	days_since_last_payment INTEGER,
	topup_freq_per_month NUMERIC(10, 4),
	median_topup_amount NUMERIC(12, 2),
	large_topup_ratio NUMERIC(6, 4),
	burstiness NUMERIC(10, 4),
	recharge_variance NUMERIC(10, 4),
	seasonal_amplitude NUMERIC(10, 4),
	harvest_aligned_spike NUMERIC(10, 4),
	rolling_monthly_variance NUMERIC(10, 4),
	seasonal_recovery_score NUMERIC(10, 4),
	created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behavioral_features_account_id_hash
	ON behavioral_features (account_id_hash, as_of_date);

CREATE TABLE IF NOT EXISTS behavioral_scores (
	id BIGSERIAL PRIMARY KEY,
	account_id_hash TEXT NOT NULL,
	as_of_date DATE NOT NULL,
	score NUMERIC(6, 4) NOT NULL,
	model_version TEXT,
	score_details JSONB,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behavioral_scores_account_id_hash
	ON behavioral_scores (account_id_hash, as_of_date);
