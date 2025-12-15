DROP TABLE IF EXISTS bip_scored;

CREATE TABLE bip_scored AS
WITH zone_rates AS (
  SELECT
    zone_id,
    COUNT(*) AS n,
    AVG(is_out) AS p_out
  FROM bip_features
  GROUP BY zone_id
)
SELECT
  f.bip_id,
  z.p_out,
  CASE
    WHEN z.p_out >= 0.90 THEN 1
    WHEN z.p_out >= 0.75 THEN 2
    WHEN z.p_out >= 0.50 THEN 3
    WHEN z.p_out >= 0.25 THEN 4
    ELSE 5
  END AS difficulty_bucket,
  'zone_v1' AS model_version,
  datetime('now') AS scored_utc
FROM bip_features f
JOIN zone_rates z
  ON f.zone_id = z.zone_id;
