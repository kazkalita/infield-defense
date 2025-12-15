DROP TABLE IF EXISTS infield_oaa_summary;

CREATE TABLE infield_oaa_summary AS
SELECT
  f.season,
  'team' AS inf_group_type,
  f.fielding_team AS inf_group_id,

  COUNT(*) AS opportunities,
  SUM(f.is_out) AS outs_made,
  SUM(s.p_out) AS expected_outs,
  SUM(f.is_out) - SUM(s.p_out) AS oaa,
  (SUM(f.is_out) - SUM(s.p_out)) * 100.0 / COUNT(*) AS oaa_per_100
FROM bip_clean f
JOIN bip_scored s
  ON f.bip_id = s.bip_id
WHERE f.fielding_team IS NOT NULL
GROUP BY f.season, f.fielding_team;
