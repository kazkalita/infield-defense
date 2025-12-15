DROP TABLE IF EXISTS bip_scored;

CREATE TABLE bip_scored AS
WITH zone_rates AS (
  SELECT
    zone_id,
    AVG(is_out) AS p_out
  FROM bip_features
  GROUP BY zone_id
),
scored AS (
  SELECT
    f.bip_id,
    z.p_out
  FROM bip_features f
  JOIN zone_rates z
    ON f.zone_id = z.zone_id
),
ranked AS (
  SELECT
    bip_id,
    p_out,
    NTILE(5) OVER (ORDER BY p_out DESC) AS difficulty_bucket
  FROM scored
)
SELECT
  bip_id,
  p_out,
  difficulty_bucket,
  'zone_v1_percentile' AS model_version,
  datetime('now') AS scored_utc
FROM ranked;
