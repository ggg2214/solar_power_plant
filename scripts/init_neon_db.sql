-- Neon Serverless PostgreSQL Database Schema for E-SolarSpot (햇빛계산소)

-- 1. Users Table (SHA-256 + Salt Encrypted Passwords)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. WebAuthn Passkeys Table (Biometric / Security Keys)
CREATE TABLE IF NOT EXISTS passkeys (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    credential_id TEXT UNIQUE NOT NULL,
    raw_credential TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Rooftop Solar Simulations Table (Persistent History)
CREATE TABLE IF NOT EXISTS simulations (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    address TEXT,
    rooftop_area_m2 NUMERIC,
    capacity_kw NUMERIC,
    annual_kwh NUMERIC,
    annual_revenue_krw NUMERIC,
    co2_reduction_kg NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Account-specific favorite estimates for My Page
-- Each row belongs to exactly one signed-in email. Keep this separate from
-- simulations so the existing scenario history and comparison feature stay unchanged.
CREATE TABLE IF NOT EXISTS favorite_estimates (
    id BIGSERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    rooftop_area_m2 NUMERIC,
    capacity_kw NUMERIC NOT NULL,
    total_cost_krw NUMERIC,
    net_investment_krw NUMERIC,
    annual_revenue_krw NUMERIC,
    payback_years NUMERIC,
    option_signature TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE favorite_estimates
    ADD COLUMN IF NOT EXISTS option_signature TEXT NOT NULL DEFAULT '';

-- Index for fast user lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_passkeys_user ON passkeys(user_email);
CREATE INDEX IF NOT EXISTS idx_favorite_estimates_user_created
    ON favorite_estimates(user_email, created_at DESC);
