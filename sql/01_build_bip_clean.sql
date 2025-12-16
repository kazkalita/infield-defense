-- Rebuild the cleaned balls-in-play table
-- This table defines the universe of events used in all downstream analysis

DROP TABLE IF EXISTS bip_clean;

CREATE TABLE bip_clean AS

-- Step 1: Pull relevant fields from raw Statcast
-- and construct a unique ID for each ball in play
WITH base AS (
  SELECT
    -- Unique identifier for each ball in play
    CAST(game_pk AS TEXT) || '-' ||
    CAST(at_bat_number AS TEXT) || '-' ||
    CAST(pitch_number AS TEXT) AS bip_id,

    season,
    game_date,
    game_pk,
    at_bat_number,
    pitch_number,

    batter AS batter_id,
    pitcher AS pitcher_id,
    stand AS batter_hand,
    p_throws AS pitcher_hand,

    launch_speed AS exit_velocity,
    launch_angle,
    bb_type,

    -- Statcast spray coordinates
    hc_x AS hit_x,
    hc_y AS hit_y,

    events,

    -- Defensive alignments
    if_fielding_alignment AS if_alignment,
    of_fielding_alignment AS of_alignment,

    outs_when_up,
    inning,
    inning_topbot,

    description
  FROM raw_statcast
),

-- Step 2: Keep only true balls in play
-- This removes walks, strikeouts, HBP, etc.
bip_only AS (
  SELECT *
  FROM base
  WHERE description LIKE 'hit_into_play%'
    AND events IS NOT NULL
    AND hit_x IS NOT NULL
    AND hit_y IS NOT NULL
),

-- Step 3: Label outcomes
-- is_out is the primary response variable
-- hit_value is kept for potential future extensions
labeled AS (
  SELECT
    *,
    CASE
      WHEN events IN (
        'field_out',
        'force_out',
        'grounded_into_double_play',
        'double_play',
        'triple_play',
        'fielders_choice_out',
        'sac_fly',
        'sac_fly_double_play',
        'sac_bunt_double_play',
        'sac_bunt',
        'strikeout_double_play'
      ) THEN 1
      ELSE 0
    END AS is_out,

    -- Simple hit value encoding
    CASE
      WHEN events = 'single' THEN 1
      WHEN events = 'double' THEN 2
      WHEN events = 'triple' THEN 3
      WHEN events = 'home_run' THEN 4
      ELSE 0
    END AS hit_value
  FROM bip_only
)

-- Step 4: Final column selection
-- Home runs are excluded since they are not fieldable
SELECT
  bip_id,
  season,
  game_date,
  game_pk,
  at_bat_number,
  pitch_number,
  batter_id,
  pitcher_id,
  batter_hand,
  pitcher_hand,
  exit_velocity,
  launch_angle,
  bb_type,
  hit_x,
  hit_y,
  events,
  is_out,
  hit_value,
  if_alignment,
  of_alignment,
  outs_when_up,
  inning,
  inning_topbot
FROM labeled
WHERE events != 'home_run';
