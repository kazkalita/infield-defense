-- Rebuild the table that contains engineered features
-- for every infield ball in play

DROP TABLE IF EXISTS bip_features;

CREATE TABLE bip_features AS

-- Step 1: Select the raw fields we care about from cleaned BIP data
WITH base AS (
  SELECT
    bip_id,          -- Unique identifier for the ball in play
    season,          -- Season (2023–2025)
    batter_hand,     -- Batter handedness (L/R)
    bb_type,         -- Batted-ball type (groundball, line drive, etc.)
    exit_velocity,   -- Exit velocity (mph)
    launch_angle,    -- Launch angle (degrees)
    hit_x,           -- Statcast spray X coordinate
    hit_y,           -- Statcast spray Y coordinate
    is_out           -- 1 if out was recorded, 0 otherwise
  FROM bip_clean
),

-- Step 2: Flag balls that are plausible infield opportunities
-- This is a spatial proxy for "infield"
infield_flag AS (
  SELECT
    *,
    CASE
      WHEN hit_y <= 150 THEN 1
      ELSE 0
    END AS is_infield_candidate
  FROM base
),

-- Step 3: Discretize the field into a grid
-- Each bin is 25x25 Statcast units
zoned AS (
  SELECT
    *,
    CAST(hit_x / 25 AS INTEGER) AS x_bin,
    CAST(hit_y / 25 AS INTEGER) AS y_bin
  FROM infield_flag
)

-- Step 4: Final feature selection and derived fields
SELECT
  bip_id,
  season,
  batter_hand,
  bb_type,
  exit_velocity,
  launch_angle,
  hit_x,
  hit_y,

  -- Unique spatial zone identifier
  -- 10 x-bins per row, stacked by y-bin
  (y_bin * 10 + x_bin) AS zone_id,

  -- Exit velocity bucket (5 mph increments)
  CAST(exit_velocity / 5 AS INTEGER) AS ev_bucket,

  -- Launch angle bucket (10 degree increments, shifted positive)
  CAST((launch_angle + 90) / 10 AS INTEGER) AS la_bucket,

  -- Retain the infield flag for transparency
  is_infield_candidate,

  -- Outcome variable
  is_out

FROM zoned

-- Only keep balls classified as infield candidates
WHERE is_infield_candidate = 1;
