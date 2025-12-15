DROP TABLE IF EXISTS bip_features;

CREATE TABLE bip_features AS
WITH base AS (
  SELECT
    bip_id,
    season,
    batter_hand,
    bb_type,
    exit_velocity,
    launch_angle,
    hit_x,
    hit_y,
    is_out
  FROM bip_clean
),
infield_flag AS (
  SELECT
    *,
    CASE
      WHEN hit_y <= 150 THEN 1
      ELSE 0
    END AS is_infield_candidate
  FROM base
),
zoned AS (
  SELECT
    *,
    CAST(hit_x / 25 AS INTEGER) AS x_bin,
    CAST(hit_y / 25 AS INTEGER) AS y_bin
  FROM infield_flag
)
SELECT
  bip_id,
  season,
  batter_hand,
  bb_type,
  exit_velocity,
  launch_angle,
  hit_x,
  hit_y,

  (y_bin * 10 + x_bin) AS zone_id,

  CAST(exit_velocity / 5 AS INTEGER) AS ev_bucket,
  CAST((launch_angle + 90) / 10 AS INTEGER) AS la_bucket,

  is_infield_candidate,
  is_out
FROM zoned
WHERE is_infield_candidate = 1;
