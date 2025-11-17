import sqlite3

db = "database.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

# --- USERS ---
cur.execute("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender_id INTEGER,
    user_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    password_hash TEXT NOT NULL,
    user_role TEXT DEFAULT 'normal',
    is_verified INTEGER DEFAULT 0,
    user_birthday DATE,
    registration_date DATETIME,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (gender_id) REFERENCES genders(gender_id)
);
""")

# --- GENDERS ---
cur.execute("""
CREATE TABLE genders (
    gender_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
""")

# --- DEVICES ---
cur.execute("""
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    device_model TEXT,
    os_name TEXT,
    os_version TEXT,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
""")

# --- BIOMETRICS ---
cur.execute("""
CREATE TABLE biometrics (
    biometric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    weight REAL,
    height REAL,
    bmi REAL,
    body_fat_pct REAL,
    blood_type TEXT,
    blood_pressure_avg TEXT,
    heart_rate_avg INTEGER,
    sleep_score INTEGER,
    recorded_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
""")

# --- ACTIVITY TYPES ---
cur.execute("""
CREATE TABLE activity_types (
    activity_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
);
""")

# --- LOCATIONS ---
cur.execute("""
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_province TEXT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
);
""")

# --- ACTIVITIES ---
cur.execute("""
CREATE TABLE activities (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activity_type_id INTEGER,
    location_id INTEGER,
    source_device_id INTEGER,
    start_time DATETIME,
    end_time DATETIME,
    duration_seconds INTEGER,
    distance_km REAL,
    calories_kcal REAL,
    steps INTEGER,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    status TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(activity_type_id) REFERENCES activity_types(activity_type_id),
    FOREIGN KEY(location_id) REFERENCES locations(location_id),
    FOREIGN KEY(source_device_id) REFERENCES devices(device_id)
);
""")

# --- GOALS ---
cur.execute("""
CREATE TABLE goals (
    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activity_type_id INTEGER,
    goal_name TEXT,
    target_value REAL,
    target_unit TEXT,
    progress_value REAL,
    progress_percent REAL,
    start_at DATETIME,
    end_at DATETIME,
    status TEXT,
    created_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(activity_type_id) REFERENCES activity_types(activity_type_id)
);
""")

# --- COMMUNITIES ---
cur.execute("""
CREATE TABLE communities (
    community_id INTEGER PRIMARY KEY AUTOINCREMENT,
    community_name TEXT,
    description TEXT,
    cover_image_url TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
""")

# community membership
cur.execute("""
CREATE TABLE communities_users (
    community_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (community_id, user_id),
    FOREIGN KEY (community_id) REFERENCES communities(community_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
""")

# events
cur.execute("""
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT,
    event_description TEXT,
    event_start_datetime DATETIME,
    event_end_datetime DATETIME,
    event_location_id INTEGER,
    max_participants INTEGER,
    created_at DATETIME,
    FOREIGN KEY(event_location_id) REFERENCES locations(location_id)
);
""")

# event memberships
cur.execute("""
CREATE TABLE communities_events (
    event_id INTEGER,
    community_id INTEGER,
    PRIMARY KEY (event_id, community_id),
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(community_id) REFERENCES communities(community_id)
);
""")

# --- ACHIEVEMENTS ---
cur.execute("""
CREATE TABLE achievements (
    achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_code TEXT,
    achievement_name TEXT,
    mission_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(mission_id) REFERENCES missions(mission_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
""")

# --- MISSION DIFFICULTIES ---
cur.execute("""
CREATE TABLE mission_difficulties (
    mission_difficulty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
""")

# --- MISSIONS ---
cur.execute("""
CREATE TABLE missions (
    mission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_name TEXT,
    description TEXT,
    activity_type_id INTEGER,
    start_at DATETIME,
    end_at DATETIME,
    mission_difficulty_id INTEGER,
    reward_points INTEGER,
    FOREIGN KEY(activity_type_id) REFERENCES activity_types(activity_type_id),
    FOREIGN KEY(mission_difficulty_id) REFERENCES mission_difficulties(mission_difficulty_id)
);
""")

# --- NEWS ---
cur.execute("""
CREATE TABLE news (
    news_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER,
    news_subject TEXT,
    news_description TEXT,
    news_start_datetime DATETIME,
    news_end_datetime DATETIME,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(author_id) REFERENCES users(user_id)
);
""")

# --- NOTIFICATIONS ---
cur.execute("""
CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    device_id INTEGER,
    notification_type TEXT,
    title TEXT,
    body TEXT,
    sent_at DATETIME,
    is_read INTEGER DEFAULT 0,
    read_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(device_id) REFERENCES devices(device_id)
);
""")

conn.commit()
conn.close()

print("database.db created successfully.")
