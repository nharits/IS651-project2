# create_db.py
"""
Run this script to create the SQLite database file `garmin_clone.db`
from the exact DDL provided by the user (no changes).
Usage:
    python create_db.py
"""
import sqlite3
import pathlib

DDL = """
PRAGMA foreign_keys = ON;
-- *** ข้อควรจำ: ในการใช้งาน DBeaver/SQLite ต้องรันคำสั่งนี้เพื่อเปิดใช้งาน Foreign Key Constraints ***
-- PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- ตาราง Lookup/Master (ต้องสร้างก่อน)
-- -----------------------------------------------------------

-- 1. ตาราง genders
CREATE TABLE genders (
    gender_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 2. (delete)ตาราง roles : ลบออกเพราะกำหนด admin ในอีกตารางแล้ว

-- 3. ตาราง mission_difficulties
CREATE TABLE mission_difficulties (
    mission_difficulty_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 4. ตาราง activity_types
CREATE TABLE activity_types (
    activity_type_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 5. ตาราง locations
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    city TEXT,
    location_latitude DECIMAL,
    location_longitude DECIMAL
);

-- -----------------------------------------------------------
-- ตารางหลักและธุรกรรม
-- -----------------------------------------------------------

-- 6. ตาราง users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    gender_id INTEGER NOT NULL REFERENCES genders(gender_id),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE,
    email TEXT NOT NULL UNIQUE,
    phone_number TEXT,
    user_verify BOOLEAN DEFAULT 0, -- 0=FALSE, 1=TRUE
    registration_date TEXT NOT NULL, -- ISO8601 Date
    user_birthday TEXT, -- ISO8601 Date
    is_active BOOLEAN DEFAULT 1 -- 0=FALSE, 1=TRUE
);

-- 7. ตาราง communities
CREATE TABLE communities (
    community_id INTEGER PRIMARY KEY,
    location_id INTEGER REFERENCES locations(location_id),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_public BOOLEAN DEFAULT 1,
    created_at TEXT NOT NULL -- ISO8601 Datetime
);

-- 8. ตาราง communities_users (ตารางเชื่อมโยงสมาชิกในชุมชน)
CREATE TABLE communities_users (
    community_id INTEGER NOT NULL REFERENCES communities(community_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    joined_at TEXT NOT NULL, -- ISO8601 Datetime
    is_admin BOOLEAN DEFAULT 0,
    PRIMARY KEY (community_id, user_id)
);

-- 9. ตาราง events
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY,
    community_id INTEGER NOT NULL REFERENCES communities(community_id),
    location_id INTEGER REFERENCES locations(location_id), -- อนุญาตให้เป็น NULL สำหรับ Virtual Event
    event_name TEXT NOT NULL,
    event_descrip TEXT,
    start_datetime TEXT NOT NULL, -- ISO8601 Datetime
    end_datetime TEXT -- ISO8601 Datetime
);

-- (new). ตาราง event_participants
CREATE TABLE event_participants (
    event_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    location_id INTEGER REFERENCES locations(location_id), -- อนุญาตให้เป็น NULL สำหรับ Virtual Event
    status TEXT NOT NULL,
    checkin_datetime TEXT NOT NULL -- ISO8601 Datetime
);

-- 10. ตาราง activities (บันทึกกิจกรรมออกกำลังกาย)
CREATE TABLE activities (
    activity_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    activity_type_id INTEGER NOT NULL REFERENCES activity_types(activity_type_id),
    location_id INTEGER REFERENCES locations(location_id),
    device_id INTEGER REFERENCES devices(device_id),
    start_datetime TEXT NOT NULL, -- ISO8601 Datetime
    end_datetime TEXT NOT NULL, -- ISO8601 Datetime
    distance_km REAL, -- ใช้ REAL สำหรับทศนิยม
    calories_kcal INTEGER,
    is_verified BOOLEAN DEFAULT 0,
    created_at TEXT NOT NULL, -- ISO8601 Datetime
    updated_at TEXT -- ISO8601 Datetime
);

-- 11. ตาราง goals
CREATE TABLE goals (
    goal_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    activity_type_id INTEGER REFERENCES activity_types(activity_type_id),
    goal_name TEXT NOT NULL,
    target_amount REAL NOT NULL,
    target_metric TEXT NOT NULL,
    start_dt TEXT NOT NULL, -- ISO8601 Date
    end_dt TEXT, -- ISO8601 Date
    status TEXT NOT NULL,
    created_at TEXT NOT NULL -- ISO8601 Datetime
);

-- 12. ตาราง biometrics
CREATE TABLE biometrics (
    biometric_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    weight REAL,
    weight_unit TEXT,
    height REAL,
    height_unit TEXT,
    blood_pressure_avg TEXT,
    heart_rate_avg INTEGER,
    sleep_score INTEGER,
    measured_at TEXT NOT NULL -- ISO8601 Datetime
);

-- 13. ตาราง devices
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    device_model TEXT,
    created_at TEXT NOT NULL -- ISO8601 Datetime
);

-- 14. ตาราง notification
CREATE TABLE notification (
    notification_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    device_id INTEGER REFERENCES devices(device_id),
    notification_type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    created_at TEXT NOT NULL, -- ISO8601 Datetime
    is_read BOOLEAN DEFAULT 0 -- 0=FALSE, 1=TRUE

);

-- 15. ตาราง news
CREATE TABLE news (
    news_id INTEGER PRIMARY KEY,
    news_subject TEXT NOT NULL,
    news_descrip TEXT,
    news_start_datetime TEXT NOT NULL, -- ISO8601 Datetime
    news_end_datetime TEXT, -- ISO8601 Datetime
    is_read BOOLEAN DEFAULT 0, -- 0=FALSE, 1=TRUE
    created_by_user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- 16. ตาราง achievements
CREATE TABLE achievements (
    achievement_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    a_code TEXT NOT NULL UNIQUE,
    a_name TEXT NOT NULL,
    a_descrip TEXT,
    earned_at TEXT NOT NULL -- ISO8601 Datetime
);

-- 17. ตาราง missions
CREATE TABLE missions (
    mission_id INTEGER PRIMARY KEY,
    mission_difficulty_id INTEGER NOT NULL REFERENCES mission_difficulties(mission_difficulty_id),
    activity_type_id INTEGER NOT NULL REFERENCES activity_types(activity_type_id),
    name TEXT NOT NULL,
    description TEXT,
    reward_points INTEGER DEFAULT 0
);
"""

def main(db_path="garmin_clone.db"):
    db_file = pathlib.Path(db_path)
    if db_file.exists():
        print(f"Overwriting existing DB: {db_file.resolve()}")
        db_file.unlink()
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        # Execute DDL as a single script
        cursor.executescript(DDL)
        conn.commit()
        print(f"Database created successfully at: {db_file.resolve()}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
