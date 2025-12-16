-- Rebuild the table that assigns an expected out probability
-- to every individual infield ball in play.

DROP TABLE IF EXISTS bip_scored;

CREATE TABLE bip_scored AS

-- Step 1: Compute league-average out rates by spatial zone
WITH zone_rates AS (
  SELECT
    -- Spatial zone identifier from bip_features
    zone_id,

    -- Number of balls hit into this zone
    COUNT(*) AS n,

    -- League-average probability of an out in this zone
    -- is_out is 1 for an out, 0 otherwise
    AVG(is_out) AS p_out
  FROM bip_features
  GROUP BY zone_id
)

-- Step 2: Assign each ball in play its expected out probability
SELECT
  -- Unique identifier for the ball in play
  f.bip_id,

  -- Expected probability of an out based on its zone
  z.p_out,

  -- Difficulty bucket derived from expected out probability
  -- Lower bucket number = easier play
  CASE
    WHEN z.p_out >= 0.90 THEN 1
    WHEN z.p_out >= 0.75 THEN 2
    WHEN z.p_out >= 0.50 THEN 3
    WHEN z.p_out >= 0.25 THEN 4
    ELSE 5
  END AS difficulty_bucket,

  -- Version tag for the opportunity model
  -- Allows future upgrades without breaking downstream logic
  'zone_v1' AS model_version,

  -- Timestamp indicating when scoring was performed
  datetime('now') AS scored_utc

FROM bip_features f

-- Join each ball in play to its zone-level expectation
JOIN zone_rates z
  ON f.zone_id = z.zone_id;
