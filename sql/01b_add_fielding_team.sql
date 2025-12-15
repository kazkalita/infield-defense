ALTER TABLE bip_clean ADD COLUMN fielding_team TEXT;

UPDATE bip_clean
SET fielding_team = (
  SELECT
    CASE
      WHEN inning_topbot = 'Top' THEN home_team
      ELSE away_team
    END
  FROM raw_statcast r
  WHERE r.game_pk = bip_clean.game_pk
  LIMIT 1
);
