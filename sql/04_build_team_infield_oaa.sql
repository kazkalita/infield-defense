DROP TABLE IF EXISTS infield_oaa_summary;

CREATE TABLE infield_oaa_summary AS
SELECT
  f.season,
  'team' AS inf_group_type,
  r.home_team AS inf_group_id,

  COUNT(*) AS opportunities,
  SUM(f.is_out) AS outs_made,
  SUM(s.p_out) AS expected_outs,
  SUM(f.is_out) - SUM(s.p_out) AS oaa,
  (SUM(f.is_out) - SUM(s.p_out)) * 100.0 / COUNT(*) AS oaa_per_100
FROM bip_features f
JOIN bip_scored s
  ON f.bip_id = s.bip_id
JOIN raw_statcast r
  ON f.bip_id LIKE r.game_pk || '-' || r.at_bat_number || '-' || r.pitch_number
GROUP BY f.season, r.home_team;
