PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS bip_clean;
CREATE TABLE bip_clean (
  bip_id TEXT PRIMARY KEY,
  season INTEGER NOT NULL,
  game_date TEXT,
  game_pk INTEGER,
  at_bat_number INTEGER,
  pitch_number INTEGER,

  batter_id INTEGER,
  pitcher_id INTEGER,
  batter_hand TEXT,
  pitcher_hand TEXT,

  exit_velocity REAL,
  launch_angle REAL,
  bb_type TEXT,

  hit_x REAL,
  hit_y REAL,

  events TEXT,
  is_out INTEGER NOT NULL,
  hit_value INTEGER NOT NULL,

  if_alignment TEXT,
  of_alignment TEXT,

  outs_when_up INTEGER,
  inning INTEGER,
  inning_topbot TEXT
);

CREATE INDEX IF NOT EXISTS idx_bip_clean_season ON bip_clean(season);
CREATE INDEX IF NOT EXISTS idx_bip_clean_gamepk ON bip_clean(game_pk);
CREATE INDEX IF NOT EXISTS idx_bip_clean_xy ON bip_clean(hit_x, hit_y);
CREATE INDEX IF NOT EXISTS idx_bip_clean_btype ON bip_clean(bb_type);

DROP TABLE IF EXISTS bip_features;
CREATE TABLE bip_features (
  bip_id TEXT PRIMARY KEY,

  season INTEGER NOT NULL,
  batter_hand TEXT,
  bb_type TEXT,

  exit_velocity REAL,
  launch_angle REAL,
  hit_x REAL,
  hit_y REAL,

  zone_id INTEGER,
  ev_bucket INTEGER,
  la_bucket INTEGER,

  is_infield_candidate INTEGER NOT NULL,
  is_out INTEGER NOT NULL,

  FOREIGN KEY (bip_id) REFERENCES bip_clean(bip_id)
);

CREATE INDEX IF NOT EXISTS idx_bip_features_season ON bip_features(season);
CREATE INDEX IF NOT EXISTS idx_bip_features_zone ON bip_features(zone_id);

DROP TABLE IF EXISTS bip_scored;
CREATE TABLE bip_scored (
  bip_id TEXT PRIMARY KEY,
  p_out REAL NOT NULL,
  difficulty_bucket INTEGER NOT NULL,
  model_version TEXT NOT NULL,
  scored_utc TEXT NOT NULL,

  FOREIGN KEY (bip_id) REFERENCES bip_clean(bip_id)
);

CREATE INDEX IF NOT EXISTS idx_bip_scored_bucket ON bip_scored(difficulty_bucket);

DROP TABLE IF EXISTS infield_oaa_summary;
CREATE TABLE infield_oaa_summary (
  season INTEGER NOT NULL,
  inf_group_type TEXT NOT NULL,
  inf_group_id TEXT NOT NULL,

  opportunities INTEGER NOT NULL,
  outs_made INTEGER NOT NULL,
  expected_outs REAL NOT NULL,
  oaa REAL NOT NULL,
  oaa_per_100 REAL NOT NULL,

  PRIMARY KEY (season, inf_group_type, inf_group_id)
);

DROP TABLE IF EXISTS infield_oaa_zone;
CREATE TABLE infield_oaa_zone (
  season INTEGER NOT NULL,
  inf_group_type TEXT NOT NULL,
  inf_group_id TEXT NOT NULL,
  zone_id INTEGER NOT NULL,

  opportunities INTEGER NOT NULL,
  outs_made INTEGER NOT NULL,
  expected_outs REAL NOT NULL,
  oaa REAL NOT NULL,

  PRIMARY KEY (season, inf_group_type, inf_group_id, zone_id)
);
