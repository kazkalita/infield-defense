-- Rebuild the team-level infield OAA summary table
-- This table aggregates performance AFTER opportunity difficulty
-- has already been modeled in bip_scored.

DROP TABLE IF EXISTS infield_oaa_summary;

CREATE TABLE infield_oaa_summary AS
SELECT
  -- Season of play
  f.season,

  -- Grouping metadata
  -- This allows future extension to positions or players
  'team' AS inf_group_type,

  -- Team credited with fielding the ball
  f.fielding_team AS inf_group_id,

  -- Total number of infield balls in play for this team and season
  COUNT(*) AS opportunities,

  -- Actual outs recorded on those balls
  SUM(f.is_out) AS outs_made,

  -- Expected outs based on league-average opportunity model
  SUM(s.p_out) AS expected_outs,

  -- Outs Above Average (OAA)
  -- Positive means the team converted more outs than expected
  SUM(f.is_out) - SUM(s.p_out) AS oaa,

  -- Rate-scaled version of OAA
  -- Normalized to 100 opportunities for easier comparison
  (SUM(f.is_out) - SUM(s.p_out)) * 100.0 / COUNT(*) AS oaa_per_100

FROM bip_clean f

-- Join brings in the expected out probability for each ball in play
JOIN bip_scored s
  ON f.bip_id = s.bip_id

-- Exclude records where the fielding team could not be identified
WHERE f.fielding_team IS NOT NULL

-- Aggregate at the season x team level
GROUP BY
  f.season,
  f.fielding_team;
