-- ============================================================
-- Parakh — Supporter subscription / billing (§9.5)
-- Razorpay, custom UPI-first checkout. Webhooks are the source of truth;
-- entitlements mutate only via webhook/reconciliation.
-- ============================================================

DO $$ BEGIN
  CREATE TYPE plan_interval AS ENUM ('monthly','yearly');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE subscription_status AS ENUM
    ('created','pending_auth','active','grace','halted','cancelled','expired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE entitlement_tier AS ENUM ('free','supporter');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS plans (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  razorpay_plan_id TEXT UNIQUE,
  interval         plan_interval NOT NULL,
  amount_inr       INTEGER NOT NULL,         -- paise or rupees — store paise
  active           BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan_id                UUID NOT NULL REFERENCES plans(id),
  razorpay_subscription_id TEXT UNIQUE,
  status                 subscription_status NOT NULL DEFAULT 'created',
  current_period_end     TIMESTAMPTZ,
  cancel_at_period_end   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

CREATE TABLE IF NOT EXISTS invoices (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id    UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
  razorpay_invoice_id TEXT UNIQUE,
  receipt_no         TEXT UNIQUE,            -- PKH-YYYY-NNNNN
  amount_inr         INTEGER NOT NULL,
  gst_amount         INTEGER NOT NULL DEFAULT 0,  -- 18% GST, inclusive display
  status             TEXT NOT NULL DEFAULT 'issued',
  invoice_pdf_url    TEXT,
  period             TEXT,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Idempotent webhook ledger. event_id UNIQUE => at-least-once delivery is safe.
CREATE TABLE IF NOT EXISTS webhook_events (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider     TEXT NOT NULL DEFAULT 'razorpay',
  event_id     TEXT NOT NULL UNIQUE,
  type         TEXT NOT NULL,
  payload      JSONB NOT NULL,
  processed_at TIMESTAMPTZ,
  error        TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_webhook_unprocessed ON webhook_events(processed_at) WHERE processed_at IS NULL;

-- getEntitlement() reads here; gates never call Razorpay at request time.
CREATE TABLE IF NOT EXISTS entitlements (
  user_id     UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  tier        entitlement_tier NOT NULL DEFAULT 'free',
  valid_until TIMESTAMPTZ,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS promo_codes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code            TEXT NOT NULL UNIQUE,
  percent_off     INTEGER NOT NULL,
  max_redemptions INTEGER,
  redemptions     INTEGER NOT NULL DEFAULT 0,
  expires_at      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Launch plans: ₹99/mo, ₹999/yr (stored in paise). razorpay_plan_id set post-provision.
INSERT INTO plans (interval, amount_inr, active) VALUES
  ('monthly', 9900,  TRUE),
  ('yearly',  99900, TRUE)
ON CONFLICT DO NOTHING;
