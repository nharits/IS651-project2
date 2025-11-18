# create_db.py
import sqlite3
DB_PATH = "garmin_like.db"

DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS activity_types (
  activity_type_id INTEGER PRIMARY KEY,
  type_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS genders (
  gender_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
  location_id INTEGER PRIMARY KEY,
  location_province TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  gender_id INTEGER,
  user_name TEXT NOT NULL,
  user_phone TEXT,
  user_email TEXT UNIQUE,
  user_status TEXT NOT NULL DEFAULT 'active',
  registration_date TEXT NOT NULL,
  user_birthday TEXT,
  user_role TEXT DEFAULT 'user',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  FOREIGN KEY (gender_id) REFERENCES genders(gender_id)
);

CREATE TABLE IF NOT EXISTS devices (
  device_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  device_model TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS biometrics (
  biometric_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  recorded_at TEXT NOT NULL,
  weight_kg REAL,
  height_cm REAL,
  blood_type TEXT,
  bp_systolic INTEGER,
  bp_diastolic INTEGER,
  heart_rate_avg INTEGER,
  sleep_score INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS activities (
  activity_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  activity_type_id INTEGER NOT NULL,
  location_id INTEGER,
  device_id INTEGER,
  start_time TEXT NOT NULL,
  end_time TEXT,
  duration_sec INTEGER,
  distance_km REAL,
  calories_kcal REAL,
  status TEXT DEFAULT 'completed',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id),
  FOREIGN KEY (location_id) REFERENCES locations(location_id),
  FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE TABLE IF NOT EXISTS mission_difficulties (
  mission_difficulty_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS missions (
  mission_id INTEGER PRIMARY KEY,
  mission_name TEXT NOT NULL,
  activity_type_id INTEGER,
  start_at TEXT,
  end_at TEXT,
  mission_difficulty_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id),
  FOREIGN KEY (mission_difficulty_id) REFERENCES mission_difficulties(mission_difficulty_id)
);

CREATE TABLE IF NOT EXISTS achievements (
  achievement_id INTEGER PRIMARY KEY,
  achievement_code TEXT NOT NULL,
  achievement_name TEXT NOT NULL,
  mission_id INTEGER,
  user_id INTEGER NOT NULL,
  achieved_at TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(mission_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS goals (
  goal_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  activity_type_id INTEGER,
  goal_name TEXT NOT NULL,
  target_value REAL NOT NULL,
  target_unit TEXT NOT NULL,
  start_at TEXT,
  end_at TEXT,
  status TEXT DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id)
);

CREATE TABLE IF NOT EXISTS events (
  event_id INTEGER PRIMARY KEY,
  event_name TEXT NOT NULL,
  event_description TEXT,
  event_start_datetime TEXT,
  event_end_datetime TEXT,
  event_location_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (event_location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS communities (
  community_id INTEGER PRIMARY KEY,
  community_name TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS communities_users (
  community_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  joined_at TEXT NOT NULL DEFAULT (datetime('now')),
  role TEXT DEFAULT 'member',
  PRIMARY KEY (community_id, user_id),
  FOREIGN KEY (community_id) REFERENCES communities(community_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS communities_events (
  community_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  PRIMARY KEY (community_id, event_id),
  FOREIGN KEY (community_id) REFERENCES communities(community_id),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS notification (
  notification_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  device_id INTEGER,
  notification_type TEXT NOT NULL,
  title TEXT,
  body TEXT,
  sent_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE TABLE IF NOT EXISTS news (
  news_id INTEGER PRIMARY KEY,
  news_subject TEXT NOT NULL,
  news_description TEXT,
  news_start_datetime TEXT,
  news_end_datetime TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_activities_user_time ON activities(user_id, start_time);
CREATE INDEX IF NOT EXISTS idx_activities_type_time ON activities(activity_type_id, start_time);
CREATE INDEX IF NOT EXISTS idx_biometrics_user_time ON biometrics(user_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id);
"""

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(DDL)
    conn.commit()
    conn.close()
    print("Database created at", DB_PATH)

if __name__ == "__main__":
    create_db()
