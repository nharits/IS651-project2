# create_db.py
import sqlite3

DB_PATH = "garmin_like.db"

DDL = """
-- activity_types
CREATE TABLE activity_types (
  activity_type_id INTEGER PRIMARY KEY,
  type_name TEXT NOT NULL -- e.g. "running","cycling","walking"
);

-- genders
CREATE TABLE genders (
  gender_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL -- "male","female","other","unknown"
);

-- locations
CREATE TABLE locations (
  location_id INTEGER PRIMARY KEY,
  location_province TEXT NOT NULL
);

-- users
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  gender_id INTEGER, -- optional
  user_name TEXT NOT NULL,
  user_phone TEXT,
  user_email TEXT UNIQUE,
  user_status TEXT NOT NULL DEFAULT 'active', -- 'active','unverified','disabled'
  registration_date TEXT NOT NULL, -- ISO datetime
  user_birthday TEXT,
  user_role TEXT DEFAULT 'user', -- 'user','coach','admin'
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  FOREIGN KEY (gender_id) REFERENCES genders(gender_id)
);

-- devices
CREATE TABLE devices (
  device_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  device_model TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- biometrics
CREATE TABLE biometrics (
  biometric_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  recorded_at TEXT NOT NULL, -- when this measurement was taken
  weight_kg REAL,
  height_cm REAL,
  blood_type TEXT,
  bp_systolic INTEGER,
  bp_diastolic INTEGER,
  heart_rate_avg INTEGER,
  sleep_score INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- activity (main usage log)
CREATE TABLE activities (
  activity_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  activity_type_id INTEGER NOT NULL,
  location_id INTEGER,
  device_id INTEGER,
  start_time TEXT NOT NULL,
  end_time TEXT,
  duration_sec INTEGER, -- derived or stored
  distance_km REAL,
  calories_kcal REAL,
  status TEXT DEFAULT 'completed', -- 'completed','in_progress','cancelled'
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id),
  FOREIGN KEY (location_id) REFERENCES locations(location_id),
  FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- missions
CREATE TABLE missions (
  mission_id INTEGER PRIMARY KEY,
  mission_name TEXT NOT NULL,
  activity_type_id INTEGER,
  start_at TEXT, -- optional
  end_at TEXT,
  mission_difficulty_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id),
  FOREIGN KEY (mission_difficulty_id) REFERENCES mission_difficulties(mission_difficulty_id)
);

-- mission_difficulties
CREATE TABLE mission_difficulties (
  mission_difficulty_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL -- 'easy','medium','hard'
);

-- achievements
CREATE TABLE achievements (
  achievement_id INTEGER PRIMARY KEY,
  achievement_code TEXT NOT NULL,
  achievement_name TEXT NOT NULL,
  mission_id INTEGER, -- optional: achieved via mission or self-contained
  user_id INTEGER NOT NULL,
  achieved_at TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(mission_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- goals
CREATE TABLE goals (
  goal_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  activity_type_id INTEGER,
  goal_name TEXT NOT NULL,
  target_value REAL NOT NULL, -- e.g., 100 (km) or 10000 (steps)
  target_unit TEXT NOT NULL,   -- 'km','kcal','steps'
  start_at TEXT,
  end_at TEXT,
  status TEXT DEFAULT 'active', -- 'active','completed','failed'
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id)
);

-- events
CREATE TABLE events (
  event_id INTEGER PRIMARY KEY,
  event_name TEXT NOT NULL,
  event_description TEXT,
  event_start_datetime TEXT,
  event_end_datetime TEXT,
  event_location_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (event_location_id) REFERENCES locations(location_id)
);

-- communities
CREATE TABLE communities (
  community_id INTEGER PRIMARY KEY,
  community_name TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- communities_users (membership)
CREATE TABLE communities_users (
  community_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  joined_at TEXT NOT NULL DEFAULT (datetime('now')),
  role TEXT DEFAULT 'member', -- 'member','moderator','owner'
  PRIMARY KEY (community_id, user_id),
  FOREIGN KEY (community_id) REFERENCES communities(community_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- communities_events (association)
CREATE TABLE communities_events (
  community_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  PRIMARY KEY (community_id, event_id),
  FOREIGN KEY (community_id) REFERENCES communities(community_id),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- notification
CREATE TABLE notification (
  notification_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  device_id INTEGER, -- optional: push to device
  notification_type TEXT NOT NULL, -- 'reminder','system','achievement'
  title TEXT,
  body TEXT,
  sent_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- news
CREATE TABLE news (
  news_id INTEGER PRIMARY KEY,
  news_subject TEXT NOT NULL,
  news_description TEXT,
  news_start_datetime TEXT,
  news_end_datetime TEXT
);
"""

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # execute DDL statements
    cur.executescript(DDL)
    conn.commit()
    conn.close()
    print(f"Created database: {DB_PATH}")

if __name__ == "__main__":
    create_db()
